import os

import lancedb
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import torch
import torch.nn.functional as F
import cv2
from transformers import AutoImageProcessor, TimesformerForVideoClassification

device = "cuda" if torch.cuda.is_available() else "cpu"

#получение доступ к бд
db = lancedb.connect("/data")

#определение модели Timesformer
model_name = "facebook/timesformer-base-finetuned-k400"
processor = AutoImageProcessor.from_pretrained(model_name)
model = TimesformerForVideoClassification.from_pretrained(model_name).to(device)

#определение объекта FastAPI
app = FastAPI()

#функция для загрузки видео
def load_video(video_path, frame_height=244, frame_width=244):
    cap = cv2.VideoCapture(video_path)
    frames = []
    k = 0
    ret, frame = cap.read()
    #идем по кадрам видео
    while ret:
        k += 1
        frame = cv2.resize(frame, (frame_width, frame_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
        ret, frame = cap.read()
    cap.release()
    idxs = np.linspace(0, len(frames) - 1, 16, dtype=int) #выбираем 16 кадров из всего видео
    return list(np.array(frames)[idxs])


# Функция для получения эмбедингов
def make_embedding(file_path, model, processor):
    frames = load_video(file_path)
    inputs = processor(images=frames, return_tensors="pt").to(device)
    outputs = model(**inputs, output_hidden_states=True)

    return outputs.hidden_states[-1].squeeze(0).mean(dim=1)

class VideoRequest(BaseModel):
    id: str
    url: str

@app.post("/")
async def process_video(video_request: VideoRequest):
    is_first = False
    if "emb_table" not in db.table_names():
        is_first = True
    else:
        tbl = db.open_table("emb_table") #открытие таблицы базы данных с векторами
    result = {}
    uuid = video_request.id #id изображения
    url = video_request.url #ссылка на изображения
    try:
        #считывание изображения
        response = requests.get(url)
        if response.status_code == 200:
            file_Path = 'short.mp4'
            with open(file_Path, 'wb') as file:
                file.write(response.content)

            # преобразование изображения в эмбединги
            emb = make_embedding(file_Path, model, processor)
            numpy_emb = emb.cpu().detach().numpy()
            #если изображение первое, создает базу
            if is_first:
                #добавление результата в базу и определение возврата ответа api серверу
                data = [{"vector": numpy_emb, "id": uuid}]
                tbl = db.create_table("emb_table", data)
                tbl.add(data)
                result['answer'] = False
                result['id'] = ""
            else:
                res = tbl.search(numpy_emb).limit(1).metric("cosine").to_pandas()
                vec = torch.tensor(list(res.vector)).squeeze(0).to(device)
                cosine_similarity = F.cosine_similarity(emb, vec, dim=0).item()
                #определение плагиата
                if cosine_similarity < 0.48:
                    # добавление результата в базу и определение возврата ответа api серверу
                    data = [{"vector": numpy_emb, "id": uuid}]
                    tbl.add(data)
                    result['answer'] = False
                    result['id'] = ""
                else:
                    # определение возврата ответа api серверу
                    result['answer'] = True
                    result['id'] = res.id
        else:
            HTTPException(status_code=404, detail="Failed to download image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
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
print(device)
db = lancedb.connect("http://lancedb")
model_name = "facebook/timesformer-base-finetuned-k400"
processor = AutoImageProcessor.from_pretrained(model_name)
model = TimesformerForVideoClassification.from_pretrained(model_name).to(device)

app = FastAPI()

#функция для загрузки видео
def load_video(video_path, frame_height=244, frame_width=244):
    cap = cv2.VideoCapture(video_path)
    frames = []
    k = 0
    ret, frame = cap.read()
    while ret:
        k += 1
        frame = cv2.resize(frame, (frame_width, frame_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
        ret, frame = cap.read()
    cap.release()
    idxs = np.linspace(0, len(frames) - 1, 16, dtype=int)
    return list(np.array(frames)[idxs])


# Функция для получения предсказаний
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
        tbl = db.open_table("emb_table")
    # считывание видео
    result = {}
    uuid = video_request.id
    url = video_request.url
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_Path = 'short.mp4'
            with open(file_Path, 'wb') as file:
                file.write(response.content)
            emb = make_embedding(file_Path, model, processor)
            numpy_emb = emb.cpu().detach().numpy()
            if is_first:
                data = [{"vector": numpy_emb, "id": uuid}]
                tbl = db.create_table("emb_table", data)
                tbl.add(data)
                result['answer'] = False
                result['id'] = ""
            else:
                res = tbl.search(numpy_emb).limit(1).metric("cosine").to_pandas()
                vec = torch.tensor(list(res.vector)).squeeze(0).to(device)
                cosine_similarity = F.cosine_similarity(emb, vec, dim=0).item()
                if cosine_similarity < 0.48:
                    data = [{"vector": numpy_emb, "id": uuid}]
                    tbl.add(data)
                    result['answer'] = False
                    result['id'] = ""
                else:
                    result['answer'] = True
                    result['id'] = res.id
        else:
            HTTPException(status_code=404, detail="Failed to download image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
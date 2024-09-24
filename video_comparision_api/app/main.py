import requests
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import torch
import cv2
from transformers import AutoImageProcessor, TimesformerForVideoClassification
import torch.nn.functional as F

model_name = "facebook/timesformer-base-finetuned-k400"
processor = AutoImageProcessor.from_pretrained(model_name)
model = TimesformerForVideoClassification.from_pretrained(model_name)

app = FastAPI()

#функция для загрузки видео
def load_video(video_path, num_frames=24, frame_height=480, frame_width=480):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while len(frames) < num_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (frame_width, frame_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
    cap.release()
    if len(frames) < num_frames:
        raise ValueError(f"Video is too short. Needed: {num_frames}, Found: {len(frames)}")
    return frames


# Функция для получения предсказаний
def make_embedding(frames, model, processor):
    inputs = processor(images=frames, return_tensors="pt")
    outputs = model(**inputs, output_hidden_states=True)

    return outputs.hidden_states[-1].squeeze(0).mean(dim=1)

class VideoFile(BaseModel):
    url: str

@app.post("/")
async def process_video(video: VideoFile):
    # считывание изображения
    url = input.url
    try:
        response = requests.get(url)
        if response.status_code == 200:
            frames = load_video(response.content)
        else:
            HTTPException(status_code=404, detail="Failed to download image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    emb = make_embedding(frames, model, processor)
    # Отправка вектора на обработку к самому себе
    response = requests.post("http://127.0.0.1:8000/process_vector/", json={"vector": emb})
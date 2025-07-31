from fastapi import FastAPI
from pydantic import BaseModel
from romsi_hate_speech.predictor import Predictor

app = FastAPI(
    title="Romanized Sinhala Hate Speech Detection API",
    description="Detects hate speech in Romanized Sinhala text using a deep learning model.",
    version="1.0.0"
)

predictor = Predictor(model_path="sakunchamikara/romsi-hate-speech")

class TextRequest(BaseModel):
    texts: list[str]

@app.get("/")
async def root():
    return {"message": "Welcome to Romanized Sinhala Hate Speech Detection API!"}

@app.post("/predict")
async def predict(req: TextRequest):
    results = []
    for text in req.texts:
        label, confidence = predictor.predict(text)
        results.append({
            "text": text,
            "label": "hate" if label == 1 else "not_hate",
            "confidence": confidence
        })
    return {"predictions": results}
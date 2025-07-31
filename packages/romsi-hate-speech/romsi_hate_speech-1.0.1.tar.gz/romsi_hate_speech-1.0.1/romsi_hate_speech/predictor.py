import torch
from romsi_hate_speech.model_loader import ModelLoader
from romsi_hate_speech.inference_preprocessor import InferencePreprocessor

class Predictor:
    def __init__(self, model_path="sakunchamikara/romsi-hate-speech"):
        self.model_loader = ModelLoader(model_path)
        self.tokenizer = self.model_loader.get_tokenizer()
        self.model = self.model_loader.get_model()
        self.device = self.model_loader.get_device()
        self.preprocessor = InferencePreprocessor(self.tokenizer, self.device)

    def predict(self, texts):
        inputs = self.preprocessor.preprocess(texts)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            labels = torch.argmax(probs, dim=1)

        results = []
        if isinstance(texts, str):
            texts = [texts]

        for text, label, confidence in zip(
                texts,
                labels.cpu(),
                probs.max(dim=1).values.cpu()
        ):
            label_str = "hate" if label.item() == 1 else "non-hate"
            results.append({
                "text": text,
                "label": label_str,
                "confidence": round(confidence.item(), 4)
            })

        return results

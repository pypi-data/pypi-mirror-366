from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class ModelLoader:
    def __init__(self, model_path):
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def get_tokenizer(self):
        return self.tokenizer

    def get_model(self):
        return self.model

    def get_device(self):
        return self.device

import re

class InferencePreprocessor:
    def __init__(self, tokenizer, device):
        self.tokenizer = tokenizer
        self.device = device

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"@\w+", "", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def preprocess(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        cleaned_texts = [self.clean_text(t) for t in texts]

        return self.tokenizer(
            cleaned_texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)

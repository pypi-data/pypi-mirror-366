import argparse
from romsi_hate_speech import Predictor

def main():
    parser = argparse.ArgumentParser(
        description="Detect Romanized Sinhala hate speech using XLM-RoBERTa"
    )
    parser.add_argument(
        "texts",
        metavar="TEXT",
        type=str,
        nargs="*",
        help="One or more Romanized Sinhala texts to analyze"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a file containing one text per line"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sakunchamikara/romsi-hate-speech",
        help="HuggingFace model name or local path (default: sakunchamikara/romsi-hate-speech)"
    )

    args = parser.parse_args()
    predictor = Predictor(model_path=args.model)

    # Read texts
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            texts = [line.strip() for line in f if line.strip()]
    else:
        texts = args.texts

    if not texts:
        print("No texts provided. Use arguments or --file.")
        return

    results = predictor.predict(texts)
    for r in results:
        print(f'"{r["text"]}" → {r["label"]} (confidence: {r["confidence"]})')

if __name__ == "__main__":
    main()

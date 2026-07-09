import argparse
import json
from pathlib import Path

import librosa
from datasets import load_dataset, Audio

from src import HuggingFaceASR


_ds_cache = {}


def load_cards(cards_path: str) -> list[dict]:
    with open(cards_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_existing_predictions(output_path: str) -> list[dict]:
    output_path = Path(output_path)

    if not output_path.exists():
        return []

    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def materialise_hf_audio(card: dict, row: dict) -> str:
    """
    Saves Hugging Face audio bytes to a local file if HF only gives us
    a relative path. Returns a real local audio path.
    """
    audio = row["audio"]

    audio_path = audio.get("path") or card.get("audio_path")
    audio_bytes = audio.get("bytes")

    # Case 1: HF gives an actual local path that exists
    if audio_path and Path(audio_path).exists():
        return audio_path

    # Case 2: HF gives only a relative filename, but also gives bytes
    if audio_bytes:
        dataset_key = card["source_dataset"].replace("/", "_")
        output_dir = Path("data/raw/hf_audio") / dataset_key
        output_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(audio_path or "").suffix or ".mp3"
        output_path = output_dir / f"{card['id']}{suffix}"

        if not output_path.exists():
            with open(output_path, "wb") as f:
                f.write(audio_bytes)

        return str(output_path)

    raise FileNotFoundError(
        f"Could not materialise audio for {card['id']}. "
        f"audio_path={audio_path}, has_bytes={audio_bytes is not None}"
    )


def resolve_audio(card):
    if card["source_type"] == "local":
        audio_array, sample_rate = librosa.load(
            card["audio_path"],
            sr=16000,
            mono=True,
        )

        return {
            "raw": audio_array,
            "sampling_rate": 16000,
        }

    if card["source_type"] == "huggingface":
        key = (card["source_dataset"], card["split"])

        if key not in _ds_cache:
            ds = load_dataset(card["source_dataset"], split=card["split"])
            ds = ds.cast_column("audio", Audio(decode=False))
            _ds_cache[key] = ds

        row = _ds_cache[key][card["row_index"]]

        audio_path = materialise_hf_audio(card, row)

        audio_array, sample_rate = librosa.load(
            audio_path,
            sr=16000,
            mono=True,
        )

        return {
            "raw": audio_array,
            "sampling_rate": 16000,
        }

    raise ValueError(f"Unknown source_type: {card['source_type']}")

def make_prediction(card: dict, model_name: str, prediction: str) -> dict:
    return {
        "id": card["id"],
        "model_name": model_name,
        "prediction": prediction,
    }


def save_predictions(predictions: list[dict], output_path: str):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--cards", default="data/final/test_cards.json")
    parser.add_argument("--model_id", default="openai/whisper-small")
    parser.add_argument("--model_name", default="whisper-small")
    parser.add_argument("--out", default="results/predictions_whisper_small.json")
    parser.add_argument("--device", default="auto")

    args = parser.parse_args()

    cards = load_cards(args.cards)

    predictions = load_existing_predictions(args.out)
    completed_ids = {pred["id"] for pred in predictions}

    print(f"Loaded {len(cards)} cards")
    print(f"Found {len(completed_ids)} existing predictions. Resuming...")

    model = HuggingFaceASR(
        model_id=args.model_id,
        device=args.device,
    )

    for i, card in enumerate(cards):
        if card["id"] in completed_ids:
            print(f"[{i + 1}/{len(cards)}] Skipping {card['id']} already done")
            continue

        print(f"[{i + 1}/{len(cards)}] Transcribing {card['id']}")

        try:
            audio_input = resolve_audio(card)
            transcript = model.transcribe(audio_input["raw"])

            prediction = make_prediction(
                card=card,
                model_name=args.model_name,
                prediction=transcript,
            )

            predictions.append(prediction)
            completed_ids.add(card["id"])

            # Save after every successful prediction
            save_predictions(predictions, args.out)

        except Exception as e:
            print(f"Error on card {card['id']}: {e}")
            print("Progress saved. Rerun the script to continue later.")
            raise

    save_predictions(predictions, args.out)
    print(f"Wrote {len(predictions)} predictions to {args.out}")


if __name__ == "__main__":
    main()
import json

from pathlib import Path
from datasets import load_dataset, Audio

from src import suggest_categories

DATASET_NAMES = [
    "benjaminogbonna/nigerian_accented_english_dataset",
    "openslr/librispeech_asr",
    "DTU54DL/common-accent"
]

def make_card(row, index, suggestion, dataset):
    return {
        "id": f"nigerian_{index:06d}_{suggestion['category']}",
        "accent_group": "Nigerian English",
        "accent_subgroup": row.get("accent", ""),
        "category_suggestion": suggestion["category"],
        "reference": row["sentence"],
        "audio_path": row["path"],
        "source_dataset": dataset,
        "source_type": "huggingface",
        "matched_terms": suggestion["matched_terms"],
        "review_status": "needs_review",
        "notes": ""
    }

def main():
    all_cards=[]
    for dataset in DATASET_NAMES:
        ds = load_dataset(dataset, split="train")
        ds = ds.cast_column("audio", Audio(decode=False))

        cards=[]

        for i, row in enumerate(ds):
            reference = row["sentence"]
            suggestions = suggest_categories(reference)

            for suggestion in suggestions:
                card = make_card(row, i, suggestion, dataset)
                cards.append(card)

            if len(cards) >= 30:
                break

    output_path = Path("data/interim/candidates_huggingface.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(cards)} candidate cards to {output_path}")

if __name__ == "__main__":
    main()
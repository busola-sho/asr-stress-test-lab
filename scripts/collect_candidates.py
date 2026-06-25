import json

from pathlib import Path
from datasets import load_dataset, Audio

from src import suggest_categories

DATASET_NAMES = {
    "benjaminogbonna/nigerian_accented_english_dataset":"nigerian",
    "openslr/librispeech_asr":"librispeech",
    "DTU54DL/common-accent":"common_accent"
}

def make_card(row, index, suggestion, dataset, transcript):
    tag=DATASET_NAMES[dataset]
    possible_path_names=["file","path","audio_path"]
    path=""
    for name in possible_path_names:
        if name in row:
            path=name
    return {
        "id": f"{tag}_{index:06d}_{suggestion['category']}",
        "accent_group": row.get("accent", ""),
        "accent_subgroup": "",
        "category_suggestion": suggestion["category"],
        "reference": row[transcript],
        "audio_path": row[path] if path else "",
        "source_dataset": dataset,
        "source_type": "huggingface",
        "matched_terms": suggestion["matched_terms"],
        "review_status": "needs_review",
        "notes": ""
    }

def collect_scots_local(folder_path: str, max_cards: int = 100):
    root = Path(folder_path)
    tsv_path = root / "ss-corpus-sco.tsv"
    audio_dir = root / "audios"

    cards = []

    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for i, row in enumerate(reader):
            reference = row["transcription"]
            audio_filename = row["audio_file"]

            if not reference or not audio_filename:
                continue

            audio_path = audio_dir / audio_filename
            suggestions = suggest_categories(reference)

            for suggestion in suggestions:
                cards.append({
                    "id": f"scots_{i:06d}_{suggestion['category']}",
                    "accent_group": "Scottish English",
                    "accent_subgroup": row.get("accents", ""),
                    "category_suggestion": suggestion["category"],
                    "reference": reference,
                    "audio_path": str(audio_path),
                    "source_dataset": "Common Voice Spontaneous Scots",
                    "source_type": "local_folder",
                    "matched_terms": suggestion["matched_terms"],
                    "split": row.get("split", ""),
                    "duration_ms": row.get("duration_ms", ""),
                    "review_status": "needs_review",
                    "notes": ""
                })

            if len(cards) >= max_cards:
                break

    return cards

def main():
    all_cards=[]
    for ds_name, tag in DATASET_NAMES.items():
        split="train.clean.100" if tag=="librispeech" else "train"
        ds = load_dataset(ds_name, split=split)
        ds = ds.cast_column("audio", Audio(decode=False))

        cards=[]

        for i, row in enumerate(ds):
            transcript="text" if tag=="librispeech" else "sentence"
            reference = row[transcript]
            if tag == "librispeech":
                use_named_entities = False
            else:
                use_named_entities = True

            suggestions = suggest_categories(reference, use_named_entities = use_named_entities)

            for suggestion in suggestions:
                card = make_card(row, i, suggestion, ds_name, transcript)
                cards.append(card)

            if len(cards) >= 30:
                all_cards.append(cards)
                break
        if len(all_cards) >= 120:
                break   
        

    output_path = Path("data/interim/candidates_huggingface.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_cards)} candidate cards to {output_path}")

if __name__ == "__main__":
    main()
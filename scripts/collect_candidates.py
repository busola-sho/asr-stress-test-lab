import json
import csv
from pathlib import Path
from datasets import load_dataset, Audio

from src import suggest_categories

HF_DATASET_NAMES = {
    "benjaminogbonna/nigerian_accented_english_dataset":"nigerian",
    "openslr/librispeech_asr":"librispeech",
    "DTU54DL/common-accent":"common_accent"
}

LOCAL_DATASET_NAMES={
    "data/raw/scots":"cv_scots"
}

def make_card(row, index, suggestion, dataset, transcript, source_type):
    if source_type=="huggingface":
        tag=HF_DATASET_NAMES[dataset]
    else:
        tag=LOCAL_DATASET_NAMES[dataset]
        
    possible_path_names=["file","path","audio_path", "audio_file"]
    path=""
    for name in possible_path_names:
        if name in row:
            path=name
    return {
        "id": f"{tag}_{index:06d}_{suggestion['category']}",
        "accent_group": row.get("accent") or row.get("accents") or "",
        "category_suggestion": suggestion["category"],
        "reference": row.get(transcript, ""),
        "audio_path": row[path] if path else "",
        "source_dataset": dataset,
        "source_type": source_type,
        "matched_terms": suggestion["matched_terms"],
        "review_status": "needs_review"
    }

def collect_from_huggingface():
    all_cards=[]
    for ds_name, tag in HF_DATASET_NAMES.items():
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
                card = make_card(row, i, suggestion, ds_name, transcript, "huggingface")
                cards.append(card)

            if len(cards) >= 30:
                all_cards.extend(cards)
                break
        if len(all_cards) >= 120:
                break   
        
    output_path = Path("data/interim/candidates_huggingface.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_cards)} candidate cards to {output_path}")

def collect_from_local_folder(
    folder_path: str,
    metadata_filename: str,
    audio_dirname: str,
    transcript_column: str,
    audio_column: str,
    max_cards: int = 100,
):
    root = Path(folder_path)
    metadata_path = root / metadata_filename
    audio_dir = root / audio_dirname

    cards = []

    with open(metadata_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for i, row in enumerate(reader):
            reference = row.get(transcript_column, "")
            audio_filename = row.get(audio_column, "")

            if not reference or not audio_filename:
                continue

            audio_path = audio_dir / audio_filename
            suggestions = suggest_categories(reference, True)

            for suggestion in suggestions:
                card =make_card(
                    row,
                    i,
                    suggestion,
                    folder_path,
                    transcript_column,
                    "local"
                )
                # card = {
                #     "id": f"{LOCAL_DATASET_NAMES[folder_path]}_{i:06d}_{suggestion['category']}",
                #     "source_type": "local",
                #     "source_dataset": source_dataset,
                #     "accent_group": accent_group,
                #     "category_suggestion": suggestion["category"],
                #     "reference": reference,
                #     "audio_path": str(audio_path),
                #     "matched_terms": suggestion["matched_terms"],
                #     "review_status": "needs_review"
                # }
                cards.append(card)

            if len(cards) >= max_cards:
                break
    output_path = Path(f"data/interim/candidates_local_{LOCAL_DATASET_NAMES[folder_path]}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(cards)} candidate cards to {output_path}")
    return cards

def main():
    collect_from_huggingface()
    collect_from_local_folder("data/raw/scots", "ss-corpus-sco.tsv", "audios", "transcription","audio_file")

if __name__ == "__main__":
    main()
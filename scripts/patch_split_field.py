"""
Quick patch to add missing 'split' and 'row_index' fields
to already-created HuggingFace test cards.

Usage:
    python scripts/patch_split_field.py --cards data/final/test_cards.json
"""

import json
import argparse
from pathlib import Path

HF_DATASET_NAMES = {
    "benjaminogbonna/nigerian_accented_english_dataset": "nigerian",
    "openslr/librispeech_asr": "librispeech",
    "DTU54DL/common-accent": "common_accent",
}

def get_split(dataset_name):
    tag = HF_DATASET_NAMES.get(dataset_name, "")
    return "train.clean.100" if tag == "librispeech" else "train"

def patch_cards(cards_path: str):
    path = Path(cards_path)
    with open(path, "r", encoding="utf-8") as f:
        cards = json.load(f)

    patched = 0
    for card in cards:
        if card.get("source_type") != "huggingface":
            continue

        if "split" not in card:
            card["split"] = get_split(card["source_dataset"])
            patched += 1

        if "row_index" not in card:
            # parse index from id, e.g. "nigerian_000032" -> 32
            try:
                card["row_index"] = int(card["id"].split("_")[-1])
            except ValueError:
                print(f"  Warning: could not parse row_index from id '{card['id']}'")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"Patched {patched} cards in {path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", required=True, help="Path to test_cards.json")
    args = parser.parse_args()
    patch_cards(args.cards)

if __name__ == "__main__":
    main()
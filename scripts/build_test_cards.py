# scripts/build_test_cards.py

import json
from pathlib import Path


INPUT_DIR = Path("data/interim")
OUTPUT_PATH = Path("data/final/test_cards.json")


FIELDS_TO_DROP = {
    "review_status",
    "notes",
}


def load_cards(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalise_card(card: dict) -> dict:
    # Handle category_suggestion -> category
    if "category" not in card and "category_suggestion" in card:
        card["category"] = card["category_suggestion"]

    # Remove old / unwanted fields
    card.pop("category_suggestion", None)

    for field in FIELDS_TO_DROP:
        card.pop(field, None)

    return card


def main():
    all_cards = []

    for path in INPUT_DIR.glob("candidates_*.json"):
        cards = load_cards(path)
        print(f"Loaded {len(cards)} cards from {path}")

        for card in cards:
            all_cards.append(normalise_card(card))

    # Remove duplicate IDs
    seen = set()
    deduped = []

    for card in all_cards:
        card_id = card["id"]

        if card_id in seen:
            continue

        seen.add(card_id)
        deduped.append(card)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(deduped)} final test cards to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
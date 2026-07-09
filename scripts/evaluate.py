import json
from jiwer import wer
from collections import defaultdict

def load_json(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_model_preds(preds_path, refs_path):
    preds = load_json(preds_path)
    refs = load_json(refs_path)

    preds_by_id = {pred["id"]: pred for pred in preds}

    rows = []
    category_rows = []
    accent_rows = []

    for ref in refs:
        if ref["id"] not in preds_by_id:
            continue

        pred = preds_by_id[ref["id"]]

        pred_text = pred["prediction"]
        ref_text = ref["reference"]

        example_wer = wer(ref_text, pred_text)

        row = {
            "id": ref["id"],
            "model_name": pred["model_name"],
            "accent_group": ref["accent_group"],
            "categories": ref["categories"],
            "reference": ref_text,
            "prediction": pred_text,
            "wer": example_wer,
        }

        rows.append(row)

        accent_rows.append({
            "accent_group": ref["accent_group"],
            "wer": example_wer,
        })

        for category in ref["categories"]:
            category_rows.append({
                "category": category,
                "wer": example_wer,
            })

    return rows, accent_rows, category_rows

def average_wer(rows, group_key):
    groups = defaultdict(list)

    for row in rows:
        group_name = row[group_key]
        groups[group_name].append(row["wer"])

    averages = {}

    for group_name, wer_scores in groups.items():
        averages[group_name] = sum(wer_scores) / len(wer_scores)

    return averages

def main():
    rows, accent_rows, category_rows = evaluate_model_preds(
        preds_path="results/predictions_whisper_small.json",
        refs_path="data/final/test_cards.json",
    )

    overall_wer = sum(row["wer"] for row in rows) / len(rows)
    wer_by_accent = average_wer(accent_rows, "accent_group")
    wer_by_category = average_wer(category_rows, "category")

    print("Overall WER:", overall_wer)
    print("WER by accent:", wer_by_accent)
    print("WER by category:", wer_by_category)

if __name__ == "__main__":
    main()
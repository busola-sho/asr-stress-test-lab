import json
from jiwer import wer


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


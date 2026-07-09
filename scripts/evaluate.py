import json
from jiwer import wer
from collections import defaultdict
from pathlib import Path
import argparse
import string

def safe_name(name: str) -> str:
    return name.replace("/", "_").replace("-", "_")

def normalise_text(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(text.split())
    return text

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

        example_wer = wer(normalise_text(ref_text), normalise_text(pred_text))

        row = {
            "id": ref["id"],
            "model_name": pred["model_name"],
            "accent_group": ref["accent_group"],
            "categories": ref["categories"],
            "source_dataset": ref["source_dataset"],
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

def prettify(label: str) -> str:
    return label.replace("_", " ").title()

def find_worst_example(rows, key, value):
    matching = []

    for row in rows:
        if key == "category":
            if value in row["categories"]:
                matching.append(row)
        else:
            if row[key] == value:
                matching.append(row)

    if not matching:
        return None

    return max(matching, key=lambda row: row["wer"])


def write_simple_report(
    rows,
    overall_wer,
    wer_by_accent,
    wer_by_category,
    model_name,
    output_path,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    worst_categories = sorted(
        wer_by_category.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]

    worst_accents = sorted(
        wer_by_accent.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:2]

    lines = []

    lines.append(f"# ASR Diagnostic: {model_name}")
    lines.append("")
    lines.append(f"Overall WER: **{overall_wer:.1%}**")
    lines.append("")

    lines.append("## Likely failure areas")
    lines.append("")

    for category, score in worst_categories:
        lines.append(f"- **{prettify(category)}**: {score:.1%} WER")

    for accent, score in worst_accents:
        lines.append(f"- **{accent} accent**: {score:.1%} WER")

    lines.append("")
    lines.append("## Example failures")
    lines.append("")

    used_example_ids = set()

    for category, score in worst_categories:
        example = find_worst_example(rows, "category", category)

        if not example or example["id"] in used_example_ids:
            continue

        used_example_ids.add(example["id"])

        lines.append(f"### {prettify(category)}")
        lines.append("")
        lines.append(f"Dataset: {example['source_dataset']}")
        lines.append("")
        lines.append(f"Accent: {example['accent_group']}")
        lines.append("")
        lines.append(f"Reference: {example['reference']}")
        lines.append("")
        lines.append(f"Prediction: {example['prediction']}")

    for accent, score in worst_accents:
        example = find_worst_example(rows, "accent_group", accent)

        if not example or example["id"] in used_example_ids:
            continue

        used_example_ids.add(example["id"])

        lines.append(f"### {accent} accent")
        lines.append("")
        lines.append(f"Dataset: {example['source_dataset']}")
        lines.append("")
        lines.append(f"Accent: {example['accent_group']}")
        lines.append("")
        lines.append(f"Reference: {example['reference']}")
        lines.append("")
        lines.append(f"Prediction: {example['prediction']}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote report to {output_path}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--preds", default="results/predictions_whisper_small.json")
    parser.add_argument("--refs", default="data/final/test_cards.json")
    parser.add_argument("--out", default=None)

    args = parser.parse_args()

    rows, accent_rows, category_rows = evaluate_model_preds(
        preds_path=args.preds,
        refs_path=args.refs,
    )

    model_name = rows[0]["model_name"]

    if not rows:
        raise ValueError("No matching predictions found. Check that prediction IDs match test card IDs.")

    overall_wer = sum(row["wer"] for row in rows) / len(rows)
    wer_by_accent = average_wer(accent_rows, "accent_group")
    wer_by_category = average_wer(category_rows, "category")

    print("Overall WER:", overall_wer)
    print("WER by accent:", wer_by_accent)
    print("WER by category:", wer_by_category)

    write_simple_report(
        rows=rows,
        overall_wer=overall_wer,
        wer_by_accent=wer_by_accent,
        wer_by_category=wer_by_category,
        model_name=model_name,
        output_path = args.out or f"reports/diagnostic_{safe_name(model_name)}.md"
    )

if __name__ == "__main__":
    main()
from datasets import load_dataset, Audio

dataset_name = "benjaminogbonna/nigerian_accented_english_dataset"

ds = load_dataset(dataset_name, split="train")
ds = ds.cast_column("audio", Audio(decode=False))  # important

print(ds.column_names)

row = ds[0]
print({
    "path": row["path"],
    "sentence": row["sentence"],
    "accent": row["accent"],
    "locale": row["locale"],
    "segment": row["segment"]
})
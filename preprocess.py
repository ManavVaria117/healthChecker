# preprocess.py
"""
Robust preprocessing for symptom->disease kaggle datasets.
Saves:
 - data/clean_data.csv   (columns: symptoms (pipe-separated), disease)
 - data/symptom_vocab.json (list of known symptoms)
"""

import os
import json
import pandas as pd
import re
from collections import Counter

DATA_DIR = "data"
INPUT_FILES = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
OUT_CLEAN = os.path.join(DATA_DIR, "clean_data.csv")
OUT_VOCAB = os.path.join(DATA_DIR, "symptom_vocab.json")

def normalize_symptom(s):
    if not isinstance(s, str):
        return None
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s\-]", " ", s)         # remove punctuation
    s = re.sub(r"\s+", " ", s)
    s = s.strip()
    # common synonyms cleanups (extend as needed)
    s = s.replace("sore throat", "sore_throat")
    s = s.replace("shortness of breath", "shortness_of_breath")
    s = s.replace("runny nose", "runny_nose")
    s = s.replace("high fever", "fever")
    s = s.replace("feverish", "fever")
    return s

def extract_symptoms_from_row(row):
    # Try some heuristics to find symptom fields
    # 1) If there's a column named 'symptoms' or 'symptom' -> use it
    for key in row.index:
        if key.lower() in ("symptoms", "symptom", "symptom_list", "symptom(s)"):
            val = row[key]
            if pd.isna(val): 
                return []
            # handle a few separators: | , ; / newline
            if isinstance(val, str) and ("|" in val or "," in val or ";" in val or "\n" in val):
                parts = re.split(r"[|,;\n/]+", val)
            else:
                parts = [val]
            return [normalize_symptom(p) for p in parts if normalize_symptom(p)]
    # 2) Otherwise look for many columns that look like symptom columns (e.g., 'itching','skin_rash'...)
    # assume binary 1/0 or yes/no columns for symptom presence
    symptom_candidates = []
    for key in row.index:
        k = key.lower()
        # heuristic: column name looks like a symptom (has space or underscore and not 'disease' and short)
        if k not in ("disease", "diagnosis", "label", "id") and (len(k) < 40 and re.match(r"^[a-z0-9_ ]+$", k)):
            # check value
            val = row[key]
            if (isinstance(val, (int, float)) and val == 1) or (isinstance(val, str) and val.lower() in ("yes","y","true","1")):
                symptom_candidates.append(normalize_symptom(k))
    if symptom_candidates:
        return symptom_candidates
    # 3) fallback: try to combine all text columns and split
    text = []
    for key in row.index:
        v = row[key]
        if isinstance(v, str) and len(v) < 500 and len(v) > 2:
            text.append(v)
    if text:
        combined = " | ".join(text)
        parts = re.split(r"[|,;\n/]+", combined)
        return [normalize_symptom(p) for p in parts if normalize_symptom(p)]
    return []

def find_disease_field(cols):
    for c in cols:
        if c.lower() in ("disease", "diagnosis", "label", "diseases"):
            return c
    # fallback: try 'prognosis' or last column
    for c in cols:
        if c.lower() in ("prognosis", "illness"):
            return c
    return cols[-1]

def main():
    if not INPUT_FILES:
        print("No CSV files found in data/. Put the downloaded dataset CSV(s) into the data/ folder.")
        return

    # try load first CSV that contains likely columns
    df = None
    for f in INPUT_FILES:
        try:
            print("Trying", f)
            temp = pd.read_csv(f)
            # if it's a tiny or empty file, skip
            if temp.shape[0] < 1:
                continue
            df = temp
            print("Loaded", f, "shape:", df.shape)
            break
        except Exception as e:
            print("Could not read", f, ":", e)
            continue

    if df is None:
        print("No readable CSV found in data/")
        return

    disease_col = find_disease_field(list(df.columns))
    print("Using disease field:", disease_col)

    cleaned_rows = []
    vocab_counter = Counter()
    for _, row in df.iterrows():
        symptoms = extract_symptoms_from_row(row)
        disease = row.get(disease_col, None)
        if pd.isna(disease) or disease is None:
            continue
        # normalize disease text
        disease = str(disease).strip()
        if not symptoms:
            # skip rows without identifiable symptoms
            continue
        # make pipe-separated normalized symptom string
        sym_pipe = "|".join(sorted(set(symptoms)))
        cleaned_rows.append({"symptoms": sym_pipe, "disease": disease})
        for s in symptoms:
            vocab_counter[s] += 1

    if not cleaned_rows:
        print("No rows could be cleaned. Please check your dataset format.")
        return

    clean_df = pd.DataFrame(cleaned_rows)
    os.makedirs(DATA_DIR, exist_ok=True)
    clean_df.to_csv(OUT_CLEAN, index=False)
    print("Saved cleaned CSV to", OUT_CLEAN)

    # save vocab (only keep top 1000 symptoms or all if smaller)
    most_common = [s for s,_ in vocab_counter.most_common(2000)]
    with open(OUT_VOCAB, "w") as f:
        json.dump(most_common, f, indent=2)
    print("Saved symptom vocab to", OUT_VOCAB, "vocab size:", len(most_common))

if __name__ == "__main__":
    main()

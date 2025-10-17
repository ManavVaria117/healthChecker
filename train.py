# train.py
"""
Train a Random Forest model to predict disease from symptoms.
Input: data/clean_data.csv  (columns: symptoms, disease)
Outputs:
 - model_rf.joblib    : trained model
 - mlb.joblib         : MultiLabelBinarizer for symptom encoding
 - label_encoder.joblib : LabelEncoder for disease encoding
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, top_k_accuracy_score
import joblib
import os
import json

DATA_PATH = "data/clean_data.csv"
MODEL_PATH = "model_rf.joblib"
MLB_PATH = "mlb.joblib"
LABEL_ENCODER_PATH = "label_encoder.joblib"

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"{DATA_PATH} not found. Run preprocess.py first.")
    df = pd.read_csv(DATA_PATH)
    print("Loaded cleaned data:", df.shape)
    # split symptom string back into list
    df["symptoms_list"] = df["symptoms"].apply(lambda x: [s.strip().lower() for s in x.split("|")])
    return df

def vectorize(df):
    # Encode symptom presence
    mlb = MultiLabelBinarizer()
    X = mlb.fit_transform(df["symptoms_list"])
    # Encode disease labels
    le = LabelEncoder()
    y = le.fit_transform(df["disease"].astype(str))
    print(f"Feature matrix shape: {X.shape}, num_classes: {len(le.classes_)}")
    return X, y, mlb, le

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print("\nClassification report:\n", classification_report(y_test, y_pred, digits=3))
    try:
        probs = model.predict_proba(X_test)
        top3 = top_k_accuracy_score(y_test, probs, k=3, labels=model.classes_)
        print("Top-3 accuracy:", round(top3, 3))
    except Exception:
        pass
    return model

def save_artifacts(model, mlb, le):
    joblib.dump(model, MODEL_PATH)
    joblib.dump(mlb, MLB_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)
    print("\nSaved model to", MODEL_PATH)
    print("Saved symptom encoder to", MLB_PATH)
    print("Saved label encoder to", LABEL_ENCODER_PATH)

def main():
    df = load_data()
    X, y, mlb, le = vectorize(df)
    model = train_model(X, y)
    save_artifacts(model, mlb, le)

    # For curiosity, print sample predictions
    sample = df.sample(3)
    for _, row in sample.iterrows():
        symptoms = row["symptoms_list"]
        x = mlb.transform([symptoms])
        pred = model.predict(x)
        pred_label = le.inverse_transform(pred)[0]
        print(f"\nExample: {symptoms}\n → Predicted: {pred_label}, Actual: {row['disease']}")

if __name__ == "__main__":
    main()

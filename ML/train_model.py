import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

def train_model():
    print("Loading dataset...")
    dataset_path = os.path.join('ML', 'interview_dataset.csv')
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Run generate_dataset.py first.")

    df = pd.read_csv(dataset_path)

    print("Preprocessing data...")
    edu_map = {'Bachelors': 0, 'Masters': 1, 'PhD': 2}
    df['education_level_encoded'] = df['education_level'].map(edu_map)

    feature_cols = [
        'years_of_experience',
        'skills_score',
        'technical_score',
        'communication_rating',
        'previous_performance',
        'education_level_encoded'
    ]
    
    X = df[feature_cols]
    y = df['selection_outcome']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Training set size: {X_train.shape[0]}")
    print(f"Testing set size: {X_test.shape[0]}")

    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=[
        'Low Selection Probability',
        'Moderately Likely to Select',
        'Highly Likely to Select'
    ]))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    os.makedirs('ML', exist_ok=True)
    model_path = os.path.join('ML', 'candidate_selection_model.pkl')
    
    model_data = {
        'model': rf_model,
        'features': feature_cols,
        'education_map': edu_map,
        'target_names': [
            'Low Selection Probability',
            'Moderately Likely to Select',
            'Highly Likely to Select'
        ]
    }
    
    joblib.dump(model_data, model_path)
    print(f"\nModel saved successfully at: {model_path}")

if __name__ == "__main__":
    train_model()

import os
import joblib
import numpy as np

MODEL_PATH = os.path.join("ML", "candidate_selection_model.pkl")

def load_prediction_model():
    if os.path.exists(MODEL_PATH):
        try:
            model_data = joblib.load(MODEL_PATH)
            print("ML Model loaded successfully from disk.")
            return model_data
        except Exception as e:
            print(f"Error loading ML model from pickle: {e}. Using rule-based fallback.")
    else:
        print(f"ML Model not found at {MODEL_PATH}. Using rule-based fallback.")
    return None

model_data = load_prediction_model()

def fallback_predict(experience: float, skills_score: int, technical_score: int, 
                     communication: int, previous: int, education: str):
    edu_score = 5
    if education == 'Masters':
        edu_score = 8
    elif education == 'PhD':
        edu_score = 10
        
    score = (
        experience * 1.0 +
        skills_score * 0.2 +
        technical_score * 0.3 +
        communication * 3.0 +
        previous * 2.0 +
        edu_score
    )
    
    if score < 56:
        outcome = "Low Selection Probability"
        prob = float(np.clip((score / 56) * 45, 10, 49))
    elif score < 74:
        outcome = "Moderately Likely to Select"
        prob = float(np.clip(50 + ((score - 56) / 18) * 35, 50, 84))
    else:
        outcome = "Highly Likely to Select"
        prob = float(np.clip(85 + ((score - 74) / 26) * 14, 85, 99))
        
    return outcome, round(prob / 100.0, 2)

def predict_candidate_selection(experience: float, skills_score: int, technical_score: int, 
                                communication: int, previous: int, education: str):
    global model_data
    if model_data is None:
        model_data = load_prediction_model()
        
    if model_data is not None:
        try:
            model = model_data['model']
            edu_encoded = model_data['education_map'].get(education, 0)
            
            features = np.array([[
                experience,
                skills_score,
                technical_score,
                communication,
                previous,
                edu_encoded
            ]])
            
            pred_class = model.predict(features)[0]
            pred_probs = model.predict_proba(features)[0]
            
            outcome = model_data['target_names'][pred_class]
            prob = float(pred_probs[pred_class])
            
            return outcome, round(prob, 2)
        except Exception as e:
            print(f"Prediction failed with model, using fallback: {e}")
            
    return fallback_predict(experience, skills_score, technical_score, communication, previous, education)

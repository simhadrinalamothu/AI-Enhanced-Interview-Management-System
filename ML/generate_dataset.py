import pandas as pd
import numpy as np
import os

np.random.seed(42)
n_records = 1000

data = {
    'years_of_experience': np.random.randint(0, 15, n_records),
    'skills_score': np.random.randint(30, 100, n_records),
    'technical_score': np.random.randint(40, 100, n_records),
    'communication_rating': np.random.randint(1, 6, n_records),
    'previous_performance': np.random.randint(1, 6, n_records),
    'education_level': np.random.choice(['Bachelors', 'Masters', 'PhD'], size=n_records, p=[0.6, 0.3, 0.1])
}

df = pd.DataFrame(data)

edu_map = {'Bachelors': 5, 'Masters': 8, 'PhD': 10}
edu_scores = df['education_level'].map(edu_map)

total_score = (
    df['years_of_experience'] * 1.0 +
    df['skills_score'] * 0.2 +
    df['technical_score'] * 0.3 +
    df['communication_rating'] * 3.0 +
    df['previous_performance'] * 2.0 +
    edu_scores
)

noise = np.random.normal(0, 4, n_records)
final_score = total_score + noise

def assign_class(score):
    if score < 56:
        return 0
    elif score < 74:
        return 1
    else:
        return 2

df['selection_outcome'] = [assign_class(s) for s in final_score]

os.makedirs('ML', exist_ok=True)
output_path = os.path.join('ML', 'interview_dataset.csv')
df.to_csv(output_path, index=False)
print(f"Dataset generated successfully at: {output_path}")
print(df['selection_outcome'].value_counts())

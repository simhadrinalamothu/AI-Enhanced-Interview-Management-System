# AI-Enhanced Interview Management System

A real-world recruitment management application for scheduling, tracking, and managing candidate interviews. It features machine learning models to predict candidate selection probabilities and generative AI to summarize interview ratings and generate HR evaluation reports.

---

## Key Features

1. **Full-Stack Interview Workflow**:
   - **Landing/Portal Choice**: Clean, beautiful entrance interface.
   - **Candidate Registration & Login**: Candidates can register, view their profiles, and track scheduled interviews and round statuses.
   - **Recruiter/Admin Login**: Recruiters can review global statistics, schedule interviews, and inspect completed evaluations.
   - **Interviewer Portal**: Interviewers can access their assigned scheduled interviews and rate candidates.
   - **Interview Dashboard**: Shows interview counts, statuses, and predicted selection class distribution.

2. **Machine Learning Module (Random Forest Classifier)**:
   - Evaluates a candidate using 6 key features: Years of Experience, Skills Score, Technical Score, Communication Rating, Previous Round Performance, and Education Level.
   - Predicts selection outcomes: *Highly Likely to Select*, *Moderately Likely to Select*, or *Low Selection Probability*.
   - Serialized model (`model.pkl`) integrated into the backend feedback submission workflow.

3. **Generative AI Module (Gemini Integration & Fallback)**:
   - Uses generative Al to produce a formatted HR evaluation report, candidate summaries, core strengths, and improvement areas.
   - Includes a robust, dynamic template-based fallback system that runs out-of-the-box if no API key is set.

---

## Technology Stack

- **Frontend**: HTML5, CSS3 (Glassmorphism & animations), JavaScript (ES6, Fetch API)
- **Backend**: FastAPI (Python), SQLAlchemy ORM
- **Database**: SQLite (local single-file database)
- **Machine Learning**: Scikit-Learn, Pandas, NumPy, Joblib
- **Generative AI**: Google Gemini API via REST requests

---

## Directory Structure

```
├── Frontend/
│   ├── css/
│   │   └── style.css            # Premium glassmorphic styling
│   ├── js/
│   │   ├── api.js               # REST API communications client
│   │   ├── landing.js           # Auth portal logic
│   │   ├── candidate.js         # Candidate dashboard handler
│   │   └── recruiter.js         # Recruiter/Interviewer dashboard handler
│   ├── index.html               # Main login/registration portal
│   ├── candidate.html           # Candidate view
│   └── recruiter.html           # Recruiter/Interviewer view
│
├── Backend/
│   ├── database.py              # SQLite connection config
│   ├── models.py                # Database tables definition
│   ├── schemas.py               # Pydantic serialization models
│   ├── crud.py                  # DB operations
│   ├── ml_predict.py            # Random Forest prediction utility
│   ├── genai_report.py          # Gemini API caller & fallback
│   ├── main.py                  # FastAPI entry point & routers
│   └── test_integration.py      # Automated API integration tests
│
└── ML/
    ├── generate_dataset.py      # Dataset simulator script
    ├── train_model.py           # Classifier training pipeline
    ├── train_model.ipynb        # Jupyter Notebook for LMS submission
    ├── interview_dataset.csv    # Generated synthetic dataset
    └── candidate_selection_model.pkl # Trained Random Forest pickle model
```

---

## Setup & Running Instructions

### 1. Prerequisites
- Python 3.7.0+ (Tested on Python 3.7.0 32-bit)
- Pip package manager

### 2. Install Dependencies
Install Python dependencies. Note that specific versions are targeted to ensure absolute compatibility with older Python 3.7 environments:
```bash
pip install pandas numpy scikit-learn joblib fastapi uvicorn sqlalchemy requests jinja2
pip install "email-validator<2.0"
pip install "urllib3<2"
```

### 3. Generate Data & Train ML Model
Generate the synthetic candidate dataset and train the Random Forest Classifier:
```bash
# Generate the CSV dataset
python ML/generate_dataset.py

# Train and serialize the Random Forest model
python ML/train_model.py
```
This generates the model files inside the `ML/` folder.

### 4. Run the Backend API Server
Start the Uvicorn server:
```bash
python -m uvicorn Backend.main:app --host 127.0.0.1 --port 8000
```
The backend server runs at `http://127.0.0.1:8000`. You can test endpoints interactively by visiting the OpenAPI documentation at `http://127.0.0.1:8000/docs`.

### 5. Access the Frontend Application
Simply open `Frontend/index.html` in your web browser. You can drag and drop the file into Google Chrome or double-click to launch.

*(Optional)* If you have a Gemini API Key, set it in your environment:
- On Windows: `set GEMINI_API_KEY=your_api_key_here`
- On Linux/macOS: `export GEMINI_API_KEY=your_api_key_here`
If not set, the system will use its robust local fallback report generator.

---

## Running Integration Tests
To programmatically verify all backend API modules (Auth, schedule, feedback, ML, and stats), execute:
```bash
python Backend/test_integration.py
```
If successfully running, all 7 tests will output `=== INTEGRATION TESTS PASSED SUCCESSFULLY! ===`.

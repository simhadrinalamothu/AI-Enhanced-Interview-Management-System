import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def run_integration_tests():
    print("=== STARTING INTEGRATION TESTS ===")
    
    try:
        res = requests.get(f"{BASE_URL}/")
        print(f"Server ping: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"Error connecting to FastAPI server: {e}")
        print("Please ensure the FastAPI server is running on http://127.0.0.1:8000")
        return False
        
    session = requests.Session()
    
    print("\n1. Registering Users...")
    
    cand_reg = {
        "user_in": {
            "username": "alice_candidate",
            "email": "alice@gmail.com",
            "password": "candidate_pass",
            "role": "candidate"
        },
        "profile_in": {
            "full_name": "Alice Green",
            "skills": "Python, Sql, FastAPI",
            "years_of_experience": 4.5,
            "education_level": "Masters"
        }
    }
    
    rec_reg = {
        "user_in": {
            "username": "bob_recruiter",
            "email": "bob@company.com",
            "password": "recruiter_pass",
            "role": "recruiter"
        }
    }
    
    int_reg = {
        "user_in": {
            "username": "Simmu Simmu",
            "email": "simmu@company.com",
            "password": "Simmu@2002",
            "role": "interviewer"
        }
    }
    
    def register_user(payload):
        res = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        if res.status_code == 200:
            print(f"Registered user: {payload['user_in']['username']} successfully")
            return res.json()
        elif res.status_code == 400:
            print(f"User {payload['user_in']['username']} already exists, logging in instead...")
            login_payload = {
                "username": payload['user_in']['username'],
                "password": payload['user_in']['password']
            }
            login_res = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
            if login_res.status_code == 200:
                print(f"Logged in user {payload['user_in']['username']}")
                return login_res.json()
            else:
                print(f"Login failed: {login_res.text}")
        else:
            print(f"Registration failed: {res.text}")
        return None

    cand_data = register_user(cand_reg)
    rec_data = register_user(rec_reg)
    int_data = register_user(int_reg)
    
    if not (cand_data and rec_data and int_data):
        print("User registration/login setup failed.")
        return False
        
    candidate_id = cand_data["id"]
    recruiter_id = rec_data["id"]
    interviewer_id = int_data["id"]
    
    print("\n2. Querying Directories...")
    candidates = requests.get(f"{BASE_URL}/api/users/candidates").json()
    interviewers = requests.get(f"{BASE_URL}/api/users/interviewers").json()
    print(f"Found {len(candidates)} candidates in system.")
    print(f"Found {len(interviewers)} interviewers in system.")
    
    print("\n3. Scheduling Interview round...")
    interview_payload = {
        "candidate_id": candidate_id,
        "recruiter_id": recruiter_id,
        "interviewer_id": interviewer_id,
        "position": "Python Software Engineer",
        "scheduled_time": "2026-06-25T14:30:00"
    }
    int_res = requests.post(f"{BASE_URL}/api/interviews", json=interview_payload)
    if int_res.status_code == 200:
        interview_data = int_res.json()
        interview_id = interview_data["id"]
        print(f"Interview scheduled successfully! ID: {interview_id}, Status: {interview_data['status']}")
    else:
        print(f"Failed to schedule interview: {int_res.text}")
        return False
        
    print("\n4. Checking Candidate portal interviews...")
    cand_ints = requests.get(f"{BASE_URL}/api/interviews/user/{candidate_id}?role=candidate").json()
    print(f"Alice has {len(cand_ints)} scheduled interviews. First interview position: {cand_ints[0]['position']}")
    
    print("\n5. Submitting Feedback (Evaluating Candidate)...")
    feedback_payload = {
        "interview_id": interview_id,
        "technical_score": 88,
        "skills_score": 92,
        "communication_rating": 4,
        "previous_performance": 5,
        "comments": "Alice performed exceptionally well in programming rounds, solved graph question quickly. Communication was clear."
    }
    
    print("Submitting feedback and waiting for ML + GenAI pipelines...")
    feed_res = requests.post(f"{BASE_URL}/api/feedback", json=feedback_payload)
    if feed_res.status_code == 200:
        feedback_data = feed_res.json()
        print("\n--- ML Prediction Results ---")
        print(f"Predicted Outcome: {feedback_data['predicted_outcome']}")
        print(f"Selection Probability: {feedback_data['predicted_probability'] * 100}%")
        
        print("\n--- GenAI Summary Report ---")
        print(f"Summary: {feedback_data['ai_feedback_summary']}")
        print(f"Strengths:\n{feedback_data['ai_strengths']}")
        print(f"Improvements:\n{feedback_data['ai_improvements']}")
        print(f"Full Report length: {len(feedback_data['ai_report'])} characters")
    else:
        print(f"Feedback submission failed: {feed_res.text}")
        return False
        
    print("\n6. Checking updated Interview round status...")
    int_detail = requests.get(f"{BASE_URL}/api/interviews/{interview_id}/detail").json()
    print(f"Interview ID: {interview_id} updated status: {int_detail['status']}")
    
    print("\n7. Fetching Recruiter Dashboard Stats...")
    stats = requests.get(f"{BASE_URL}/api/dashboard/stats").json()
    print("Dashboard Stats:")
    print(json.dumps(stats, indent=2))
    
    print("\n=== INTEGRATION TESTS PASSED SUCCESSFULLY! ===")
    return True

if __name__ == "__main__":
    run_integration_tests()

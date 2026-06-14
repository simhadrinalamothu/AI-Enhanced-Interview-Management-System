import os
import requests
import json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def generate_local_mock_report(candidate_name: str, position: str, skills: str, 
                               experience: float, tech_score: int, comm_rating: int, 
                               prev_performance: int, comments: str, outcome: str):
    comm_labels = {1: "poor", 2: "below average", 3: "satisfactory", 4: "strong", 5: "exceptional"}
    perf_labels = {1: "poor", 2: "unsatisfactory", 3: "average", 4: "good", 5: "outstanding"}
    
    comm_desc = comm_labels.get(comm_rating, "satisfactory")
    perf_desc = perf_labels.get(prev_performance, "average")
    
    if outcome == "Highly Likely to Select":
        summary = f"The candidate, {candidate_name}, demonstrated outstanding capabilities throughout the evaluation for the {position} role. With {experience} years of experience and a high technical score of {tech_score}%, they showed a deep grasp of core concepts. Communication skills were {comm_desc}, facilitating a highly collaborative and structured interview flow."
        strengths = f"1. Exceptional technical competence ({tech_score}% assessment score).\n2. {experience} years of hands-on experience in key technologies.\n3. Strong alignment on communication and team coordination.\n4. Excellent previous round rating of {perf_desc}."
        improvements = "1. Can explore higher-level architecture leadership roles.\n2. Minor polishing on specific advanced niche methodologies mentioned during discussion."
        observations = f"Overall, {candidate_name} is an excellent fit for the role. Their experience and technical scores suggest they will immediately add value to the engineering team. Recommend proceeding to immediate offer stage."
    
    elif outcome == "Moderately Likely to Select":
        summary = f"The candidate, {candidate_name}, presented a solid profile during the {position} interview. They have {experience} years of experience and achieved a reasonable {tech_score}% technical assessment score. Their communication rating is {comm_desc}, indicating they can collaborate effectively within the team."
        strengths = f"1. Practical hands-on experience of {experience} years.\n2. Satisfactory technical assessment performance of {tech_score}%.\n3. Good work ethic and willingness to learn."
        improvements = f"1. Technical depth could be enhanced, particularly in advanced problem solving.\n2. Communication rating ({comm_rating}/5) can be improved with clearer articulation of concepts.\n3. Previous round consistency was {perf_desc}."
        observations = f"{candidate_name} exhibits good potential but would benefit from brief mentorship in advanced areas. They are a viable candidate for the team, provided they match cultural criteria and show improvement in technical depth."
        
    else:
        summary = f"The interview for {candidate_name} for the position of {position} concluded with some gaps in key evaluation areas. The technical assessment score of {tech_score}% and communication skills described as {comm_desc} suggest that the candidate does not fully meet the requirements for the role at this stage."
        strengths = f"1. Possesses basic fundamentals in {skills if skills else 'relevant fields'}.\n2. Shows enthusiasm for the {position} opportunity."
        improvements = f"1. Significant improvement needed in technical domains (current score: {tech_score}%).\n2. Communication rating ({comm_rating}/5) is below expectations for active team settings.\n3. Experience level ({experience} years) is currently insufficient for the role's responsibilities."
        observations = f"At this stage, the candidate's scores and feedback comments ('{comments}') indicate a mismatch with the core requirements. Suggest looking for other roles or re-applying in 6 months after upskilling."

    return {
        "summary": summary,
        "strengths": strengths,
        "improvements": improvements,
        "report": f"INTERVIEW EVALUATION REPORT\nCandidate: {candidate_name}\nPosition: {position}\nStatus: {outcome}\n\nSUMMARY\n{summary}\n\nKEY STRENGTHS\n{strengths}\n\nAREAS FOR IMPROVEMENT\n{improvements}\n\nFINAL OBSERVATIONS\n{observations}"
    }

def generate_interview_evaluation_report(candidate_name: str, position: str, skills: str, 
                                         experience: float, tech_score: int, comm_rating: int, 
                                         prev_performance: int, comments: str, outcome: str):
    prompt = f"""
    You are an expert HR recruiter and senior engineering manager.
    Generate an interview evaluation report for a candidate with the following details:
    - Candidate Name: {candidate_name}
    - Position: {position}
    - Skills: {skills}
    - Years of Experience: {experience}
    - Technical Score: {tech_score}/100
    - Communication Rating: {comm_rating}/5
    - Previous Round Performance: {prev_performance}/5
    - Interviewer Comments: {comments}
    - Selection Outcome Prediction: {outcome}
    
    Format the output as a strict JSON object with four keys:
    1. "summary" (A concise paragraph summarizing the candidate's interview performance and background)
    2. "strengths" (A bulleted list or paragraph of the candidate's major strengths)
    3. "improvements" (A bulleted list or paragraph of areas of improvement)
    4. "report" (A formatted textual final observations summary report suitable for HR files)
    
    Ensure the JSON matches this structure and is valid JSON without code blocks or extra text.
    """
    
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY is not set. Generating report using local engine.")
        return generate_local_mock_report(candidate_name, position, skills, experience, tech_score, comm_rating, prev_performance, comments, outcome)
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            parsed_report = json.loads(raw_text.strip())
            required_keys = ["summary", "strengths", "improvements", "report"]
            if all(k in parsed_report for k in required_keys):
                return parsed_report
            else:
                print("Gemini response missing keys, falling back to local generation.")
        else:
            print(f"Gemini API returned status code {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Failed to generate feedback with Gemini: {e}")
        
    return generate_local_mock_report(candidate_name, position, skills, experience, tech_score, comm_rating, prev_performance, comments, outcome)

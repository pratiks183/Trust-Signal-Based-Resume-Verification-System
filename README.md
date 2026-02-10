# Resume Verification Trust Signal API

## Overview
This is a production-quality prototype REST API designed to evaluate the **public online existence confidence** of companies listed in resumes. 
It uses **Google Gemini** as a semantic search discovery tool to find public signals (Official Website, LinkedIn Presence) and applies a deterministic rule-based scoring system to assign a trust verdict (High, Medium, Low).

## ⚠️ Important Disclaimer
- **NOT A BACKGROUND CHECK**: This system does NOT verify employment history, specific roles, or candidate identity.
- **NO LEGITIMACY CLAIMS**: A "Low" score does not mean a company is fake; it only means insufficient public digital footprint was found by this specific crawler.
- **NO ML DECISIONS**: The scoring is 100% rule-based and explainable. AI is used ONLY to fetch search results (urls/snippers).

## 🔑 Setup & API Key
**CRITICAL**: You need a Google Gemini API Key.

1.  Open `project/search_client.py`.
2.  Find the line: `GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")`
3.  Replace `"YOUR_API_KEY_HERE"` with your actual key, OR better yet, set it in your environment variables.

## Project Structure
- `main.py`: FastAPI entry point.
- `verification_service.py`: Core logic orchestration.
- `search_client.py`: Gemini API interface (Search Abstraction).
- `signals.py`: Logic to extract finding signals from raw search text.
- `scoring.py`: Deterministic scoring rules.

## Scoring Logic
| Signal | Score Addition |
| :--- | :--- |
| Official Website Found | +0.4 |
| LinkedIn Page Found | +0.3 |
| Multiple Independent Sources | +0.3 |

**Verdict**:
- `>= 0.7`: **High** Confidence
- `0.4 - 0.7`: **Medium** Confidence
- `< 0.4`: **Low** Confidence

## Running the API
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   python main.py
   ```
3. POST to `http://127.0.0.1:8000/verify` with:
   ```json
   {
     "internships": [
       { "company": "Amazon", "role": "Machine Learning Intern" }
     ]
   }
   ```

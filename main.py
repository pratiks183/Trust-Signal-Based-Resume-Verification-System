from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import InputPayload, APIResponse
from verification_service import VerificationService
from google.api_core import exceptions
import uvicorn
import os

app = FastAPI(title="Resume Trust Signal API", version="1.0.0")

script_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(script_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, 'index.html'))

service = VerificationService()

@app.post("/verify", response_model=APIResponse)
async def verify_resume(payload: InputPayload):
    try:
        results = service.verify_internships(payload.internships)
        return APIResponse(verification_results=results)
    except exceptions.ResourceExhausted:
        print("Error: Gemini API Quota Exceeded")
        raise HTTPException(
            status_code=429, 
            detail="Daily API quota exceeded. Please try again later."
        )
    except Exception as e:

        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

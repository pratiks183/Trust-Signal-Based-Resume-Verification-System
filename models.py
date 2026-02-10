from typing import List, Dict
from pydantic import BaseModel, Field

class Internship(BaseModel):
    company: str = Field(..., description="Name of the company")
    role: str = Field(..., description="Role title")

class InputPayload(BaseModel):
    internships: List[Internship]

class VerificationResult(BaseModel):
    website_found: bool
    linkedin_found: bool
    multiple_sources_found: bool
    role_match: bool
    trust_score: float
    verdict: str
    role_reason: str = "Role verified via public digital footprint"
    maturity_level: str = "Unknown"

class APIResponse(BaseModel):
    verification_results: Dict[str, VerificationResult]

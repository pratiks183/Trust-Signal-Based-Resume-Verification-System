from typing import Dict
from models import Internship, VerificationResult
from search_client import GeminiSearchClient
from signals import SignalExtractor
from scoring import calculate_score, determine_verdict

class VerificationService:
    def __init__(self):
        self.search_client = GeminiSearchClient()
        self.signal_extractor = SignalExtractor()
        
        self.query_templates = [
            "{company} official website linkedin",
            "{company} {role} internship",
            "{role} at {company} linkedin"
        ]

    def verify_internships(self, internships: list[Internship]) -> Dict[str, VerificationResult]:
        results = {}
        
        for item in internships:
            company = item.company
            role = item.role
            key = f"{company} - {role}"
            all_search_results = []
            for template in self.query_templates:
                query = template.format(company=company, role=role)
                search_results = self.search_client.search(query)
                all_search_results.extend(search_results)
            
            signals = self.signal_extractor.extract_signals(company, role, all_search_results)
            
            score = calculate_score(signals)
            verdict = determine_verdict(score)
            
            reason = signals.get("role_reason", "Role verified via public digital footprint")

            results[key] = VerificationResult(
                website_found=signals.get("website_found", False),
                linkedin_found=signals.get("linkedin_found", False),
                multiple_sources_found=signals.get("multiple_sources_found", False),
                role_match=signals.get("role_match", False),
                trust_score=round(score, 2),
                verdict=verdict,
                role_reason=reason,
                maturity_level=signals.get("maturity_level", "Unknown")
            )
            
        return results

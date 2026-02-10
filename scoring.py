from typing import Dict, Any

def calculate_score(signals: Dict[str, Any]) -> float:
    """
    Calculates trust score based on rule-based signals.
    
    Rules:
    - Official Website: +0.3
    - LinkedIn: +0.2
    - Multiple Sources: +0.2
    - Role Match: +0.3
    
    Safety Rule:
    - If Role Match is FALSE, max score = 0.55 (Medium/Low)
    """
    maturity = signals.get("maturity_level", "Unknown")
    
    # 1. Base Signal Score (Weighted)
    # Total possible: 1.0
    # Website (0.25) + LinkedIn (0.20) + Multi-source (0.25) + Role (0.30)
    
    base_score = 0.0
    if signals.get("website_found"):
        base_score += 0.25
    if signals.get("linkedin_found"):
        base_score += 0.20
    if signals.get("multiple_sources_found"):
        base_score += 0.25
    if signals.get("role_match"):
        base_score += 0.30
        
    # 2. Maturity / Footprint Cap
    # - Global: 1.0
    # - Established: 0.90
    # - SME: 0.85
    # - Unknown: 0.60
    
    caps = {
        "Global": 1.0,
        "Established": 0.90,
        "SME": 0.85,
        "Unknown": 0.60
    }
    maturity_cap = caps.get(maturity, 0.60)
    
    final_score = min(base_score, maturity_cap)

    # 3. Role Mismatch Penalty
    # If role is NOT matched, score should be significantly reduced.
    # Cap at 0.55 (Low/Medium boundary) regardless of company size.
    if not signals.get("role_match"):
        final_score = min(final_score, 0.55)
    
    return round(final_score, 2)

def determine_verdict(score: float) -> str:
    """
    Maps score to verdict.
    
    Range:
    - 0.7 - 1.0: High
    - 0.4 - 0.7: Medium
    - < 0.4: Low
    """
    if score >= 0.7:
        return "High"
    elif score >= 0.4:
        return "Medium"
    else:
        return "Low"

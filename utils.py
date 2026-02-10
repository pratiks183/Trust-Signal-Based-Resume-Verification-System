import re
from urllib.parse import urlparse

def normalize_string(s: str) -> str:
    """Lowercase and strip whitespace."""
    if not s:
        return ""
    return s.lower().strip()

def extract_domain(url: str) -> str:
    """Extracts the domain from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""

def is_linkedin_url(url: str) -> bool:
    """Checks if a URL is a LinkedIn company page."""
    domain = extract_domain(url)
    return "linkedin.com" in domain and "/company/" in url

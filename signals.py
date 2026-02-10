from typing import List, Dict
from search_client import SearchResult
from utils import extract_domain, is_linkedin_url, normalize_string

class SignalExtractor:
    def extract_signals(self, company_name: str, role: str, search_results: List[SearchResult]) -> Dict[str, bool]:
        normalized_company = normalize_string(company_name)
        website_found = False
        linkedin_found = False
        role_match = False
        company_found_anywhere = False
        unique_domains = set()

        normalized_role = normalize_string(role)
        role_tokens = set(normalized_role.split())
        
        ignored_words = {'intern', 'internship', 'trainee', 'associate', 'junior', 'senior', 'part-time', 'full-time'}
        meaningful_tokens = {t for t in role_tokens if t not in ignored_words and len(t) > 2}

        for result in search_results:
            domain = extract_domain(result.url)
            if not domain:
                continue
            
            unique_domains.add(domain)

            company_nospace = normalized_company.replace(" ", "")
            if company_nospace in domain.replace("-", ""):
                 if "linkedin" not in domain and "facebook" not in domain and "twitter" not in domain:
                     website_found = True
            
            if is_linkedin_url(result.url):
                linkedin_found = True
                
            content = (result.title + " " + result.snippet).lower()
            
            company_in_result = (normalized_company in content) or (company_nospace in content.replace(" ", ""))
            
            if company_in_result:
                company_found_anywhere = True
                
                match_count = 0
                for token in meaningful_tokens:
                    if token in content:
                        match_count += 1
                
                if len(meaningful_tokens) == 0:
                     pass
                elif len(meaningful_tokens) == 1:
                    if match_count >= 1:
                        role_match = True
                else:
                    if match_count >= 2:
                        role_match = True

        multiple_sources = len(unique_domains) >= 2
        
        role_reason = "Role verified via public digital footprint"
        
        if not role_match:
            if company_found_anywhere:
                 role_reason = "Role Not Associated with This Company"
            else:
                 role_reason = "No public evidence of this role at the company"

        return {
            "website_found": website_found,
            "linkedin_found": linkedin_found,
            "multiple_sources_found": multiple_sources,
            "role_match": role_match,
            "role_reason": role_reason,
            "maturity_level": self.detect_company_maturity(normalized_company, search_results)
        }

    def detect_company_maturity(self, company_name: str, search_results: List[SearchResult]) -> str:
        """
        Infers company maturity based on known lists and snippet keywords.
        Returns: 'Global', 'Established', 'SME', or 'Unknown'.
        """
        company_lower = company_name.lower()
        
        # 1. Known Lists (Prototype Heuristics)
        GLOBAL_GIANTS = {
            "google", "amazon", "microsoft", "apple", "facebook", "meta", 
            "netflix", "tesla", "ibm", "oracle", "salesforce", "adobe",
            "intel", "nvidia", "samsung", "sony", "toyota", "cocacola", "pepsi"
        }
        
        ESTABLISHED_COMPANIES = {
            "zoho", "freshworks", "flipkart", "swiggy", "zomato", "paytm", 
            "uber", "airbnb", "stripe", "spotify", "shopify", "slack",
            "atlassian", "infosys", "tcs", "wipro", "hcl", "accenture",
            "deloitte", "kpmg", "pwc", "ey", "capgemini", "cognizant"
        }
        
        # Check simplistic known lists first
        for giant in GLOBAL_GIANTS:
            if giant in company_lower:
                return "Global"
                
        for established in ESTABLISHED_COMPANIES:
            if established in company_lower:
                return "Established"

        # 2. Snippet Keyword Analysis for "Footprint"
        # We look for signals of scale in the search snippets
        maturity_keywords = [
            "fortune 500", "nasdaq", "nyse", "publicly traded", "multinational",
            "global offices", "headquarters in", "thousands of employees",
            "leader in", "established in", "founded in 19", "founded in 18"
        ]
        
        keyword_hits = 0
        combined_snippets = " ".join([r.snippet.lower() for r in search_results])
        
        for kw in maturity_keywords:
            if kw in combined_snippets:
                keyword_hits += 1
                
        # If we find strong signals of maturity
        if keyword_hits >= 2:
            return "Established"
            
        # 3. Default Fallback
        # If we have basic signals (website + LinkedIn) but no "giant" keywords, it's likely an SME/Startup
        # We'll determine "SME" vs "Unknown" based on signal strength in the caller, 
        # but here we return a baseline. 
        # Actually, let's distinguish "SME" (has presence) from "Unknown" (ghost)
        
        has_website = False
        has_linkedin = False
        
        for r in search_results:
            if "linkedin.com/company" in r.url:
                has_linkedin = True
            # Simple heuristic for website: not linkedin/fb/twitter/insta
            domain = extract_domain(r.url)
            if domain and not any(x in domain for x in ["linkedin", "facebook", "twitter", "instagram", "glassdoor", "crunchbase"]):
               has_website = True

        if has_website or has_linkedin:
            return "SME"
            
        return "Unknown"

import os
import google.generativeai as genai
from google.api_core import exceptions
import json
from typing import List, Dict
from dotenv import load_dotenv


load_dotenv(override=True)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    print(f"DEBUG: Loaded API Key: {GEMINI_API_KEY[:5]}...{GEMINI_API_KEY[-5:]}")
else:
    print("DEBUG: No API Key found.")

class SearchResult:
    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet
    
    def to_dict(self):
        return {"title": self.title, "url": self.url, "snippet": self.snippet}

class GeminiSearchClient:
    _cache = {}

    def __init__(self):
        if not GEMINI_API_KEY or "YOUR_API_KEY" in GEMINI_API_KEY:

             print("Warning: Gemini API Key not found. Set GEMINI_API_KEY env var.")
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite-001')
            
            try:
                self.grounded_model = genai.GenerativeModel('gemini-2.0-flash-lite-001', tools='google_search_retrieval')
            except Exception:
                self.grounded_model = None


    def search(self, query: str) -> List[SearchResult]:
        """
        Simulates a search using Gemini to generate potential search results.
        Returns a list of SearchResult objects.
        """
        if not GEMINI_API_KEY or "YOUR_API_KEY" in GEMINI_API_KEY:

            return []

        if query in self._cache:
            print(f"DEBUG: Cache hit for query: '{query}'")
            return self._cache[query]

        if self.grounded_model:
            try:
                response = self.grounded_model.generate_content(
                    f"Find official website and linkedin page for: {query}. If not found or looks fake, say 'Not Found'."
                )
                
                if hasattr(response.candidates[0], 'grounding_metadata') and response.candidates[0].grounding_metadata.search_entry_point:
                    pass
            except Exception as e:
                print(f"Grounding failed, falling back to simulation: {e}")

        prompt = f"""
        You are a STRICT Resume Verification Assistant.
        Your task is to find REAL, VERIFIABLE digital footprints for the company AND role in this query: "{query}".
        
        Rules for Output:
        1. Verify BOTH the company and whether the provided role or internship is plausibly associated with that company.
        2. If the company is famous (e.g. "Amazon", "Google") but the role is fake/random (e.g. "Sndfg", "King of World"), DO NOT INVENT A WEBSITE for the role. Return evidence for the company only if requested, but clearly distinguishing the role is not found is key.
        3. Actually, just return valid public links found.
        4. CRITICAL: If the role appears random, unsupported, or meaningless (e.g. "Sndfg"), return no role evidence even if the company exists.
        5. CROSS-COMPANY CHECK: If the query combines a company with a role associated with a different specific entity (e.g. "Google AWS Intern"), DO NOT return results that just compare them (e.g. "Google vs AWS"). Only return results if the internship is ACTUALLY AT the requested company. If in doubt, return NOTHING.
        
        Output format:
        A JSON list of objects with keys: "title", "url", "snippet".
        
        Example for "Google Software Engineer": 
        [{{"title": "Google Careers - Software Engineering", "url": "https://careers.google.com/jobs", "snippet": "Apply to Software Engineer jobs at Google..."}}]
        
        Example for "Google Sndfg": 
        [{{"title": "Google", "url": "https://www.google.com", "snippet": "Google official website..."}}] 
        (Notice: No mention of "Sndfg" in snippet or title, so role_match will fail downstream)
        
        Example for "Google AWS Intern":
        [] 
        (Notice: Returns empty because AWS is Amazon's product, not Google's role)
        
        Output STRICT JSON only. No markdown formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)

            if not hasattr(response, "candidates") or not response.candidates:
                print(f"WARNING: No candidates returned for query: {query}")
                self._cache[query] = []
                return []

            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text)
            results = []
            for item in data:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", "")
                ))
            
            self._cache[query] = results
            return results
            
        except exceptions.ResourceExhausted as e:
            print(f"ERROR: Gemini API Quota Exceeded. Details: {e}")
            raise 
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            raise e

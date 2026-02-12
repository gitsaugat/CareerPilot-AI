import requests
# Using a simple text extraction approach. 
# For a production app, use beautifulsoup4.
# Assuming user has beautifulsoup4 installed as it's common, but if not, we can fall back to simple string manipulation or check deps.
# Given constraints, let's try to use basic requests + text processing, 
# or use `ollama` to process the raw HTML if it's not too huge.

def fetch_url_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def extract_job_info(html_content, analyzer):
    """
    Uses the AI analyzer to extract Title and Description from HTML.
    This is expensive but effective for unstructured data.
    """
    # Truncate HTML to avoid token limits (heuristically, body content is usually in first 15k chars for job boards)
    # or better, use a text extractor first.
    # For now, let's just strip tags partially or send a chunk.
    
    # Simple tag stripping to reduce noise
    import re
    clean_text = re.sub('<[^<]+?>', ' ', html_content[:20000]) # First 20k chars
    clean_text = re.sub('\s+', ' ', clean_text).strip()
    
    prompt = f"""
    Analyze the following web page text and extract the Job Title and Job Description.
    Return ONLY a JSON object with keys "title" and "description".
    
    Web Page Text:
    {clean_text[:8000]} 
    """
    
    # We can reuse the analyzer's internal LLM call or just call ollama directly if exposed.
    # Since `ResumeAnalyzer` has `analyze` which is specific to Resume vs JD,
    # we might need to expose a generic `generate` method or similar.
    # For now, let's assume we can add a method to `ResumeAnalyzer` or import ollama here.
    
    import ollama
    try:
        response = ollama.chat(model='gpt-oss:120b-cloud', messages=[
            {'role': 'user', 'content': prompt}
        ])
        content = response['message']['content']
        
        # Try to parse JSON
        import json
        # Find first { and last }
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = content[start:end]
            return json.loads(json_str)
        else:
            return {"title": "Extracted Job", "description": content}
            
    except Exception as e:
        print(f"AI Extraction failed: {e}")
        return None

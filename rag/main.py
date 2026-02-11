import ollama
import json
import logging
from pypdf import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    def __init__(self, model_name="gpt-oss:120b-cloud"):
        self.model_name = model_name

    def extract_text_from_pdf(self, pdf_path):
        """Extracts text from a PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None

    def analyze(self, resume_path, job_description):
        """
        Analyzes a resume against a job description using Ollama.
        Returns a dictionary with score, summary, matching_keywords, missing_keywords, and recommendations.
        """
        resume_text = self.extract_text_from_pdf(resume_path)
        if not resume_text:
            return {
                "score": 0,
                "summary": "Error: Could not extract text from resume.",
                "matching_keywords": [],
                "missing_keywords": [],
                "recommendations": []
            }

        # prompt for the LLM
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) and Resume Coach.
        Compare the following Resume against the Job Description.

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        Analyze the match and return a valid JSON object with the following fields:
        - "score": A number between 0 and 100 representing the match percentage.
        - "summary": A brief (1-2 sentences) summary of the fit.
        - "matching_keywords": A list of strings (skills/keywords present in both).
        - "missing_keywords": A list of strings (skills/keywords in JD but missing in Resume).
        - "recommendations": A list of strings (3-5 actionable tips to improve the resume for this job).

        Ensure the response is purely valid JSON, no markdown formatting.
        """

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json', # Enforce JSON mode if supported, otherwise styling prompt is key
                options={'temperature': 0.1}
            )
            
            content = response['message']['content']
            # Parse JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Fallback if raw text has markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                    return json.loads(content)
                logger.error(f"Failed to parse JSON response: {content}")
                return None

        except Exception as e:
            logger.error(f"Error during AI analysis: {e}")
            return {
                "score": 0,
                "summary": f"Error during analysis: {str(e)}",
                "matching_keywords": [],
                "missing_keywords": [],
                "recommendations": []
            }

# Singleton instance or factory can be used if needed
analyzer = ResumeAnalyzer()
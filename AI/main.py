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
        - "Updated resume" : A newly revised resume based on the job description. Use strict MARKDOWN format.
          CRITICAL: The resume MUST be designed to fit on a SINGLE PAGE.
          - Structure: Header (Name/Contact), Professional Summary (3 lines max), Experience (reverse chronological, focus on achievements), Skills, Education.
          - Use concise, impact-driven bullet points.
          - No conversational filler or explanations.
          - Use professional formatting (## for sections, ### for roles, * for bullets).
        Ensure the response is purely valid JSON, no markdown formatting outside the JSON structure.
        """

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json', # Enforce JSON mode if supported, otherwise styling prompt is key
                options={'temperature': 0.1}
            )
            
            content = response['message']['content']
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
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

    def generate_cover_letter(self, resume_path, job_description):
        """Generate a customized cover letter."""
        resume_text = self.extract_text_from_pdf(resume_path)
        if not resume_text:
            return None
            
        prompt = f"""
        You are an expert career coach and professional writer.
        Write a compelling, professional cover letter for the candidate based on their resume and the job description.
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {resume_text}
        
        The cover letter should:
        1. Address the hiring manager professionally.
        2. Highlight key skills from the resume that match the job.
        3. Express enthusiasm for the role and company.
        4. Be formatted in Markdown.
        5. Keep it concise (under 400 words).
        """
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return None

    def generate_interview_prep(self, resume_path, job_description):
        """Generate interview preparation questions and answers."""
        resume_text = self.extract_text_from_pdf(resume_path)
        if not resume_text:
            return None
            
        prompt = f"""
        You are an expert technical recruiter and interview coach.
        Generate a set of interview preparation materials based on the candidate's resume and the job description.
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {resume_text}
        
        Output a valid JSON object with the following structure:
        {{
            "technical_questions": [
                {{"question": "...", "ideal_answer_points": "..."}}
            ],
            "behavioral_questions": [
                {{"question": "...", "star_answer_guide": "..."}}
            ],
            "questions_to_ask_interviewer": [
                "..."
            ]
        }}
        """
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0.7}
            )
            content = response['message']['content']
            try:
                return json.loads(content)
            except:
                if "```json" in content:
                    return json.loads(content.split("```json")[1].split("```")[0])
                return json.loads(content) 
        except Exception as e:
            logger.error(f"Error generating interview prep: {e}")
            return None


# Singleton instance or factory can be used if needed
analyzer = ResumeAnalyzer()
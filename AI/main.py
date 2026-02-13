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

    def analyze(self, resume_path, job_description, model_name=None):
        """
        Analyzes a resume against a job description using Ollama.
        Returns a dictionary with score, summary, matching_keywords, missing_keywords, and recommendations.
        """
        model_to_use = model_name if model_name else self.model_name
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
        You are a razor-sharp Fortune 500 Executive Recruiter and ATS Optimization Expert.
        Your goal is to ruthlessly critique this resume and rewrite it to effectively guarantee an interview for the specific job description.

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        TASK:
        1. Analyze the resume against the JD to determine a match score.
        2. Identify critical hard skills and keywords missing from the resume.
        3. Rewrite the resume to be a "Perfect Match" for this specific JD.

        OUTPUT VALID JSON ONLY:
        {{
            "score": <0-100 integer. Be strict. <70 is a fail.>,
            "summary": "<Direct, no-fluff assessment of fit. Start with 'Strong Fit', 'Potential Fit', or 'Poor Fit'.>",
            "matching_keywords": ["<skill1>", "<skill2>"],
            "missing_keywords": ["<CRITICAL missing skill from JD>", "<missing tool/tech>"],
            "recommendations": [
                "<Actionable advice 1>",
                "<Actionable advice 2>",
                "<Actionable advice 3>"
            ],
            "updated_resume_markdown": "<Full Markdown content of the rewritten resume>"
        }}

        REWRITE RULES FOR 'updated_resume_markdown':
        - FORMAT: Standard Markdown. Use '##' for sections.
        - LENGTH: Strictly 1 page equivalent (approx 400-600 words).
        - SUMMARY: 3 sentences max. Pitch the candidate as the *solution* to the JD's problems.
        - EXPERIENCE:
            - Reword bullet points to match JD keywords exactly.
            - Use the 'Action + Context + Result' formula.
            - QUANTIFY RESULTS. If exact numbers are missing, plausible placeholders like '[X]%' or '$[Y]k'.
            - Remove weak verbs (e.g., 'Responsible for', 'Helped with'). Use strong verbs (e.g., 'Spearheaded', 'Optimized', 'Generated').
        - SKILLS: Group by category (e.g., Languages, Frameworks, Tools) to match JD structure.
        """

        try:
            response = ollama.chat(
                model=model_to_use,
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

    def generate_cover_letter(self, resume_path, job_description, model_name=None):
        """Generate a customized cover letter."""
        model_to_use = model_name if model_name else self.model_name
        resume_text = self.extract_text_from_pdf(resume_path)
        if not resume_text:
            return None
            
        prompt = f"""
        You are a professional Ghostwriter for top executives.
        Write a disruptive, attention-grabbing cover letter that breaks the mold of "I am writing to apply...".
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {resume_text}
        
        GUIDELINES:
        1. Hook the reader immediately in the first sentence with a relevant achievement or passion.
        2. Focus on "What I can do for you", not "What I have done".
        3. Use a confident, professional, but human tone.
        4. Keep it under 250 words. Short and punchy.
        5. Format in Markdown.
        
        Structure:
        - Hook (The "Why me")
        - The Proof (1-2 key achievements mapping to JD pains)
        - The Close (Call to action)
        """
        
        try:
            response = ollama.chat(
                model=model_to_use,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return None

    def generate_interview_prep(self, resume_path, job_description, model_name=None):
        """Generate interview preparation questions and answers."""
        model_to_use = model_name if model_name else self.model_name
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
                model=model_to_use,
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

    def generate_networking_messages(self, resume_path, job_description, model_name=None):
        """Generate networking messages (Cold Email & LinkedIn)."""
        model_to_use = model_name if model_name else self.model_name
        resume_text = self.extract_text_from_pdf(resume_path)
        if not resume_text:
            return None
            
        prompt = f"""
        You are an expert career coach and networking strategist.
        Generate networking messages for a candidate based on their resume and a target job description.
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {resume_text}
        
        Output a valid JSON object with the following structure:
        {{
            "cold_email_hiring_manager": {{
                "subject": "...",
                "body": "..." 
            }},
            "linkedin_connection_request": "Max 300 characters. Professional and personalized.",
            "informational_interview_request": "Email body asking for 15 mins of advice from a peer."
        }}
        """
        
        try:
            response = ollama.chat(
                model=model_to_use,
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
            logger.error(f"Error generating networking messages: {e}")
            return None

    def optimize_linkedin(self, resume_path, job_description, model_name=None):
        """Generate LinkedIn profile optimization suggestions."""
        model_to_use = model_name if model_name else self.model_name
        resume_text = self.extract_text_from_pdf(resume_path)
        if not resume_text:
            return None
            
        prompt = f"""
        You are a LinkedIn Profile Expert.
        Optimize the candidate's LinkedIn profile to attract recruiters for the specific target job.
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {resume_text}
        
        Output a valid JSON object with the following structure:
        {{
            "headline": "SEO-optimized headline (max 220 chars)",
            "about_section": "Engaging, first-person summary optimized for the target role.",
            "key_skills_to_pin": ["Skill 1", "Skill 2", "Skill 3"],
            "experience_enhancements": [
                "Specific bullet point to add to latest role...",
                "Keyword to emphasize..."
            ]
        }}
        """
        
        try:
            response = ollama.chat(
                model=model_to_use,
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
            logger.error(f"Error optimizing LinkedIn profile: {e}")
            return None

    def generate_negotiation_scripts(self, job_title, offer_details=None, model_name=None):
        """Generate salary negotiation scripts."""
        model_to_use = model_name if model_name else self.model_name
        
        context = f"Job Title: {job_title}"
        if offer_details:
            context += f"\nOffer Details: {offer_details}"
            
        prompt = f"""
        You are a Salary Negotiation Coach.
        Generate scripts and strategies for a candidate negotiating a job offer.
        
        CONTEXT:
        {context}
        
        Output a valid JSON object with the following structure:
        {{
            "email_script": "Professional email counter-offer script.",
            "phone_script": "Bullet points for a phone conversation.",
            "questions_to_ask": ["Question to uncover budget...", "Question about benefits..."],
            "strategy_tips": ["Tip 1", "Tip 2"]
        }}
        """
        
        try:
            response = ollama.chat(
                model=model_to_use,
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
            logger.error(f"Error generating negotiation scripts: {e}")
            return None


# Singleton instance or factory can be used if needed
analyzer = ResumeAnalyzer()
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
        You are a tough, no-nonsense Senior Executive Recruiter.
        Your job is to brutally critique this resume and rewrite it to get the candidate hired for the specific job description.

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        Analyze the fit and return a valid JSON object with the following fields:
        - "score": A number between 0 and 100. Be strict. High scores (90+) are reserved for perfect matches.
        - "summary": A direct, honest assessment of why they are or are not a fit.
        - "matching_keywords": List of hard skills found in both.
        - "missing_keywords": List of critical hard skills from the JD missing in the resume. EXPERT TIP: Do not hallucinate.
        - "recommendations": A list of 3-5 specific, harsh, and actionable changes. 
           Example: "Change 'Responsible for sales' to 'Generated $50k in pipeline monthly'."
        - "Updated resume" : A completely rewritten, top-tier professional resume in strict MARKDOWN.
          RULES:
          1. SINGLE PAGE ONLY. Cut fluff ruthlessly.
          2. Professional Summary: 2-3 powerful sentences pitching the candidate for THIS specific role.
          3. Experience: Rewrite bullet points to be "Result + Action + Context". Use numbers/metrics where possible (even if estimated placeholders like '[X]%').
          4. Skills: Group by category (e.g., Languages, Frameworks).
          5. Formatting: standard Markdown (## Headers, * Bullets). No images or columns.

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

    def generate_networking_messages(self, resume_path, job_description):
        """Generate networking messages (Cold Email & LinkedIn)."""
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
            logger.error(f"Error generating networking messages: {e}")
            return None

    def optimize_linkedin(self, resume_path, job_description):
        """Generate LinkedIn profile optimization suggestions."""
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
            logger.error(f"Error optimizing LinkedIn profile: {e}")
            return None

    def generate_negotiation_scripts(self, job_title, offer_details=None):
        """Generate salary negotiation scripts."""
        
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
            logger.error(f"Error generating negotiation scripts: {e}")
            return None


# Singleton instance or factory can be used if needed
analyzer = ResumeAnalyzer()
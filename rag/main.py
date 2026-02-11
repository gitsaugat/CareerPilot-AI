import ollama
import faiss
import numpy as np
tetx = """
About the job
Kick start your career with a paid internship at Sodexo! Working with Sodexo is more than a job; it’s a chance to be part of something greater because we believe our everyday actions have a big impact.

Sodexo’s Strategic Internship Program has an opening within the Finance and Accounting. This internship is designed to provide hands-on experience in learning how to perform reconciliations, navigate in our ERP System, and other auxiliary software as it relates to supporting Banking and Credit Card activities and the associated Accounting for these workflows.

As an Intern in this position, you would experience first-hand the company's revenue recognition policies and cash handling procedures and see examples of automation of postings and system enhancements for management of large volumes of data along with supporting Sodexo's business units.

This is a hybrid internship program, requires 3 days in office at our Cheektowaga location. Summer Internship June 1, 2026 – August 7, 2026. What You'll Do

Key Responsibilities: 
Learn the fundamentals of performing timely reconciliation of non-standard Banking and Credit Card Service Activity using Frontier, SAP and third-party vendor applications
Work alongside team members to Investigate reconciliation issues escalated by offshore reconcilers; working with field personnel, Point of Sale vendors, and various other credit card equipment processing system providers to understand root cause variances and mitigating loss in revenue streams.
Learn how to identify trends and monitor Reconciliation Patterns for reporting inconsistencies, deposit or settlement issues, and mitigation of risk of loss of company assets
Learn how to proactively look for process improvements and provide recommendations for the Management of end-to-end process improvements for Banking activities and work on supporting process improvement enhancements and the associated testing, review, and development requirements prior to implementation
Assist and help pull supporting documentation to prepare Audit Workpapers for Auditors and work with the team to prove these requests and see the control process within the organization that supports the postings
Special projects as needed
What We Offer

Compensation is fair and equitable, partially determined by a candidate's education level or years of relevant experience. Salary offers are based on a candidate's specific criteria, like experience, skills, education, and training. Sodexo offers a comprehensive benefits package that may include:

Medical, Dental, Vision Care and Wellness Programs
401(k) Plan with Matching Contributions
Paid Time Off and Company Holidays
Career Growth Opportunities and Tuition Reimbursement
More extensive information is provided to new employees upon hire.

What You Bring

Minimum Qualifications: 
Currently pursuing a Bachelor of Science Degree in Accounting, Finance or Business
0-2 years' accounting experience or related college courses
Excellent verbal & written communication skills
Ability to work independently, as well as in a team environment
Managing multiple priorities and time management skills
Strong technical and attention to detail
Strong PC & related software knowledge
Who We Are

At Sodexo, our purpose is to create a better everyday for everyone and build a better life for all. We believe in improving the quality of life for those we serve and contributing to the economic, social, and environmental progress in the communities where we operate. Sodexo partners with clients to provide a truly memorable experience for both customers and employees alike. We do this by providing food service, catering, facilities management, and other integrated solutions worldwide.

Our company values you for you; you will be treated fairly and with respect, and you can be yourself. You will have your ideas count and your opinions heard because we can be a stronger team when you’re happy at work. This is why we embrace diversity and inclusion as core values, fostering an environment where all employees are valued and respected. We are committed to providing equal employment opportunities to individuals regardless of race, color, religion, national origin, age, sex, gender identity, pregnancy, disability, sexual orientation, military status, protected veteran status, or any other characteristic protected by applicable federal, state, or local law. If you need assistance with the application process, please complete this form.

Qualifications & Requirements Minimum Education Requirement - Current college student with studies in hospitality/food management, facilities management, engineering, communications, human resources, accounting, marketing or another industry related college program.


"""
class RAG:
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self.index = None

    def chunk_text(self, text, chunk_size=500, overlap=100):
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i+chunk_size])
        self.chunks = chunks

    def embed_text(self, text):
        response = ollama.embeddings(
            model="nomic-embed-text",
            prompt=text
        )
        return response["embedding"]

    def get_embeddings(self):
        self.embeddings = [self.embed_text(chunk) for chunk in self.chunks]
        print(self.embeddings)
        return self.embeddings

    def build_index(self):
        self.index = faiss.IndexFlatL2(len(self.embeddings[0]))
        self.index.add(np.array(self.embeddings))
        return self.index


rag = RAG()
rag.chunk_text(tetx)
rag.embed_text(tetx)
rag.get_embeddings()
rag.build_index()
print(rag.index)
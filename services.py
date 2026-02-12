from AI.main import ResumeAnalyzer
from markdown_it import MarkdownIt

# Initialize Analyzer (uses 'gpt-oss:120b-cloud' by default as per req)
analyzer = ResumeAnalyzer(model_name="gpt-oss:120b-cloud")
md = MarkdownIt()

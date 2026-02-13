from flask import Flask
import os
from flask_migrate import Migrate
from extensions import db
from services import md

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.jobs import jobs_bp
from routes.resumes import resumes_bp
from routes.tools import tools_bp
from routes.settings import settings_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# SQLite database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads", "resumes")
app.config["ALLOWED_RESUME_EXTENSIONS"] = {"pdf", "doc", "docx"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(resumes_bp)
app.register_blueprint(tools_bp)
app.register_blueprint(settings_bp)

# Register Template Filters
@app.template_filter('markdown')
def markdown_filter(text):
    return md.render(text) if text else ""

if __name__ == "__main__":
    app.run(debug=True)

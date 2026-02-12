from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
    abort,
)
import os
import time
from pathlib import Path
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

from extensions import db
from models import User, Resume
from models.job import Job

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# SQLite database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads", "resumes")
app.config["ALLOWED_RESUME_EXTENSIONS"] = {"pdf", "doc", "docx"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB


def allowed_resume_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in app.config["ALLOWED_RESUME_EXTENSIONS"]


# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        zip_code = request.form.get("zip_code", "").strip()
        country = request.form.get("country", "").strip()
        role = request.form.get("role", "").strip() or "user"

        required = {
            "username": username,
            "email": email,
            "password": password,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "country": country,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            flash("Please fill in all required fields.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
        else:
            user = User(
                username=username,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                country=country,
                role=role,
                status="active",
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))

    resumes = Resume.query.order_by(Resume.created_at.desc()).all()

    selected_resume = None
    can_preview_pdf = False
    viewer_url = None

    selected_id = request.args.get("resume_id", type=int)
    if selected_id:
        selected_resume = Resume.query.get(selected_id)
    elif resumes:
        selected_resume = resumes[0]

    if selected_resume and os.path.exists(selected_resume.resume_file_path):
        ext = Path(selected_resume.resume_file_path).suffix.lower()
        if ext == ".pdf":
            can_preview_pdf = True
            viewer_url = url_for("view_resume_inline", resume_id=selected_resume.id)

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        resumes=resumes,
        selected_resume=selected_resume,
        can_preview_pdf=can_preview_pdf,
        viewer_url=viewer_url,
    )


@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "user_id" not in session:
        flash("Please log in to upload a resume.", "error")
        return redirect(url_for("login"))

    file = request.files.get("resume_file")
    name = request.form.get("name", "").strip()
    resume_text = request.form.get("resume_text", "").strip()

    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("dashboard"))

    if not allowed_resume_file(file.filename):
        flash("Unsupported file type. Allowed: pdf, doc, docx.", "error")
        return redirect(url_for("dashboard"))

    original_filename = secure_filename(file.filename)
    if not name:
        name = original_filename

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    unique_name = f"{int(time.time())}_{original_filename}"
    full_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)

    file.save(full_path)

    resume = Resume(
        name=name,
        resume_text=resume_text or "",
        resume_file_path=full_path,
        user_id=session["user_id"],
    )
    db.session.add(resume)
    db.session.commit()

    flash("Resume uploaded successfully.", "success")
    return redirect(url_for("dashboard", resume_id=resume.id))


@app.route("/resumes/<int:resume_id>")
def download_resume(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to access resumes.", "error")
        return redirect(url_for("login"))

    resume = Resume.query.get_or_404(resume_id)
    if not os.path.exists(resume.resume_file_path):
        abort(404)

    download_name = os.path.basename(resume.resume_file_path)
    return send_file(resume.resume_file_path, as_attachment=True, download_name=download_name)


@app.route("/resumes/<int:resume_id>/delete", methods=["POST"])
def delete_resume(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to manage resumes.", "error")
        return redirect(url_for("login"))

    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session["user_id"]:
        flash("You are not allowed to delete this resume.", "error")
        return redirect(url_for("dashboard"))

    # Remove file from disk if it still exists
    if os.path.exists(resume.resume_file_path):
        try:
            os.remove(resume.resume_file_path)
        except OSError:
            # If deletion fails, we still remove the DB record
            pass

    db.session.delete(resume)
    db.session.commit()

    flash("Resume deleted.", "success")
    return redirect(url_for("dashboard"))


from AI.main import ResumeAnalyzer
from markdown_it import MarkdownIt

# Initialize Analyzer (uses 'gpt-oss:120b-cloud' by default as per req)
analyzer = ResumeAnalyzer(model_name="gpt-oss:120b-cloud")
md = MarkdownIt()

@app.template_filter('markdown')
def markdown_filter(text):
    return md.render(text) if text else ""




# ... (Existing imports)

# --- Job Routes ---

@app.route("/jobs")
def jobs_list():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    jobs = Job.query.filter_by(user_id=session["user_id"]).order_by(Job.created_at.desc()).all()
    return render_template("jobs/list.html", jobs=jobs)

@app.route("/jobs/create", methods=["GET", "POST"])
def jobs_create():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        company = request.form.get("company")
        job_url = request.form.get("job_url")
        status = request.form.get("status", "Saved")
        notes = request.form.get("notes")
        
        if title and description:
            try:
                new_job = Job(
                    title=title, 
                    description=description, 
                    company=company,
                    job_url=job_url,
                    status=status,
                    notes=notes,
                    user_id=session["user_id"]
                )
                db.session.add(new_job)
                db.session.commit()
                flash("Job created successfully!", "success")
                return redirect(url_for("jobs_list"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error creating job: {e}", "error")
        else:
            flash("Please fill in all fields.", "error")
            
    return render_template("jobs/create.html")

@app.route("/jobs/<int:job_id>")
def jobs_detail(job_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    job = Job.query.get_or_404(job_id)
    if job.user_id != session["user_id"]:
        flash("Access denied.", "error")
        return redirect(url_for("jobs_list"))
        
    return render_template("jobs/detail.html", job=job)

# --- End Job Routes ---

# --- Ranking Routes ---

@app.route("/ranking/select", methods=["GET", "POST"])
def ranking_select():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        job_id = request.form.get("job_id")
        resume_ids = request.form.getlist("resume_ids")
        
        if not job_id or not resume_ids:
            flash("Please select a job and at least one candidate.", "error")
            return redirect(url_for("ranking_select"))
            
        return redirect(url_for("ranking_process", job_id=job_id, resume_ids=",".join(resume_ids)))

    # GET: Show Selection Form
    jobs = Job.query.filter_by(user_id=session["user_id"]).order_by(Job.created_at.desc()).all()
    resumes = Resume.query.filter_by(user_id=session["user_id"]).order_by(Resume.created_at.desc()).all()
    return render_template("ranking/select.html", jobs=jobs, resumes=resumes)

@app.route("/ranking/process")
def ranking_process():
    if "user_id" not in session:
        return redirect(url_for("login"))

    job_id = request.args.get("job_id")
    resume_ids_str = request.args.get("resume_ids")
    
    if not job_id or not resume_ids_str:
        return redirect(url_for("ranking_select"))
        
    job = Job.query.get_or_404(job_id)
    resume_ids = [int(id) for id in resume_ids_str.split(",")]
    # Assuming Resume model is imported or available (it is in main.py)
    # We need to import Resume if not already, but it usually is. 
    # Let's check imports. Resume might be in models.resumes or similar.
    # Based on existing code, `from models.resumes import Resume` is likely needed if not present.
    # However, existing routes use `Resume` so it must be imported.
    resumes = Resume.query.filter(Resume.id.in_(resume_ids)).all()
    
    results = []
    
    for resume in resumes:
        try:
            analysis = analyzer.analyze(resume.resume_file_path, job.description)
            if analysis:
                results.append({
                    "resume": resume,
                    "score": analysis.get("score", 0),
                    "summary": analysis.get("summary", "No summary available")
                })
        except Exception as e:
            print(f"Failed to analyze resume {resume.id}: {e}")
            
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return render_template("ranking/results.html", job=job, results=results)

# --- End Ranking Routes ---

@app.route("/compare/<int:resume_id>", methods=["GET", "POST"])
def compare_resume(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to compare resumes.", "error")
        return redirect(url_for("login"))

    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session["user_id"]:
        flash("You are not allowed to view this resume.", "error")
        return redirect(url_for("dashboard"))

    can_preview_pdf = False
    viewer_url = None
    if os.path.exists(resume.resume_file_path):
        ext = Path(resume.resume_file_path).suffix.lower()
        if ext == ".pdf":
            can_preview_pdf = True
            viewer_url = url_for("view_resume_inline", resume_id=resume.id)

    job_description_html = ""
    analysis_results = None

    analysis_results = None

    if request.method == "POST":
        job_description_html = request.form.get("job_description", "")
        
        # Real AI Analysis
        if job_description_html.replace("<p>", "").replace("</p>", "").strip():
            try:
                # Assuming job_description_html contains HTML, we might want to strip tags
                # For simplicity, passing it as is, or could use BeautifulSoup. 
                # The LLM is smart enough to ignore basic HTML tags usually.
                analysis_results = analyzer.analyze(resume.resume_file_path, job_description_html)
                if not analysis_results:
                     flash("Analysis failed. Please try again.", "error")
            except Exception as e:
                flash(f"An error occurred during analysis: {e}", "error")
        else:
            flash("Please enter a job description.", "error")

    # Fetch Saved Jobs for Sidebar/Dropdown
    saved_jobs = Job.query.filter_by(user_id=session["user_id"]).order_by(Job.created_at.desc()).all()

    return render_template(
        "compare.html",
        resume=resume,
        can_preview_pdf=can_preview_pdf,
        viewer_url=viewer_url,
        job_description_html=job_description_html,
        analysis_results=analysis_results,
        jobs=saved_jobs
    )


@app.route("/resumes/<int:resume_id>/view")
def view_resume_inline(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to access resumes.", "error")
        return redirect(url_for("login"))

    resume = Resume.query.get_or_404(resume_id)
    if not os.path.exists(resume.resume_file_path):
        abort(404)

    ext = Path(resume.resume_file_path).suffix.lower()
    if ext != ".pdf":
        abort(415)

    return send_file(resume.resume_file_path, mimetype="application/pdf")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


from utils.scraper import fetch_url_content, extract_job_info

@app.route("/api/extract-job", methods=["POST"])
def api_extract_job():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    # 1. Fetch content
    html_content = fetch_url_content(url)
    if not html_content:
        return jsonify({"error": "Failed to fetch URL. Check if it's valid."}), 400
        
    # 2. Extract Info using AI
    # We pass the analyzer to the helper, specifically the LLM part if needed, 
    # but scraper.py imports ollama directly in my implementation.
    # Let's double check scraper.py. It imports ollama.
    
    extracted_data = extract_job_info(html_content, analyzer)
    
    if extracted_data:
        return jsonify(extracted_data)
    else:
        return jsonify({"error": "Failed to extract job info."}), 500
@app.route("/cover-letter", methods=["GET", "POST"])
def cover_letter():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    resumes = Resume.query.filter_by(user_id=user_id).all()
    jobs = Job.query.filter_by(user_id=user_id).all()
    
    generated_letter = None
    selected_resume_id = None
    job_description = ""
    
    if request.method == "POST":
        resume_id = request.form.get("resume_id")
        job_description = request.form.get("job_description")
        
        if resume_id and job_description:
            selected_resume_id = int(resume_id)
            resume = Resume.query.get(resume_id)
            if resume and resume.user_id == user_id:
                # Generate Cover Letter
                generated_letter = analyzer.generate_cover_letter(resume.resume_file_path, job_description)
                if not generated_letter:
                    flash("Failed to generate cover letter. Please try again.", "error")
            else:
                flash("Invalid resume selected.", "error")
        else:
            flash("Please select a resume and provide a job description.", "error")
            
    return render_template("tools/cover_letter.html", resumes=resumes, jobs=jobs, generated_letter=generated_letter, selected_resume_id=selected_resume_id, job_description=job_description)

@app.route("/interview-prep", methods=["GET", "POST"])
def interview_prep():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    resumes = Resume.query.filter_by(user_id=user_id).all()
    jobs = Job.query.filter_by(user_id=user_id).all()
    
    prep_material = None
    selected_resume_id = None
    job_description = ""
    
    if request.method == "POST":
        resume_id = request.form.get("resume_id")
        job_description = request.form.get("job_description")
        
        if resume_id and job_description:
            selected_resume_id = int(resume_id)
            resume = Resume.query.get(resume_id)
            if resume and resume.user_id == user_id:
                # Generate Interview Prep
                prep_material = analyzer.generate_interview_prep(resume.resume_file_path, job_description)
                if not prep_material:
                    flash("Failed to generate interview prep material. Please try again.", "error")
            else:
                flash("Invalid resume selected.", "error")
        else:
            flash("Please select a resume and provide a job description.", "error")
            
    return render_template("tools/interview_prep.html", resumes=resumes, jobs=jobs, prep_material=prep_material, selected_resume_id=selected_resume_id, job_description=job_description)

if __name__ == "__main__":
    app.run(debug=True)

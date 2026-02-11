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
from werkzeug.utils import secure_filename

from extensions import db
from models import User, Resume

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

# Create tables once at startup
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))
    resumes = Resume.query.order_by(Resume.created_at.desc()).all()
    return render_template(
        "dashboard.html",
        username=session.get("username"),
        resumes=resumes,
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

    resume = Resume(name=name, resume_text=resume_text or "", resume_file_path=full_path)
    db.session.add(resume)
    db.session.commit()

    flash("Resume uploaded successfully.", "success")
    return redirect(url_for("dashboard"))


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


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

from flask import Blueprint, send_file, request, redirect, url_for, session, flash, current_app, abort
from models import Resume
from extensions import db
from werkzeug.utils import secure_filename
import os
import time
from pathlib import Path

resumes_bp = Blueprint('resumes', __name__)

def allowed_resume_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_RESUME_EXTENSIONS"]

@resumes_bp.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "user_id" not in session:
        flash("Please log in to upload a resume.", "error")
        return redirect(url_for("auth.login"))

    file = request.files.get("resume_file")
    name = request.form.get("name", "").strip()
    resume_text = request.form.get("resume_text", "").strip()

    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("dashboard.dashboard"))

    if not allowed_resume_file(file.filename):
        flash("Unsupported file type. Allowed: pdf, doc, docx.", "error")
        return redirect(url_for("dashboard.dashboard"))

    original_filename = secure_filename(file.filename)
    if not name:
        name = original_filename

    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    unique_name = f"{int(time.time())}_{original_filename}"
    full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)

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
    return redirect(url_for("dashboard.dashboard", resume_id=resume.id))

@resumes_bp.route("/resumes/<int:resume_id>")
def download_resume(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to access resumes.", "error")
        return redirect(url_for("auth.login"))

    resume = Resume.query.get_or_404(resume_id)
    if not os.path.exists(resume.resume_file_path):
        abort(404)

    download_name = os.path.basename(resume.resume_file_path)
    return send_file(resume.resume_file_path, as_attachment=True, download_name=download_name)

@resumes_bp.route("/resumes/<int:resume_id>/delete", methods=["POST"])
def delete_resume(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to manage resumes.", "error")
        return redirect(url_for("auth.login"))

    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session["user_id"]:
        flash("You are not allowed to delete this resume.", "error")
        return redirect(url_for("dashboard.dashboard"))

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
    return redirect(url_for("dashboard.dashboard"))

@resumes_bp.route("/resumes/<int:resume_id>/view")
def view_resume_inline(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to access resumes.", "error")
        return redirect(url_for("auth.login"))

    resume = Resume.query.get_or_404(resume_id)
    if not os.path.exists(resume.resume_file_path):
        abort(404)

    ext = Path(resume.resume_file_path).suffix.lower()
    if ext != ".pdf":
        abort(415)

    return send_file(resume.resume_file_path, mimetype="application/pdf")

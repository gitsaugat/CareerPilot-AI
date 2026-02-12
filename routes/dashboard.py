from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from models import Job, Resume
import os
from pathlib import Path

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("auth.login"))

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
            viewer_url = url_for("resumes.view_resume_inline", resume_id=selected_resume.id)

    # Fetch Job Stats
    jobs = Job.query.filter_by(user_id=session["user_id"]).all()
    total_applications = len(jobs)
    interviews_count = len([j for j in jobs if j.status in ['Interviewing', 'Offer']])
    
    # Recent Activity (Last 5 jobs)
    recent_jobs = Job.query.filter_by(user_id=session["user_id"]).order_by(Job.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        resumes=resumes,
        selected_resume=selected_resume,
        can_preview_pdf=can_preview_pdf,
        viewer_url=viewer_url,
        total_applications=total_applications,
        interviews_count=interviews_count,
        recent_jobs=recent_jobs
    )

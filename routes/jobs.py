from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Job, Resume
from extensions import db
from datetime import datetime
from services import analyzer
from utils.scraper import fetch_url_content, extract_job_info

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route("/jobs")
def jobs_list():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    jobs = Job.query.filter_by(user_id=session["user_id"]).order_by(Job.created_at.desc()).all()
    return render_template("jobs/list.html", jobs=jobs)

@jobs_bp.route("/jobs/create", methods=["GET", "POST"])
def jobs_create():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    user_id = session["user_id"]
    
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        company = request.form.get("company")
        job_url = request.form.get("job_url")
        status = request.form.get("status", "Saved")
        location = request.form.get("location")
        salary_range = request.form.get("salary_range")
        notes = request.form.get("notes")
        resume_id = request.form.get("resume_id")
        interview_date_str = request.form.get("interview_date")
        
        interview_date = None
        if interview_date_str:
            try:
                interview_date = datetime.strptime(interview_date_str, "%Y-%m-%d")
            except ValueError:
                pass # Handle error or ignore

        if title: # Description might be empty if just tracking a link initially
            try:
                new_job = Job(
                    title=title, 
                    description=description or "", 
                    company=company,
                    job_url=job_url,
                    status=status,
                    location=location,
                    salary_range=salary_range,
                    notes=notes,
                    resume_id=int(resume_id) if resume_id else None,
                    interview_date=interview_date,
                    user_id=user_id
                )
                db.session.add(new_job)
                db.session.commit()
                flash("Job created successfully!", "success")
                return redirect(url_for("jobs.jobs_list"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error creating job: {e}", "error")
        else:
            flash("Job title is required.", "error")
            
    # Fetch Resumes for dropdown
    resumes = Resume.query.filter_by(user_id=user_id).all()
    return render_template("jobs/create.html", resumes=resumes)

@jobs_bp.route("/jobs/<int:job_id>")
def jobs_detail(job_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    job = Job.query.get_or_404(job_id)
    if job.user_id != session["user_id"]:
        flash("Access denied.", "error")
        return redirect(url_for("jobs.jobs_list"))
        
    resume = Resume.query.get(job.resume_id) if job.resume_id else None
        
    return render_template("jobs/detail.html", job=job, resume=resume)

@jobs_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    job = Job.query.get_or_404(job_id)
    if job.user_id != session["user_id"]:
        flash("Access denied.", "error")
        return redirect(url_for("jobs.jobs_list"))
        
    try:
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting job: {e}", "error")
        
    return redirect(url_for("jobs.jobs_list"))

@jobs_bp.route("/api/extract-job", methods=["POST"])
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
    extracted_data = extract_job_info(html_content, analyzer)
    
    if extracted_data:
        return jsonify(extracted_data)
    else:
        return jsonify({"error": "Failed to extract job info."}), 500

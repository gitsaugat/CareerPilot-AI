from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Job, Resume
from services import analyzer
import os
from pathlib import Path

tools_bp = Blueprint('tools', __name__)

@tools_bp.route("/ranking/select", methods=["GET", "POST"])
def ranking_select():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        job_id = request.form.get("job_id")
        resume_ids = request.form.getlist("resume_ids")
        
        if not job_id or not resume_ids:
            flash("Please select a job and at least one candidate.", "error")
            return redirect(url_for("tools.ranking_select"))
            
        return redirect(url_for("tools.ranking_process", job_id=job_id, resume_ids=",".join(resume_ids)))

    # GET: Show Selection Form
    jobs = Job.query.filter_by(user_id=session["user_id"]).order_by(Job.created_at.desc()).all()
    resumes = Resume.query.filter_by(user_id=session["user_id"]).order_by(Resume.created_at.desc()).all()
    return render_template("ranking/select.html", jobs=jobs, resumes=resumes)

@tools_bp.route("/ranking/process")
def ranking_process():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    job_id = request.args.get("job_id")
    resume_ids_str = request.args.get("resume_ids")
    
    if not job_id or not resume_ids_str:
        return redirect(url_for("tools.ranking_select"))
        
    job = Job.query.get_or_404(job_id)
    resume_ids = [int(id) for id in resume_ids_str.split(",")]

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

@tools_bp.route("/compare/<int:resume_id>", methods=["GET", "POST"])
def compare_resume(resume_id: int):
    if "user_id" not in session:
        flash("Please log in to compare resumes.", "error")
        return redirect(url_for("auth.login"))

    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session["user_id"]:
        flash("You are not allowed to view this resume.", "error")
        return redirect(url_for("dashboard.dashboard"))

    can_preview_pdf = False
    viewer_url = None
    if os.path.exists(resume.resume_file_path):
        ext = Path(resume.resume_file_path).suffix.lower()
        if ext == ".pdf":
            can_preview_pdf = True
            viewer_url = url_for("resumes.view_resume_inline", resume_id=resume.id)

    job_description_html = ""
    analysis_results = None

    if request.method == "POST":
        job_description_html = request.form.get("job_description", "")
        
        # Real AI Analysis
        if job_description_html.replace("<p>", "").replace("</p>", "").strip():
            try:
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

@tools_bp.route("/cover-letter", methods=["GET", "POST"])
def cover_letter():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
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

@tools_bp.route("/interview-prep", methods=["GET", "POST"])
def interview_prep():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
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

@tools_bp.route("/networking", methods=["GET", "POST"])
def networking():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    user_id = session["user_id"]
    resumes = Resume.query.filter_by(user_id=user_id).all()
    jobs = Job.query.filter_by(user_id=user_id).all()
    
    generated_content = None
    selected_resume_id = None
    job_description = ""
    
    if request.method == "POST":
        resume_id = request.form.get("resume_id")
        job_description = request.form.get("job_description")
        
        if resume_id and job_description:
            selected_resume_id = int(resume_id)
            resume = Resume.query.get(resume_id)
            if resume and resume.user_id == user_id:
                # Generate Networking Messages
                generated_content = analyzer.generate_networking_messages(resume.resume_file_path, job_description)
                if not generated_content:
                    flash("Failed to generate networking messages. Please try again.", "error")
            else:
                flash("Invalid resume selected.", "error")
        else:
            flash("Please select a resume and provide a job description.", "error")
            
    return render_template("tools/networking.html", resumes=resumes, jobs=jobs, generated_content=generated_content, selected_resume_id=selected_resume_id, job_description=job_description)

@tools_bp.route("/linkedin", methods=["GET", "POST"])
def linkedin():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    user_id = session["user_id"]
    resumes = Resume.query.filter_by(user_id=user_id).all()
    jobs = Job.query.filter_by(user_id=user_id).all()
    
    generated_content = None
    selected_resume_id = None
    job_description = ""
    
    if request.method == "POST":
        resume_id = request.form.get("resume_id")
        job_description = request.form.get("job_description")
        
        if resume_id and job_description:
            selected_resume_id = int(resume_id)
            resume = Resume.query.get(resume_id)
            if resume and resume.user_id == user_id:
                # Generate LinkedIn Optimization
                generated_content = analyzer.optimize_linkedin(resume.resume_file_path, job_description)
                if not generated_content:
                    flash("Failed to generate LinkedIn optimization. Please try again.", "error")
            else:
                flash("Invalid resume selected.", "error")
        else:
            flash("Please select a resume and provide a job description.", "error")
            
    return render_template("tools/linkedin.html", resumes=resumes, jobs=jobs, generated_content=generated_content, selected_resume_id=selected_resume_id, job_description=job_description)

@tools_bp.route("/negotiation", methods=["GET", "POST"])
def negotiation():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    generated_content = None
    job_title = ""
    offer_details = ""
    
    if request.method == "POST":
        job_title = request.form.get("job_title")
        offer_details = request.form.get("offer_details")
        
        if job_title:
            # Generate Negotiation Scripts
            generated_content = analyzer.generate_negotiation_scripts(job_title, offer_details)
            if not generated_content:
                flash("Failed to generate negotiation scripts. Please try again.", "error")
        else:
            flash("Please enter a job title.", "error")
            
    return render_template("tools/negotiation.html", generated_content=generated_content, job_title=job_title, offer_details=offer_details)

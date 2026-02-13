from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User
from extensions import db
import ollama

settings_bp = Blueprint('settings', __name__)

@settings_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])
    
    # Fetch available models from Ollama
    try:
        models_info = ollama.list()
        # Extract model names. The structure of models_info might vary, usually it's {'models': [{'name': '...'}, ...]}
        available_models = [m['name'] for m in models_info.get('models', [])]
    except Exception as e:
        available_models = ["gpt-oss:120b-cloud", "llama3", "mistral"] # Fallback
        print(f"Error fetching models: {e}")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            selected_model = request.form.get("selected_model")
            if selected_model:
                user.selected_model = selected_model
                db.session.commit()
                flash("Preferences updated successfully.", "success")
        
        elif action == "change_password":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not user.check_password(current_password):
                flash("Incorrect current password.", "error")
            elif new_password != confirm_password:
                flash("New passwords do not match.", "error")
            elif len(new_password) < 8:
                flash("Password must be at least 8 characters.", "error")
            else:
                user.set_password(new_password)
                db.session.commit()
                flash("Password changed successfully.", "success")

        return redirect(url_for("settings.settings"))

    return render_template("settings.html", user=user, available_models=available_models)

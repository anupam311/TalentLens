from flask import Blueprint, jsonify, g
from app.extensions import db
from app.models import Application, Job, Candidate, AIAnalysis
from app.services.auth_service import login_required
from app.services.ai_service import analyze_candidate

ai_analysis_bp = Blueprint("ai_analysis", __name__, url_prefix="/api/applications")

@ai_analysis_bp.route("/<application_id>/analyze", methods=["POST"])
@login_required
def create_analysis(application_id):
    application = Application.query.join(Job).filter(
        Application.id == application_id,
        Job.organization_id == g.current_user.organization_id,
    ).first()

    if not application:
        return jsonify({"errors": {"_general": ["Application not found."]}}), 404

    job = Job.query.get(application.job_id)
    candidate = Candidate.query.get(application.candidate_id)

    if not candidate.resume_text:
        return jsonify({"errors": {"_general": ["This candidate has no parsed resume text to analyze."]}}), 400

    try:
        result = analyze_candidate(
            job_description=job.description,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            resume_text=candidate.resume_text,
        )
    except RuntimeError as e:
        return jsonify({"errors": {"_general": [str(e)]}}), 502
    except ValueError as e:
        return jsonify({"errors": {"_general": [f"AI response could not be validated: {e}"]}}), 502

    analysis = AIAnalysis(
        application_id=application.id,
        overall_match_score=result["overall_match_score"],
        technical_skills_score=result["technical_skills_score"],
        experience_score=result["experience_score"],
        culture_score=result["culture_score"],
        strengths=result["strengths"],
        missing_skilld=result["missing_skills"],
        suggested_questions=result["suggested_questions"],
        model_used=result["model_used"],
    )
    db.session.add(analysis)
    db.session.commit()

    return jsonify(analysis.to_dict()), 201

@ai_analysis_bp.route("/<application_id>/analysis", methods=["GET"])
@login_required
def list_analysis(application_id):
    application = Application.query.join(Job).filter(
        Application.id == application_id,
        Job.organization_id == g.current_user.organization_id,
    ).first()

    if not application:
        return jsonify({"errors": {"_general": ["Application not found."]}}), 404

    analysis = AIAnalysis.query.filter_by(application_id=application.id) \
                                .order_by(AIAnalysis.created_at.desc()) \
                                .all()

    return jsonify({"analysis": [a.to_dict() for a in analysis]}), 200
from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from app.extensions import db
from app.models import Application, Candidate, Job
from app.schemas.application_schemas import CreateApplicationSchema, UpdateApplicationStatusSchema
from app.services.auth_service import login_required

applications_bp = Blueprint("applications", __name__, url_prefix="/api/applications")
create_application_schema = CreateApplicationSchema()
update_status_schema = UpdateApplicationStatusSchema()


@applications_bp.route("", methods=["POST"])
@login_required
def create_application():
    try:
        data = create_application_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Crucial check: both the candidate AND the job must belong to this org.
    # Without this, someone could link a candidate from Org A to a job in Org B.
    candidate = Candidate.query.filter_by(
        id=data["candidate_id"],
        organization_id=g.current_user.organization_id,
    ).first()
    job = Job.query.filter_by(
        id=data["job_id"],
        organization_id=g.current_user.organization_id,
    ).first()

    if not candidate or not job:
        return jsonify({"errors": {"_general": ["Candidate or job not found."]}}), 404

    existing = Application.query.filter_by(
        candidate_id=candidate.id,
        job_id=job.id,
    ).first()
    if existing:
        return jsonify({"errors": {"_general": ["This candidate has already applied to this job."]}}), 409

    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        source=data.get("source", "manual"),
        status="new",
    )
    db.session.add(application)
    db.session.commit()

    return jsonify(application.to_dict()), 201

@applications_bp.route("", methods=["GET"])
@login_required
def list_applications():
    job_id = request.args.get("job_id", default=None, type=str)
    candidate_id = request.args.get("candidate_id", default=None, type=str)
    status_filter = request.args.get("status", default=None, type=str)

    # Join through Job/Candidate to enforce org-scoping, since Application itself
    # has no organization_id column of its own — it inherits scoping through its parents.
    query = Application.query.join(Job).filter(Job.organization_id == g.current_user.organization_id)

    if job_id:
        query = query.filter(Application.job_id == job_id)
    if candidate_id:
        query = query.filter(Application.candidate_id == candidate_id)
    if status_filter:
        query = query.filter(Application.status == status_filter)

    applications = query.order_by(Application.applied_at.desc()).all()

    return jsonify({"applications": [a.to_dict() for a in applications]}), 200

@applications_bp.route("/<application_id>", methods=["PATCH"])
@login_required
def update_application_status(application_id):
    application = Application.query.join(Job) \
        .filter(
            Application.id == application_id,
            Job.organization_id == g.current_user.organization_id,
        ).first()

    if not application:
        return jsonify({"errors": {"_general": ["Application not found."]}}), 404

    try:
        data = update_status_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    application.status = data["status"]
    db.session.commit()

    return jsonify(application.to_dict()), 200

@applications_bp.route("/<application_id>", methods=["GET"])
@login_required
def get_application(application_id):
    application = Application.query.join(Job) \
        .filter(
            Application.id == application_id,
            Job.organization_id == g.current_user.organization_id,
        ).first()

    if not application:
        return jsonify({"errors": {"_general": ["Application not found."]}}), 404

    return jsonify(application.to_dict()), 200


@applications_bp.route("/<application_id>", methods=["DELETE"])
@login_required
def delete_application(application_id):
    application = Application.query.join(Job) \
        .filter(
            Application.id == application_id,
            Job.organization_id == g.current_user.organization_id,
        ).first()

    if not application:
        return jsonify({"errors": {"_general": ["Application not found."]}}), 404

    db.session.delete(application)
    db.session.commit()

    return "", 204
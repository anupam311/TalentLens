from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from app.extensions import db
from app.models import Job
from app.schemas.job_schemas import CreateJobSchema
from app.services.auth_service import login_required

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")
create_job_schema = CreateJobSchema()

# --------------------
# Create Jobs
# --------------------

@jobs_bp.route("", methods=["POST"])
@login_required
def create_job():
    try:
        data = create_job_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    job = Job(
        organization_id=g.current_user.organization_id,
        created_by=g.current_user.id,
        status="draft",
        **data,
    )
    db.session.add(job)
    db.session.commit()

    return jsonify(job.to_dict()), 201

# --------------------
# List Jobs
# --------------------

@jobs_bp.route("", methods=["GET"])
@login_required
def list_jobs():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=25, type=int)
    per_page = min(per_page, 100)
    search = request.args.get("search", default=None, type=str)
    status_filter = request.args.get("status", default=None, type=str)

    query = Job.query.filter_by(organization_id=g.current_user.organization_id)

    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))

    if status_filter:
        query = query.filter_by(status=status_filter)

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()) \
                .offset((page - 1) * per_page) \
                .limit(per_page) \
                .all()

    return jsonify({
        "jobs": [job.to_dict() for job in jobs],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        },
    }), 200

@jobs_bp.route("/<job_id>", methods=["GET"])
@login_required
def get_job(job_id):
    job = Job.query.filter_by(
        id=job_id,
        organization_id=g.current_user.organization_id,
    ).first()

    if not job:
        return jsonify({"errors": {"_general": ["Job not found."]}}), 404

    return jsonify(job.to_dict()), 200

# --------------------
# Update Jobs
# --------------------

from app.schemas.job_schemas import CreateJobSchema, UpdateJobSchema

update_job_schema = UpdateJobSchema()

@jobs_bp.route("/<job_id>", methods=["PATCH"])
@login_required
def update_job(job_id):
    job = Job.query.filter_by(
        id=job_id,
        organization_id=g.current_user.organization_id,
    ).first()

    if not job:
        return jsonify({"errors": {"_general": ["Job not found."]}}), 404

    try:
        data = update_job_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for field, value in data.items():
        setattr(job, field, value)

    db.session.commit()
    return jsonify(job.to_dict()), 200

# --------------------
# Delete Jobs
# --------------------

@jobs_bp.route("/<job_id>", methods=["DELETE"])
@login_required
def delete_job(job_id):
    job = Job.query.filter_by(
        id=job_id,
        organization_id=g.current_user.organization_id,
    ).first()

    if not job:
        return jsonify({"errors": {"_general": ["Job not found."]}}), 404

    db.session.delete(job)
    db.session.commit()

    return "", 204
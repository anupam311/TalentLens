from flask import Blueprint, jsonify, g, request
from datetime import datetime, timezone
from app.extensions import db
from app.models import Job, JobDistribution
from app.services.auth_service import login_required
from app.services.distribution_adapters import ADAPTERS

distribution_bp = Blueprint("distribution", __name__, url_prefix="/api/jobs")

@distribution_bp.route("/<job_id>/publish", methods=["POST"])
@login_required
def publish_job(job_id):
    channel = request.get_json().get("channel") if request.get_json(silent=True) else None

    if channel not in ADAPTERS:
        return jsonify({"errors": {"channel": [f"Unsupported channel. Choose from: {list(ADAPTERS.keys())}"]}}), 400

    job = Job.query.filter_by(id=job_id, organization_id=g.current_user.organization_id).first()
    if not job:
        return jsonify({"errors": {"_general": ["Job not found."]}}), 404

    existing = JobDistribution.query.filter_by(job_id=job.id, channel=channel).first()
    if existing and existing.status == "published":
        return jsnoify({"errors": {"_general": [f"This job is already published to {channel}."]}}), 409

    distribution = existing or JobDistribution(job_id=job.id, channel=channel)

    try:
        external_url = ADAPTERS[channel].publish(job)
        distribution.status = "published"
        distribution.external_url = external_url
        distribution.published_at = datetime.now(timezone.utc)
    except Exception as e:
        distribution.status = "failed"
        db.session.add(distribution)
        db.session.commit()
        return jsonify({"errors": {"_general": [f"Publishing failed: {e}"]}}), 502

    db.session.add(distribution)
    db.session.commit()

    return jsonify(distribution.to_dict()), 201

@distribution_bp.route("/<job_id>/distributions", methods=["GET"])
@login_required
def list_distributions(job_id):
    job = Job.query.filter_by(id=job_id, organization_id=g.current_user.organization_id).first()
    if not job:
        return jsonify({"errors": {"_general": ["Job not found."]}}), 404
    
    distributions = JobDistribution.query.filter_by(job_id=job.id).all()
    return jsonify({"distributions": [d.to_dict() for d in distributions]}), 200
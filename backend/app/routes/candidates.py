from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from app.extensions import db
from app.models import Candidate
from app.schemas.candidate_schemas import CreateCandidateSchema, UpdateCandidateSchema
from app.services.auth_service import login_required
from app.services.upload_service import save_resume_file
from app.services.resume_parser import extract_text_from_pdf

candidates_bp = Blueprint("candidates", __name__, url_prefix="/api/candidates")
create_candidate_schema = CreateCandidateSchema()
update_candidate_schema = UpdateCandidateSchema()

@candidates_bp.route("", methods=["POST"])
@login_required
def create_candidate():
    # Text fields come from request.form (not request.get_json()) since this is multipart
    try:
        data = create_candidate_schema.load(request.form.to_dict())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Check for duplicate email within this org before touching the file at all
    existing = Candidate.query.filter_by(
        organization_id=g.current_user.organization_id,
        email=data["email"],
    ).first()
    if existing:
        return jsonify({"errors": {"email": ["A candidate with this email already exists."]}}), 409

    resume_file_path = None
    resume_text = None
    resume_file = request.files.get("resume")
    if resume_file and resume_file.filename:
        try:
            resume_file_path = save_resume_file(resume_file)
        except ValueError as e:
            return jsonify({"errors": {"resume": [str(e)]}}), 400

        if resume_file_path.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file_path)

    candidate = Candidate(
        organization_id=g.current_user.organization_id,
        resume_file_path=resume_file_path,
        resume_text=resume_text,
        **data,
    )
    db.session.add(candidate)
    db.session.commit()

    return jsonify(candidate.to_dict()), 201

@candidates_bp.route("", methods=["GET"])
@login_required
def list_candidates():
    page = request.args.get("page", default=1, type=int)
    per_page = min(request.args.get("per_page", default=25, type=int), 100)
    search = request.args.get("search", default=None, type=str)

    query = Candidate.query.filter_by(organization_id=g.current_user.organization_id)

    if search:
        query = query.filter(
            db.or_(
                Candidate.first_name.ilike(f"%{search}%"),
                Candidate.last_name.ilike(f"%{search}%"),
                Candidate.email.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    candidates = query.order_by(Candidate.created_at.desc()) \
                       .offset((page - 1) * per_page) \
                       .limit(per_page) \
                       .all()

    return jsonify({
        "candidates": [c.to_dict() for c in candidates],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        },
    }), 200

@candidates_bp.route("/<candidate_id>", methods=["GET"])
@login_required
def get_candidate(candidate_id):
    candidate = Candidate.query.filter_by(
        id=candidate_id,
        organization_id=g.current_user.organization_id,
    ).first()

    if not candidate:
        return jsonify({"errors": {"_general": ["Candidate not found."]}}), 404

    return jsonify(candidate.to_dict()), 200


@candidates_bp.route("/<candidate_id>", methods=["PATCH"])
@login_required
def update_candidate(candidate_id):
    candidate = Candidate.query.filter_by(
        id=candidate_id,
        organization_id=g.current_user.organization_id,
    ).first()

    if not candidate:
        return jsonify({"errors": {"_general": ["Candidate not found."]}}), 404

    try:
        data = update_candidate_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # If email is being changed, re-check the org-scoped uniqueness manually
    # (the DB constraint would catch it too, but checking here gives a clean 409
    # instead of an ugly database IntegrityError bubbling up)
    if "email" in data and data["email"] != candidate.email:
        existing = Candidate.query.filter_by(
            organization_id=g.current_user.organization_id,
            email=data["email"],
        ).first()
        if existing:
            return jsonify({"errors": {"email": ["A candidate with this email already exists."]}}), 409

    for field, value in data.items():
        setattr(candidate, field, value)

    db.session.commit()
    return jsonify(candidate.to_dict()), 200


@candidates_bp.route("/<candidate_id>", methods=["DELETE"])
@login_required
def delete_candidate(candidate_id):
    candidate = Candidate.query.filter_by(
        id=candidate_id,
        organization_id=g.current_user.organization_id,
    ).first()

    if not candidate:
        return jsonify({"errors": {"_general": ["Candidate not found."]}}), 404

    db.session.delete(candidate)
    db.session.commit()

    return "", 204
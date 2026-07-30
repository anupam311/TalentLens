import uuid
from datetime import datetime, timezone
from app.extensions import db

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(255))
    employment_type = db.Column(db.String(20), nullable=False, default="full-time")
    years_experience = db.Column(db.String(50))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    description = db.Column(db.Text)
    required_skills = db.Column(db.ARRAY(db.String), default=list)
    preferred_skills = db.Column(db.ARRAY(db.String), default=list)
    benefits = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="draft")
    application_deadline = db.Column(db.Date)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.CheckConstraint(
            "employment_type IN ('full-time', 'part-time', 'contract', 'internship')",
            name="check_job_employment_type",
        ),
        db.CheckConstraint(
            "status IN ('draft', 'active', 'closed')",
            name="check_job_status",
        )
    )

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "created_at": self.created_at,
            "title": self.title,
            "department": self.department,
            "location": self.location,
            "employment_type": self.employment_type,
            "years_experience": self.years_experience,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "description": self.description,
            "required_skills": self.required_skills or [],
            "preferred_skills": self.preferred_skills or [],
            "benefits": self.benefits,
            "status": self.status,
            "application_deadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
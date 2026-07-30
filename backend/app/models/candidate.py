import uuid
from datetime import datetime, timezone
from app.extensions import db

class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    location = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(500))
    other_url = db.Column(db.String(500))
    resume_file_path = db.Column(db.String(500))
    resume_text = db.Column(db.Text)
    skills = db.Column(db.ARRAY(db.String), default=list)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("organization_id", "email", name="uq_candidate_org_email"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin_url": self.linkedin_url,
            "other_url": self.other_url,
            "resume_file_path": self.resume_file_path,
            "resume_text": self.resume_text,
            "skills": self.skills or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
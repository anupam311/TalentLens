import uuid
from datetime import datetime, timezone
from app.extensions import db

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = db.Column(db.String(36), db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="new")
    source = db.Column(db.String(50), default="manual")
    applied_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint("candidate_id", "job_id", name="uq_application_candidate_job"),
        db.CheckConstraint(
            "status IN ('new','screening','interview','offer','hired','rejected')",
            name="check_application_status",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "status": self.status,
            "source": self.source,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
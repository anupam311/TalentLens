import uuid
from datetime import datetime, timezone
from app.extensions import db

class JobDistribution(db.Model):
    __tablename__ = "job_distributions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    external_url = db.Column(db.String(500))
    published_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("job_id", "channel", name="uq_job_distribution_job_channel"),
        db.CheckConstraint("status IN ('pending','published','failed')", name="check_distribution_status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "channel": self.channel,
            "status": self.status,
            "external_url": self.external_url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
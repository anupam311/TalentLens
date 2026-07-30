import uuid
from datetime import datetime, timezone
from app.extensions import db

class RecruiterNote(db.Model):
    __tablename__ = "recruiter_notes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = db.Column(db.String(36), db.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
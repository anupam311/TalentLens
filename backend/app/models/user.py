import uuid
from datetime import datetime, timezone
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="recruiter")
    avatar_url = db.Column(db.String(500))
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    organization = db.relationship("Organization", back_populates="users")

    __table_args__ = (db.CheckConstraint("role IN ('admin', 'recruiter', 'viewer')", name="check_user_role"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "avatar_url": self.avatar_url,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

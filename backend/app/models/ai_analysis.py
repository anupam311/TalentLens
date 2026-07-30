import uuid
from datetime import datetime, timezone
from app.extensions import db

class AIAnalysis(db.Model):
    __tablename__ = "ai_analyses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = db.Column(db.String(36), db.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    overall_match_score = db.Column(db.SmallInteger)
    technical_skills_score = db.Column(db.SmallInteger)
    experience_score = db.Column(db.SmallInteger)
    culture_score = db.Column(db.SmallInteger)
    strengths = db.Column(db.JSON, default=list)
    missing_skills = db.Column(db.JSON, default=list)
    suggested_questions = db.Column(db.JSON, default=list)
    model_used = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint("overall_match_score BETWEEN 0 AND 100", name="check_overall_score_range"),
        db.CheckConstraint("technical_skills_score BETWEEN 0 AND 100", name="check_tech_score_range"),
        db.CheckConstraint("experience_score BETWEEN 0 AND 100", name="check_experience_score_range"),
        db.CheckConstraint("culture_score BETWEEN 0 AND 100", name="check_culture_score_range"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "overall_match_score": self.overall_match_score,
            "technical_skills_score": self.technical_skills_score,
            "experience_score": self.experience_score,
            "culture_score": self.culture_score,
            "strengths": self.strengths or [],
            "missing_skills": self.missing_skills or [],
            "suggested_questions": self.suggested_questions or [],
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
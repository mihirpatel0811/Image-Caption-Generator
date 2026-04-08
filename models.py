from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class ImageCaption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    descriptive_caption = db.Column(db.Text, nullable=True)
    social_caption = db.Column(db.Text, nullable=True)
    alt_text = db.Column(db.Text, nullable=True)
    platform = db.Column(db.String(50), default="general")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "descriptive_caption": self.descriptive_caption,
            "social_caption": self.social_caption,
            "alt_text": self.alt_text,
            "platform": self.platform,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class SavedCaption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption_text = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(50), default="general")
    caption_type = db.Column(db.String(50), default="promotional")
    tone = db.Column(db.String(50), default="casual")
    description = db.Column(db.Text, nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "caption_text": self.caption_text,
            "platform": self.platform,
            "caption_type": self.caption_type,
            "tone": self.tone,
            "description": self.description,
            "is_favorite": self.is_favorite,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

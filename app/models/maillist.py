import uuid

from app.extensions import db


class MailList(db.Model):
    __tablename__ = 'maillist'

    id = db.Column(db.String(512), primary_key=True, default=lambda: str(uuid.uuid4()))
    mail = db.Column(db.String(512), unique=False, nullable=True)

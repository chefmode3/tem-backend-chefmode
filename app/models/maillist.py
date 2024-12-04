import uuid

from app.extensions import db


class MailList(db.Model):
    __tablename__ = 'maillist'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    mail = db.Column(db.String(255), unique=False, nullable=True)

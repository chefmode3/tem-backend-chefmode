from app.extensions import db
from datetime import datetime


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),  nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    activate = db.Column(db.Boolean, default=False)
    google_token = db.Column(db.String(255), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), unique=True, nullable=True)
    # subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def __init__(
            self,
            username,
          email,
          activate = False,
          password=None,
          google_token=None,
          google_id=None
    ):
        self.username = username
        self.email = email
        self.password = password
        self.activate = activate
        self.google_id = google_id
        self.google_token = google_token
        # self.subscription_id = subscription_id

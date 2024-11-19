from app.extensions import db


class TaskResult(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    servings = db.Column(db.Integer, nullable=True)
    preparation_time = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

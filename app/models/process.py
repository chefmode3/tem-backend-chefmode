import uuid

from app.extensions import db

class Process(db.Model):
    __tablename__ = 'processes'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    step_number = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.String(255), db.ForeignKey('recipes.id'), nullable=False)

    # Relationships
    # recipe = db.relationship('Recipe', back_populates='processes')

from app.extensions import db

class Process(db.Model):
    __tablename__ = 'processes'

    id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    # Relationships
    recipe = db.relationship('Recipe', back_populates='processes')

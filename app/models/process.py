from app.extensions import db


class Process(db.Model):
    __tablename__ = 'process'
    id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=True)
    instructions = db.Column(db.Text, nullable=True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

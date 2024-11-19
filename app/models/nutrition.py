from app.extensions import db

class Nutrition(db.Model):
    __tablename__ = 'nutritions'

    id = db.Column(db.Integer, primary_key=True)
    calories = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    fiber = db.Column(db.Float, nullable=False)
    proteins = db.Column(db.Float, nullable=False)
    sodium = db.Column(db.Float, nullable=False)
    sugar = db.Column(db.Float, nullable=False)

    ingredient = db.relationship('Ingredient', back_populates='nutrition', uselist=False)

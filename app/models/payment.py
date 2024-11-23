import uuid

from datetime import datetime

from app.extensions import db

from sqlalchemy_fsm import FSMField, transition

from app.services.entities import MembershipStates


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50))

    # Relationships
    user_id = db.Column(db.String(255), db.ForeignKey('user.id'), nullable=False)


class Subscription(db.Model):
    __tablename__ ='subscription'
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(50), nullable=False, unique=True)
    expires_in_days = db.Column(db.Integer, default=0)
    max_receipts = db.Column(db.Integer, default=5)


class SubscriptionMembership(db.Model):
    __tablename ='subscriptionmembership'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.ForeignKey('user.id'), nullable=False)
    subscription= db.Column(db.ForeignKey('subscription.id'), nullable=False)

    state = db.Column(FSMField, default=MembershipStates.NEW.value, nullable=False)
    store = db.Column(db.String(50), nullable=True)

    stripe_subscription_id = db.Column(db.String(50), nullable=True)
    purchase_date = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    expired_at = db.Column(db.DateTime, nullable=True)
    payment_frequency = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    @transition(
        field='state',
        source="*",
        target=MembershipStates.PAID.value
    )
    def pay(self, subscription_data):
        pass

    @transition(
        field='state',
        source=[MembershipStates.NEW.value, MembershipStates.PAID.value],
        target=MembershipStates.CANCELLED.value
     )
    def cancel(self):
        pass

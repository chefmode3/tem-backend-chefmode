import uuid

from datetime import datetime

from app.extensions import db

from app.services.entities import MembershipStates


def get_paid_plan(product_id=None):
    if product_id:
        subscription_plan = db.query(Subscription).filter(product_id == product_id).first()
        return subscription_plan
    return None


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(255))

    # Relationships
    user_id = db.Column(db.String(255), db.ForeignKey('user.id'), nullable=False)


class Subscription(db.Model):
    __tablename__ ='subscription'
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(255), nullable=False, unique=True)
    expires_in_days = db.Column(db.Integer, default=0)
    max_receipts = db.Column(db.Integer, default=0)
    price_id = db.Column(db.String(255), nullable=False, unique=True)


class SubscriptionMembership(db.Model):
    __tablename ='subscriptionmembership'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    subscription= db.Column(db.ForeignKey('subscription.id'), nullable=False)

    state = db.Column(db.String(255), default=MembershipStates.NEW.value, nullable=False)

    subscription_id = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.String(255), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    latest_invoice = db.Column(db.Text(), nullable=True)
    purchase_date = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    expired_at = db.Column(db.DateTime, nullable=True)
    payment_frequency = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def from_dict(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)
        return self


class StripeUserCheckoutSession(db.Model):
    __tablename = 'stripeusercheckoutsession'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(255), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    subscription_id = db.Column(db.String(255), nullable=True)
    price_id = db.Column(db.String(255), nullable=True)

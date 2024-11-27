from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

import stripe
from sqlalchemy.orm import Session
from stripe import StripeError

from app.extensions import db
from app.exceptions import SubscriptionException
from app.models import SubscriptionMembership, Subscription
from app.services.entities import SubscriptionEntity


@dataclass
class UserSubscriptionService:
    user: Any
    stripe_api_key: str

    def get_get_checkout_session(self, checkout_session_id: str) -> Optional[str]:

        try:
            stripe.api_key = self.stripe_api_key
            subscription =stripe.checkout.Session.retrieve(checkout_session_id)
            if subscription.get("status") == "complete" and subscription.get("payment_status") == "paid":
                return subscription.get("subscription")
        except StripeError as e:
            raise SubscriptionException(str(e), 400)

    def get_subscriptions(self, subscription_id) -> Optional[SubscriptionEntity]:

        try:
            stripe.api_key = self.stripe_api_key
            subscription = stripe.Subscription.retrieve(subscription_id)
            subscription_entity = SubscriptionEntity(
                subscription_id=subscription.get("id"),
                product_id=subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("product", ""),
                invoice_id=subscription.get("latest_invoice", {}),
                customer_id=subscription.get("customer", ""),
                price=subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("unit_amount", ""),
                currency=subscription.get('currency', "usd"),
                payment_frequency=subscription.get(
                    "items", {}
                ).get("data", [{}])[0].get("price", {}).get("recurring", {}).get("interval", ""),
                purchase_date=(
                    datetime.fromtimestamp(subscription.get('current_period_start'))
                    if subscription.get('current_period_start') else None
                ),
                payment_status=subscription.get('payment_status', ""),
                expires_at=(
                    datetime.fromtimestamp(subscription.get("current_period_end"))
                    if subscription.get("current_period_start") else None
                ),
            )
            return subscription_entity
        except StripeError as e:
            raise SubscriptionException(str(e), 400)

    def subscribe_user(self, subscription_id: str):
        subscription_data = self.get_subscriptions(subscription_id)
        if not subscription_data:
            raise SubscriptionException("Subscription does not exist", 400)
        s_membership = SubscriptionMembership.query.filter_by(user_id=self.user.id).first()
        if not s_membership:
            subscription = Subscription.query.filter_by(product_id=subscription_data.product_id).first()
            s_membership = SubscriptionMembership(
                user=self.user,
                subscription=subscription
            )
        s_membership.pay(subscription_data)
        db.session.add(s_membership)
        db.commit()
        return s_membership

    def cancel_user_subscription(self, db: Session):
        try:
            ...
        except StripeError as e:
            raise SubscriptionException(str(e), 400)

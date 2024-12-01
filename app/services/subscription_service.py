import logging

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

import stripe
from stripe import StripeError

from app.extensions import db
from app.exceptions import SubscriptionException
from app.models import SubscriptionMembership, Subscription
from app.models.payment import StripeUserCheckoutSession
from app.services.entities import SubscriptionEntity, CheckoutCreationEntity

logger = logging.getLogger(__name__)


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
                payment_status=subscription.get('status', ""),
                expires_at=(
                    datetime.fromtimestamp(subscription.get("current_period_end"))
                    if subscription.get("current_period_start") else None
                ),
                canceled_at=(
                    datetime.fromtimestamp(subscription.get("canceled_at"))
                    if subscription.get("canceled_at") else None
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
                user_id=self.user.id,
                subscription=subscription.id,
                state=subscription_data.payment_status,
                subscription_id=subscription_data.subscription_id,
                product_id=subscription_data.product_id,
                latest_invoice=subscription_data.invoice_id,
                customer_id=subscription_data.customer_id,
                purchase_date=subscription_data.purchase_date,
                expired_at=subscription_data.expires_at,
                payment_frequency=subscription_data.payment_frequency,
                price=subscription_data.price,
                cancelled_at=subscription_data.canceled_at,
            )
            db.session.add(s_membership)
            db.session.commit()
        else:
            s_membership.subscription_id=subscription_data.subscription_id
            s_membership.state=subscription_data.payment_status
            s_membership.payment_frequency=subscription_data.payment_frequency
            s_membership.price = subscription_data.price
            s_membership.latest_invoice=subscription_data.invoice_id
            db.session.commit()
        return s_membership

    def create_checkout_session(self, checkout_entity: CheckoutCreationEntity) -> dict:
        try:
            stripe.api_key = self.stripe_api_key
            response = stripe.checkout.Session.create(
                success_url=checkout_entity.redirect_url,
                mode=checkout_entity.mode,
                ui_mode=checkout_entity.ui_mode,
                line_items=[
                    {
                        "price": checkout_entity.price_id
                    }
                ]
            )
            stripe_user = StripeUserCheckoutSession(
                user_id=self.user.id,
                session_id=response.get("id", ""),
                price_id=checkout_entity.price_id
            )
            db.session.add(stripe_user)
            db.session.commit()
            return response.get("client_secrete")
        except StripeError as e:
            raise SubscriptionException(str(e), 400)


@dataclass
class SubscriptionWebhookService:
    data: dict
    event_type: str


    def execute(self):
        session_id = self.data.get("id")
        subscription_id = self.data.get("subscription")
        customer_id = self.data.get("customer")
        price = self.data.get("items", {}).get("data", [{}])[0].get("price", {}).get("unit_amount", ""),
        status = self.data.get("status")
        purchase_date = (
            datetime.fromtimestamp(self.data.get("period_start"))
            if self.data.get("period_start") else None
        )
        expired_at = (
            datetime.fromtimestamp(self.data.get("period_end"))
            if self.data.get("period_end") else None
        )
        payment_frequency = self.data.get("data", [{}])[0].get("price", {}).get("recurring", {}).get("interval", ""),
        cancelled_at = (
            datetime.fromtimestamp(self.data.get("canceled_at"))
            if self.data.get("canceled_at") else None
        )

        stripe_user = StripeUserCheckoutSession.query.filter_by(session_id=session_id).first()
        if self.event_type == "checkout.session.completed":
            customer_id = self.data.get("customer")
            subscription_id = self.data.get("subscription")
            if stripe_user:
                stripe_user.customer_id = customer_id
                stripe_user.subscription_id = subscription_id
                db.session.commit()
        elif self.event_type == "payment_intent.succeeded":
            s_membership = SubscriptionMembership.query.filter_by(customer_id=customer_id).first()

            if not s_membership and stripe_user:
                subscription = Subscription.query.filter_by(price_id=stripe_user.price_id)
                if not subscription:
                    raise SubscriptionException("Internal Server Error", 400)
                s_membership = SubscriptionMembership(
                    subscription=subscription.id
                )

            s_membership.price = price
            s_membership.customer_id = customer_id
            s_membership.subscription_id = subscription_id
            s_membership.state = status
            s_membership.purchase_date = purchase_date
            s_membership.expired_at = expired_at
            s_membership.payment_frequency = payment_frequency
            db.session.commit()
            logger.info(f"PaymentIntent succeeded")
        elif self.event_type in  ["invoice.payment_failed", "customer.subscription.deleted"]:
            s_membership = SubscriptionMembership.query.filter_by(customer_id=customer_id).first()
            if not s_membership:
                raise SubscriptionException("Internal Server Error", 400)
            s_membership.state = status
            s_membership.cancelled_at = cancelled_at
            db.session.commit()
            logger.info(f"Invoice payment failed")
        else:
            logger.info(f"Unhandled event type")

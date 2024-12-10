import logging
import os

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

import stripe
from sqlalchemy import or_
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

    def create_checkout_session(self, checkout_entity: CheckoutCreationEntity) -> str:
        try:
            stripe.api_key = self.stripe_api_key
            response = stripe.checkout.Session.create(
                return_url=checkout_entity.redirect_url,
                mode=checkout_entity.mode,
                ui_mode=checkout_entity.ui_mode,
                line_items=[
                    {
                        "price": checkout_entity.price_id,
                        "quantity": 1
                    }
                ]
            )
            
            session_id=response.get("id", "")
            stripe_user = StripeUserCheckoutSession.query.filter_by(user_id=self.user.id).first()
            if not stripe_user:
                stripe_user = StripeUserCheckoutSession(
                    user_id=self.user.id,
                    session_id=session_id
                )
                db.session.add(stripe_user)
                db.session.commit()
            
            stripe_user.price_id = checkout_entity.price_id
            db.session.commit()
            return response.get("client_secret")
        except StripeError as e:
            raise SubscriptionException(str(e), 400)


@dataclass
class SubscriptionWebhookService:
    data: dict
    event_type: str


    def get_checkout_session(self, session_id) -> None:
        if "completed" in self.event_type:
            stripe.api_key = os.environ['STRIPE_SECRET_KEY']
            user_checkout = stripe.checkout.Session.retrieve(session_id)
            customer_id = user_checkout.get("customer")
            subscription_id = user_checkout.get("subscription")
            amount = user_checkout.get("amount", 0)
            if user_checkout.get("status", "") == "complete" and customer_id:
                stripe_user = StripeUserCheckoutSession.query.filter(
                    or_(session_id == session_id, customer_id == customer_id)
                ).first()
                if stripe_user:
                    subscription = Subscription.query.filter_by(price_id=stripe_user.price_id).first()
                    if subscription:
                        s_membership = SubscriptionMembership(
                            user_id=stripe_user.user_id,
                            subscription=subscription.id,
                            price=stripe_user.price_id,
                            customer_id=customer_id,
                            state="paid",
                            subscription_id=subscription_id
                        )
                        s_membership.price=amount
                        db.session.add(s_membership)
                        db.session.commit()

    def handle_updated_customer(self):
        logger.info("updated customer subscription")
        customer_id = self.data.get("customer")
        subscription_id = self.data.get("id")
        amount = self.data.get("items", {}).get("data", [{}])[0].get("amount", 0)
        s_membership = SubscriptionMembership.query.filter(
            or_(subscription_id == subscription_id, customer_id == customer_id)
        )
        if not s_membership:
            stripe_user = StripeUserCheckoutSession.query.filter(
                or_(subscription_id == subscription_id, customer_id == customer_id)
            ).first()
            subscription = Subscription.query.filter_by(price_id=stripe_user.price_id).first()
            if subscription and stripe_user:
                s_membership = SubscriptionMembership(
                    user_id=stripe_user.user_id,
                    subscription=subscription.id
                )
            else:
                return 200

        s_membership.price = amount
        s_membership.latest_invoice = self.data.get("in_1QUJIWFTd6Kcyq7qstFyalAK")
        s_membership.customer_id = customer_id
        s_membership.product_id = self.data.get("items", {}).get("data", [{}])[0].get("plan", {}).get("subscription_id")
        s_membership.subscription_id = subscription_id
        s_membership.state = "paid"
        s_membership.purchase_date =  (
            datetime.fromtimestamp(self.data.get("current_period_start"))
            if self.data.get("current_period_start") else None
        )
        s_membership.expired_at = (
            datetime.fromtimestamp(self.data.get("current_period_end"))
            if self.data.get("current_period_end") else None
        )
        s_membership.payment_frequency = self.data.get("items", {}).get("data", [{}])[0].get("plan", {}).get("interval")
        db.session.commit()
        logger.info("Customer updated successfully")

    def handle_payment_success(self):
        subscription_id = self.data.get("subscription")
        customer_id = self.data.get("customer")
        price_id = self.data.get("lines", {}).get("data", [{}])[0].get("price", {}).get("id")
        logger.info("user subscribe for price {}".format(price_id))
        s_membership = SubscriptionMembership.query.filter_by(customer_id=customer_id).first()
        if not s_membership:
            stripe_user = StripeUserCheckoutSession.query.filter(
                or_(subscription_id==subscription_id, customer_id==customer_id, price_id==price_id)
            ).first()
            subscription = Subscription.query.filter_by(price_id=price_id).first()
            logger.info("subscription_price: %s" % subscription.plan_name)
            if not subscription:
                return 200
            s_membership = SubscriptionMembership(
                user_id=stripe_user.user_id,
                subscription=subscription.id
            )
            db.session.add(s_membership)
            db.session.commit()

        s_membership.price = self.data.get("lines", {}).get("data", [{}])[0].get("price", {}).get("unit_amount", "")
        s_membership.latest_invoice = self.data.get("lines", {}).get("data", [{}])[0].get("invoice", "")
        s_membership.customer_id = customer_id
        s_membership.product_id = self.data.get("lines", {}).get("data", [{}])[0].get("plan", {}).get("product")
        s_membership.subscription_id = subscription_id
        s_membership.state = self.data.get("status")
        s_membership.purchase_date = (
            datetime.fromtimestamp(self.data.get("period_start"))
            if self.data.get("period_start") else None
        )
        s_membership.expired_at = (
            datetime.fromtimestamp(self.data.get("period_end"))
            if self.data.get("period_end") else None
        )
        s_membership.payment_frequency = self.data.get("lines", {}).get("data", [{}])[0].get("price", {}).get("recurring", {}).get("interval", ""),
        db.session.commit()
        logger.info(f"PaymentIntent succeeded")

    def handle_checkout_completed(self):
        logger.info(f"handle_checkout_completed")
        session_id = self.data.get("id")
        customer_id = self.data.get("customer")
        subscription_id = self.data.get("subscription")
        stripe_user = StripeUserCheckoutSession.query.filter(
            or_(session_id == session_id, customer_id == customer_id)
        ).first()
        if stripe_user:
            stripe_user.customer_id = customer_id
            stripe_user.subscription_id = subscription_id
        else:
            stripe_user = StripeUserCheckoutSession(
                session_id=session_id,
                customer_id=customer_id,
                subscription_id=subscription_id,
            )
            db.session.add(stripe_user)
        db.session.commit()
        logger.info("Checkout completed")

    def execute(self):
        if self.event_type == "checkout.session.completed":
            self.handle_checkout_completed()
        if self.event_type == "customer.subscription.updated":
            self.handle_updated_customer()
        elif self.event_type == "invoice.payment_succeeded":
            self.handle_payment_success()
        elif self.event_type in  ["invoice.payment_failed", "customer.subscription.deleted"]:
            status = self.data.get("status")
            cancelled_at = self.data.get("date")
            customer_id = self.data.get("customer")
            s_membership = SubscriptionMembership.query.filter_by(customer_id=customer_id).first()
            if not s_membership:
                raise SubscriptionException("Internal Server Error", 400)
            s_membership.state = status
            s_membership.cancelled_at = cancelled_at
            db.session.commit()
            logger.info(f"Invoice payment failed")
        else:
            session_id = self.data["id"]
            self.get_checkout_session(session_id)
            logger.info("Unhandled event type {}".format(self.event_type))

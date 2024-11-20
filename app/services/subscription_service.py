from dataclasses import dataclass
from datetime import datetime

import stripe
from stripe import StripeError

from app.exceptions import SubscriptionException
from app.services.entities import SubscriptionEntity


@dataclass
class UserSubscriptionService:
    user_id: int
    stripe_api_key: str

    def get_subscriptions(self, cs_subscription_id: str) -> SubscriptionEntity:

        try:
            stripe.api_key = self.stripe_api_key
            subscription =stripe.checkout.Session.retrieve(cs_subscription_id)
            subscription_entity = SubscriptionEntity(
                invoice_id=subscription.get('invoice', ""),
                customer_id=subscription.get('customer', ""),
                price=subscription.get('amount_total', 0),
                currency=subscription.get('currency', "usd"),
                status=subscription.get('status', "open"),
                purchase_date=(
                    datetime.fromtimestamp(subscription.get('created', ""))
                    if subscription.get('created', "") else None
                ),
                payment_status=subscription.get('payment_status', ""),
                subscription_id=subscription.get("subscription"),
                expires_at=subscription.get("expires_at", "")
                )

            return subscription_entity

        except StripeError as e:
            raise SubscriptionException(e, 400)



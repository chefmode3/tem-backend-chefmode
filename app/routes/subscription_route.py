import logging
import os

import stripe

from flask import request, abort
from marshmallow import ValidationError
from flask_restx import Namespace, Resource

from app.models import User
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.subscription_service import UserSubscriptionService, SubscriptionWebhookService
from app.serializers.subscription_serializer import (
    PaymentSerializer,
    UserSubscriptionSerializer,
    StripeEventSchema
)

payment_payload = PaymentSerializer()
subscription_ns = Namespace('subscriptions', description='Subscription related operations')

payment_model = convert_marshmallow_to_restx_model(subscription_ns, payment_payload)
subscription_response = convert_marshmallow_to_restx_model(subscription_ns, UserSubscriptionSerializer())
stripe_schema = StripeEventSchema()

logger = logging.getLogger(__name__)


def get_api_key():
    return os.environ['STRIPE_SECRET_KEY']


def get_stripe_event_secret():
    return os.environ['STRIPE_WEBHOOK_SECRET']


@subscription_ns.route('/pay_subscriptions/')
class UserPaidSubscriptions(Resource):

    def get(self):
        return 'get'

    @subscription_ns.expect(payment_model)
    @subscription_ns.response(200, "Payment successful.", model=subscription_response)
    @subscription_ns.response(400, "Bad Request.")
    @subscription_ns.response(401, "User does not exist.")
    def post(self):
        try:
            data = payment_payload.load(request.get_json())
            email = data.get("user_email", "")
            session_id = data.get("customer_id")
            user = User.query.filter_by(email=email).first()

            if not user or not user.activate:
                abort(401, description="User does not exist.")
            user_subscription = UserSubscriptionService(
                user=user,
                stripe_api_key=get_api_key()
            )
            subscription_id = user_subscription.get_get_checkout_session(session_id)
            user_membership = user_subscription.subscribe_user(subscription_id)
            return UserSubscriptionSerializer().dump(user_membership), 201
        except ValidationError as err:
            abort(400, description=err.messages)


@subscription_ns.route('/subscription/webhook/')
class SubscriptionWebhook(Resource):

    @subscription_ns.response(200, "successful.")
    def post(self):
        payload = request.data
        sig_header = request.headers.get("Stripe-Signature")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, get_stripe_event_secret())
        except (ValueError, stripe.error.SignatureVerificationError):
            return {"message": "Invalid payload or signature"}, 400

        try:
            validated_data = stripe_schema.load(event)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        event_type = validated_data["type"]
        data = validated_data.get('data', {})
        webhook_service = SubscriptionWebhookService(data, event_type)
        webhook_service.execute()
        return {"message": "Webhook received"}, 200

from __future__ import annotations

import logging
import os

import stripe
from flask import abort
from flask import request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_restx import Namespace
from flask_restx import Resource
from marshmallow import ValidationError

from app.decorateur.permissions import token_required
from app.models import SubscriptionMembership
from app.models import User
from app.serializers.subscription_serializer import PaymentSerializer, ManageSubscriptionSerializer
from app.serializers.subscription_serializer import StripeEventSchema
from app.serializers.subscription_serializer import UserSubscriptionSerializer
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.entities import CheckoutCreationEntity
from app.services.subscription_service import SubscriptionWebhookService
from app.services.subscription_service import UserSubscriptionService

payment_payload = PaymentSerializer()
subscription_ns = Namespace('subscriptions', description='Subscription related operations')

manage_subscription = ManageSubscriptionSerializer()

payment_model = convert_marshmallow_to_restx_model(subscription_ns, payment_payload)
manage_subscription_model = convert_marshmallow_to_restx_model(subscription_ns, manage_subscription)
subscription_response = convert_marshmallow_to_restx_model(subscription_ns, UserSubscriptionSerializer())
stripe_schema = StripeEventSchema()

logger = logging.getLogger(__name__)


def get_api_key():
    return os.environ['STRIPE_SECRET_KEY']


def get_stripe_event_secret():
    return os.environ['STRIPE_WEBHOOK_SECRET']


@subscription_ns.route('/pay_subscriptions/')
class UserPaidSubscriptions(Resource):

    @token_required
    @jwt_required(verify_type=False)
    def get(self):
        token = get_jwt()
        user = User.query.filter_by(email=token['sub']).first()
        subscription = SubscriptionMembership.query.filter_by(user_id=user.id).first()
        if subscription:
            return UserSubscriptionSerializer().dump(subscription), 201
        return "No subscription for this user"

    @subscription_ns.expect(payment_model)
    @subscription_ns.response(200, 'Payment successful.', model=subscription_response)
    @subscription_ns.response(400, 'Bad Request.')
    @subscription_ns.response(401, 'User does not exist.')
    @token_required
    @jwt_required(verify_type=False)
    def post(self):
        try:
            token = get_jwt()
            data = payment_payload.load(request.get_json())
            checkout_entity = CheckoutCreationEntity(
                price_id=data.get('price_id'),
                mode=data.get('mode'),
                redirect_url=os.environ.get('CHECKOUT_REDIRECT_URL')
            )
            user = User.query.filter_by(email=token['sub']).first()

            if not user or not user.activate:
                abort(401, description='User does not exist.')
            user_subscription = UserSubscriptionService(
                user=user,
                stripe_api_key=get_api_key()
            )
            result = user_subscription.create_checkout_session(checkout_entity)
            return {'client_secrete': result}, 200
        except ValidationError as err:
            abort(400, description=err.messages)

@subscription_ns.route('/manage_subscriptions/')
class ManageUserSubscriptions(Resource):
    @subscription_ns.expect(manage_subscription_model)
    @subscription_ns.response(200, 'Payment successful.', model=subscription_response)
    @subscription_ns.response(400, 'Bad Request.')
    @subscription_ns.response(401, 'User does not exist.')
    @token_required
    @jwt_required(verify_type=False)
    def post(self):
        token = get_jwt()
        data = payment_payload.load(request.get_json())
        user = User.query.filter_by(email=token['sub']).first()
        user_subscription = UserSubscriptionService(
            user=user,
            stripe_api_key=get_api_key()
        )
        subscription = user_subscription.update_user_subscription(data.get("price"))
        if subscription:
            return UserSubscriptionSerializer().dump(subscription), 201
        return "Can not update User subscription.", 400


@subscription_ns.route('/subscription/webhook/')
class SubscriptionWebhook(Resource):

    @subscription_ns.response(200, 'successful.')
    def post(self):
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, get_stripe_event_secret())
        except (ValueError, stripe.error.SignatureVerificationError):
            return {'message': 'Invalid payload or signature'}, 400

        try:
            validated_data = stripe_schema.load(event)
        except ValidationError as err:
            return {'message': 'Validation error', 'errors': err.messages}, 400
        event_type = validated_data["type"]
        data = validated_data.get('data', {}).get("object")
        webhook_service = SubscriptionWebhookService(data, event_type)
        webhook_service.execute()
        return {'message': 'Webhook received'}, 200

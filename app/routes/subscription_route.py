import os

from flask import request, abort
from marshmallow import ValidationError
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt

from app.serializers.subscription_serializer import PaymentSerializer, UserSubscriptionSerializer
from app.models import User
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.subscription_service import UserSubscriptionService

payment_payload = PaymentSerializer()
subscription_ns = Namespace('subscriptions', description='Subscription related operations')

payment_model = convert_marshmallow_to_restx_model(subscription_ns, payment_payload)
subscription_response = convert_marshmallow_to_restx_model(subscription_ns, UserSubscriptionSerializer())

def get_api_key():
    return os.environ['STRIPE_SECRET_KEY']


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
            return UserSubscriptionSerializer.dump(user_membership)
        except ValidationError as err:
            abort(400, description=err.messages)
        return 'post'


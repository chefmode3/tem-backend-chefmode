from flask_restx import Namespace, Resource
from flask import request, abort
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt

subscription_ns = Namespace('subscriptions', description='Subscription related operations')


@subscription_ns.route('/pay_subscriptions/')
class UserPaidSubscriptions(Resource):

    def get(self):
        return 'get'

    @jwt_required()
    @subscription_ns.expect()
    @subscription_ns.marshal_with(as_list=True)
    def post(self):
        return 'post'


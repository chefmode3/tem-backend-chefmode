from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


from app.models.payment import SubscriptionMembership


class UserSubscriptionSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = SubscriptionMembership
        load_instance = True
        exclude = ('subscription_id', 'customer_id')


class PaymentSerializer(Schema):
    price_id = fields.Str(required=True)
    mode = fields.Str(required=True)


class StripeEventSchema(Schema):
    id = fields.String(required=True)
    api_version = fields.String(required=True)
    livemode = fields.Boolean()
    request = fields.Dict(required=True)
    object = fields.String(required=True)
    created = fields.Integer(required=True)
    pending_webhooks = fields.Integer()
    type = fields.String(required=True)
    data = fields.Dict(required=True)


class ManageSubscriptionSerializer(Schema):
    price_id = fields.Str(required=True)

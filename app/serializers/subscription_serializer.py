from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


from app.models.payment import SubscriptionMembership


class UserSubscriptionSerializer(SQLAlchemyAutoSchema):
    class Meta:
        model = SubscriptionMembership
        load_instance = True
        exclude = ('subscription_id', 'customer_id')


class PaymentSerializer(Schema):
    customer_id = fields.Str(required=True)
    user_email = fields.Email(required=True)

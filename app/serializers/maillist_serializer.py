from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models.maillist import MailList


class MailListSchema(Schema):
    email = fields.Email(required=True)


class MailListSerializerResponse(SQLAlchemyAutoSchema):
    class Meta:
        model = MailList
        load_instance = True

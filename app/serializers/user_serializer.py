from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from app.models.user import User
from app.extensions import db


class UserSignupSchema(Schema):

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password', "user_id",)
        fields = ('password', "user_id",'name', 'email', 'activate', 'google_token', 'google_id')


class UserRegisterSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    google_token = fields.Str(required=False)
    google_id = fields.Str(required=False)
    activate = fields.Bool(required=False)


class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True, description="User email for password reset request")


class ResetPasswordSchema(Schema):
    new_password = fields.Str(required=True, description="New password for the user")


class UserResponseSchema(Schema):
    email = fields.Email(required=True)
    verified = fields.Boolean(required=True)

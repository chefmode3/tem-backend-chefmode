from marshmallow import Schema, fields, validate


class GoogleCallBackSchema(Schema):
    code = fields.Str(required=True)

class UserSignupSchema(Schema):

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=False)
    email = fields.Email(required=True)
    activate = fields.Boolean(required=False, default=False)
    google_token =fields.Str(required=False)
    google_id = fields.Str(required=False)


class UserRegisterSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=False)
    email = fields.Email(required=True)
    activate = fields.Boolean(required=False)
    google_token = fields.Str(required=False)
    google_id = fields.Str(required=False)
    access_token = fields.Str(required=True)


class UserResponseSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=False)
    email = fields.Email(required=True)
    activate = fields.Boolean(required=False, default=False)
    google_token = fields.Str(required=False)
    google_id = fields.Str(required=False)
    access_token = fields.Str(required=True)


class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True, description="User email for password reset request")


class ResetPasswordSchema(Schema):
    new_password = fields.Str(required=True, description="New password for the user")
    token = fields.Str(required=True, description="token identifiction")


class UserActivationSchema(Schema):
    email = fields.Email(required=True, description="User email for password reset request")
    token = fields.Str(required=True, description="token identifiction")
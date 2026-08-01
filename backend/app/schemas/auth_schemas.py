from marshmallow import Schema, fields, validate

class SignupSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    organization_name = fields.String(required=True, validate=validate.Length(min=1, max=255))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))
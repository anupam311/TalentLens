from marshmallow import Schema, fields, validate

class CreateCandidateSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.String(required=False, allow_none=True)
    location = fields.String(required=False, allow_none=True)
    linkedin_url = fields.String(required=False, allow_none=True)
    other_url = fields.String(required=False, allow_none=True)
    skills = fields.List(fields.String(), required=False, load_default=list)

class UpdateCandidateSchema(Schema):
    first_name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=False)
    phone = fields.String(required=False, allow_none=True)
    location = fields.String(required=False, allow_none=True)
    linkedin_url = fields.String(required=False, allow_none=True)
    other_url = fields.String(required=False, allow_none=True)
    skills = fields.List(fields.String(), required=False)
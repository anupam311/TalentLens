from marshmallow import Schema, fields, validate

class CreateJobSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    department = fields.String(required=False, allow_none=True)
    location = fields.String(required=False, allow_none=True)
    employment_type = fields.String(
        required=False,
        validate=validate.OneOf(["full-time", "part-time", "contract", "internship"]),
        load_default="full-time",
    )
    years_experience = fields.String(required=False, allow_none=True)
    salary_min = fields.Integer(required=False, allow_none=True)
    salary_max = fields.Integer(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    required_skills = fields.List(fields.String(), required=False, load_default=list)
    preferred_skills = fields.List(fields.String(), required=False, load_default=list)
    benefits = fields.String(required=False, allow_none=True)
    application_deadline = fields.Date(required=False, allow_none=True)

class UpdateJobSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    department = fields.String(required=False, allow_none=True)
    location = fields.String(required=False, allow_none=True)
    employment_type = fields.String(
        required=False,
        validate=validate.OneOf(["full-time", "part-time", "contract", "internship"]),
    )
    years_experience = fields.String(required=False, allow_none=True)
    salary_min = fields.Integer(required=False, allow_none=True)
    salary_max = fields.Integer(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    required_skills = fields.List(fields.String(), required=False)
    preferred_skills = fields.List(fields.String(), required=False)
    benefits = fields.String(required=False, allow_none=True)
    status = fields.String(required=False, validate=validate.OneOf(["draft", "active", "closed"]))
    application_deadline = fields.Date(required=False, allow_none=True)
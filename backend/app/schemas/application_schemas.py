from marshmallow import Schema, fields, validate

VALID_STATUSES = ["new", "screening", "interview", "offer", "hired", "rejected"]

class CreateApplicationSchema(Schema):
    candidate_id = fields.String(required=True)
    job_id = fields.String(required=True)
    source = fields.String(required=False, load_default="manual")


class UpdateApplicationStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(VALID_STATUSES))
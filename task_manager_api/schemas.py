from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    username = fields.Str(required=False, validate=validate.Length(min=3))
    email = fields.Email(required=False)
    password = fields.Str(required=True, validate=validate.Length(min=8))

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        if not data.get("username") and not data.get("email"):
            raise ValidationError("Either email or username is required")


class AddTask(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    completion = fields.Boolean(required=False)
    due_date = fields.DateTime(required=False)
    priority = fields.Str(
        required=False, validate=validate.OneOf([p.value for p in Priority])
    )  # validate  will test that value should be from this list only

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        if data.get("title") == "" and data.get("description") == "":
            raise ValidationError("title and  description cant be empty")


class UpdateTask(Schema):
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    completion = fields.Boolean(required=False)
    due_date = fields.DateTime(required=False)
    priority = fields.Str(
        required=False, validate=validate.OneOf([p.value for p in Priority])
    )

    @validates_schema
    def validate_identifier(self, data, **kwargs):
        if data.get("title") == "" and data.get("description") == "":
            raise ValidationError("title and  description cant be empty")


class ForgetPassword(Schema):
    email = fields.Email(required=True)


class VerifyOtp(Schema):
    otp = fields.Str(required=True, validate=validate.Length(min=6))
    email = fields.Email(required=True)


class ResetPassword(Schema):
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

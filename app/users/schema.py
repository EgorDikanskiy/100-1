from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(required=False)
    tg_id = fields.Int(required=True)
    first_name = fields.Str(required=True)

from marshmallow import Schema, fields

class GameSchema(Schema):
    id = fields.Int(required=False)
    chat_id = fields.Int(required=True)
    is_active = fields.Bool(required=True)
    created_at = fields.DateTime(required=False)

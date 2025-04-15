from marshmallow import Schema, fields

class GameSchema(Schema):
    id = fields.Int(required=False)
    chat_id = fields.Int(required=True)
    is_active = fields.Bool(required=True)
    created_at = fields.DateTime(required=False)


class GameScoreSchema(Schema):
    id = fields.Int(dump_only=True)
    player_id = fields.Int(required=True)
    game_id = fields.Int(required=True)
    score = fields.Int()
    is_active = fields.Bool()

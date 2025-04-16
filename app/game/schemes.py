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


class GameRoundSchema(Schema):
    id = fields.Int(dump_only=True)
    game_id = fields.Int(required=True)
    question_id = fields.Int(required=True)
    current_player_id = fields.Int(required=False)
    is_active = fields.Bool(required=False)
    created_at = fields.DateTime(dump_only=True)


class RoundQuestionAnswerSchema(Schema):
    id = fields.Int(dump_only=True)
    round_question_id = fields.Int(required=True)
    answer_id = fields.Int(required=True)
    is_found = fields.Bool(required=False)


class RoundQuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    round_id = fields.Int(required=True)
    question_id = fields.Int(required=True)
    is_found = fields.Bool(required=False)
    answers = fields.List(
        fields.Nested(RoundQuestionAnswerSchema), dump_only=True
    )

from marshmallow import Schema, fields

class AnswerSchema(Schema):
    id = fields.Int(dump_only=True)
    question_id = fields.Int(required=True)
    word = fields.Str(required=True)
    score = fields.Int(required=True)

class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    question = fields.Str(required=True)
    answers = fields.List(fields.Nested(AnswerSchema), dump_only=True)

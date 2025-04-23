from datetime import UTC, datetime

from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp_apispec import docs, request_schema, response_schema

from app.game.schemes import (
    GameRoundSchema,
    GameSchema,
    GameScoreSchema,
    RoundQuestionAnswerSchema,
    RoundQuestionSchema,
)
from app.web.app import View
from app.web.utils import json_response


class GameAddView(View):
    @docs(
        tags=["game"],
        summary="Add new game",
        description="Create a new game",
        responses={
            200: {"description": "Game successfully created"},
            409: {"description": "Game with this chat ID already exists"},
        },
    )
    @request_schema(GameSchema)
    @response_schema(GameSchema, 200)
    async def post(self):
        data = await self.request.json()
        chat_id = data["chat_id"]

        if await self.store.game.get_game_by_chat_id(chat_id=chat_id):
            raise HTTPConflict

        game = await self.store.game.create_game(
            chat_id=chat_id,
            is_active=data["is_active"],
            created_at=datetime.now(UTC),
        )
        return json_response(data=GameSchema().dump(game))


class GameGetView(View):
    @docs(
        tags=["game"],
        summary="Get game by chat ID",
        description="Retrieve game information by chat ID",
        parameters=[
            {
                "name": "chat_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Game found successfully"},
            400: {"description": "Invalid chat_id parameter"},
            404: {"description": "Game not found"},
        },
    )
    @response_schema(GameSchema, 200)
    async def get(self):
        chat_id_str = self.request.query.get("chat_id")
        if not chat_id_str or not chat_id_str.isdigit():
            raise HTTPBadRequest(
                text="Parameter 'chat_id' is required and must be an integer."
            )
        chat_id = int(chat_id_str)
        game = await self.store.game.get_game_by_chat_id(chat_id=chat_id)
        if not game:
            raise HTTPNotFound(text=f"Game with chat_id {chat_id} not found.")
        return json_response(data=GameSchema().dump(game))


class GamePatchView(View):
    @docs(
        tags=["game"],
        summary="Update game",
        description="Update game information",
        responses={
            200: {"description": "Game successfully updated"},
            404: {"description": "Game not found"},
        },
    )
    @request_schema(GameSchema)
    @response_schema(GameSchema, 200)
    async def patch(self):
        data = await self.request.json()
        chat_id = data.get("chat_id")
        is_active = data.get("is_active")

        updated_game = await self.store.game.update_game_is_active(
            chat_id=chat_id, new_status=is_active
        )
        if not updated_game:
            raise HTTPNotFound(text=f"Game with chat_id {chat_id} not found.")

        return json_response(data=GameSchema().dump(updated_game))


class GameScoreAddView(View):
    @docs(
        tags=["game"],
        summary="Add game score",
        description="Add a new score for a game",
        responses={
            200: {"description": "Score successfully added"},
            404: {"description": "Game not found"},
        },
    )
    @request_schema(GameScoreSchema)
    @response_schema(GameScoreSchema, 200)
    async def post(self):
        data = await self.request.json()
        try:
            score = await self.store.game_scores.create_game_score(
                player_id=data["player_id"],
                game_id=data["game_id"],
            )
            return json_response(data=GameScoreSchema().dump(score))
        except ValueError as e:
            raise HTTPConflict(text=str(e)) from e


class GameScoreListView(View):
    @docs(
        tags=["game"],
        summary="List game scores",
        description="Get all scores for a specific game",
        parameters=[
            {
                "name": "game_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Scores retrieved successfully"},
            404: {"description": "Game not found"},
        },
    )
    @response_schema(GameScoreSchema(many=True), 200)
    async def get(self):
        game_id_str = self.request.query.get("game_id")
        if not game_id_str or not game_id_str.isdigit():
            raise HTTPNotFound(text="Missing or invalid game_id")
        scores = await self.store.game_scores.get_scores_by_game(
            int(game_id_str)
        )
        return json_response(data=GameScoreSchema(many=True).dump(scores))


class GameRoundAddView(View):
    @docs(
        tags=["game"],
        summary="Add game round",
        description="Add a new round to a game",
        responses={
            200: {"description": "Round successfully added"},
            404: {"description": "Game not found"},
        },
    )
    @request_schema(GameRoundSchema)
    @response_schema(GameRoundSchema, 200)
    async def post(self):
        data = await self.request.json()
        game_round = await self.store.game_rounds.create_game_round(
            game_id=data["game_id"],
            question_id=data["question_id"],
            created_at=datetime.now(UTC),
        )
        return json_response(data=GameRoundSchema().dump(game_round))


class GameRoundGetView(View):
    @docs(
        tags=["game"],
        summary="Get game round",
        description="Get information about a specific game round",
        parameters=[
            {
                "name": "round_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Round found successfully"},
            404: {"description": "Round not found"},
        },
    )
    @response_schema(GameRoundSchema, 200)
    async def get(self):
        round_id = self.request.query.get("round_id")
        if not round_id or not round_id.isdigit():
            raise HTTPBadRequest(
                text="Query param 'round_id' is required and must be int"
            )
        round_id = int(round_id)
        game_round = await self.store.game_rounds.get_game_round(round_id)
        if not game_round:
            raise HTTPNotFound(text=f"GameRound {round_id} not found.")
        return json_response(data=GameRoundSchema().dump(game_round))


class GameRoundUpdateView(View):
    @docs(
        tags=["game"],
        summary="Update game round",
        description="Update information about a game round",
        responses={
            200: {"description": "Round successfully updated"},
            404: {"description": "Round not found"},
        },
    )
    @response_schema(GameRoundSchema, 200)
    async def patch(self):
        data = await self.request.json()
        round_id = data.get("round_id")
        current_player_id = data.get("current_player_id", None)
        new_status = data.get("is_active", True)
        updated = await self.store.game_rounds.update_round(
            round_id=round_id,
            current_player_id=current_player_id,
            is_active=new_status,
        )
        if not updated:
            raise HTTPNotFound(text=f"GameRound {round_id} not found.")
        return json_response(data=GameRoundSchema().dump(updated))


class RoundQuestionAddView(View):
    @docs(
        tags=["game"],
        summary="Add round question",
        description="Add a new question to a game round",
        responses={
            200: {"description": "Question successfully added"},
            404: {"description": "Round not found"},
        },
    )
    @request_schema(RoundQuestionSchema)
    @response_schema(RoundQuestionSchema, 200)
    async def post(self):
        data = await self.request.json()
        rq = await self.store.round_questions.create_round_question(
            round_id=data["round_id"],
            question_id=data["question_id"],
            is_found=False,
        )
        return json_response(data=RoundQuestionSchema().dump(rq))


class RoundQuestionGetView(View):
    @docs(
        tags=["game"],
        summary="Get round question",
        description="Get information about a specific question in a round",
        parameters=[
            {
                "name": "question_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Question found successfully"},
            404: {"description": "Question not found"},
        },
    )
    @response_schema(RoundQuestionSchema, 200)
    async def get(self):
        rq_id = self.request.query.get("id")
        if not rq_id or not rq_id.isdigit():
            raise HTTPBadRequest(
                text="Query parameter 'id' is required and must be an integer."
            )
        rq = await self.store.round_questions.get_round_question_by_id(
            int(rq_id)
        )
        if not rq:
            raise HTTPNotFound(text=f"RoundQuestion with id {rq_id} not found.")
        return json_response(data=RoundQuestionSchema().dump(rq))


class RoundQuestionAnswerAddView(View):
    @docs(
        tags=["game"],
        summary="Add question answer",
        description="Add an answer to a round question",
        responses={
            200: {"description": "Answer successfully added"},
            404: {"description": "Question not found"},
        },
    )
    @request_schema(RoundQuestionAnswerSchema)
    @response_schema(RoundQuestionAnswerSchema, 200)
    async def post(self):
        data = await self.request.json()
        crt_rqa = self.store.round_question_answers.create_round_question_answer
        rqa = await crt_rqa(
            round_question_id=data["round_question_id"],
            answer_id=data["answer_id"],
            is_found=False,
        )
        return json_response(data=RoundQuestionAnswerSchema().dump(rqa))


class RoundQuestionAnswerGetView(View):
    @docs(
        tags=["game"],
        summary="Get question answers",
        description="Get all answers for a specific question",
        parameters=[
            {
                "name": "question_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Answers retrieved successfully"},
            404: {"description": "Question not found"},
        },
    )
    @response_schema(RoundQuestionAnswerSchema(many=True), 200)
    async def get(self):
        rq_id = self.request.query.get("round_question_id")
        if not rq_id or not rq_id.isdigit():
            raise HTTPBadRequest(
                text="Query parameter 'round_question_id' is "
                "required and must be an integer."
            )
        g_abrq = self.store.round_question_answers.get_answers_by_round_question
        answers = await g_abrq(int(rq_id))
        if not answers:
            raise HTTPNotFound(
                text=f"No answers found for round_question_id {rq_id}."
            )
        return json_response(
            data=RoundQuestionAnswerSchema(many=True).dump(answers)
        )

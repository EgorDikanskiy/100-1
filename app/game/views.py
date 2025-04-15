from datetime import datetime, timezone
from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp_apispec import request_schema, response_schema
from app.web.app import View
from app.web.utils import json_response
from app.game.schemes import GameSchema, GameScoreSchema


class GameAddView(View):
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
            created_at=datetime.now(timezone.utc),
        )
        return json_response(data=GameSchema().dump(game))
    

class GameGetView(View):
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
    @request_schema(GameSchema)
    @response_schema(GameSchema, 200)
    async def patch(self):
        data = await self.request.json()
        chat_id = data.get("chat_id")
        is_active = data.get("is_active")

        updated_game = await self.store.game.update_game_is_active(chat_id=chat_id, new_status=is_active)
        if not updated_game:
            raise HTTPNotFound(text=f"Game with chat_id {chat_id} not found.")

        return json_response(data=GameSchema().dump(updated_game))
    
    
class GameScoreAddView(View):
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
            raise HTTPConflict(text=str(e))


class GameScoreListView(View):
    @response_schema(GameScoreSchema(many=True), 200)
    async def get(self):
        game_id_str = self.request.query.get("game_id")
        if not game_id_str or not game_id_str.isdigit():
            raise HTTPNotFound(text="Missing or invalid game_id")
        scores = await self.store.game_scores.get_scores_by_game(int(game_id_str))
        return json_response(data=GameScoreSchema(many=True).dump(scores))

        
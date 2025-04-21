from datetime import UTC, datetime
from ..base import BaseCommandHandler
from app.store.tg_api.dataclasses import Message
from ..utils.helpers import create_round_with_question

class StartGameHandler(BaseCommandHandler):
    async def handle(self):
        game = await self.app.store.game.get_game_by_chat_id(chat_id=self.chat_id)

        if game and game.is_active:
            await self._handle_active_game(game)
        else:
            game = await self.app.store.game.create_game(
                chat_id=self.chat_id, is_active=True, created_at=datetime.now(UTC)
            )
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="Игра началась")
            )
            await create_round_with_question(app=self.app, game_id=game.id, chat_id=self.chat_id)

    async def _handle_active_game(self, game):
        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text="Игра активна")
        )
        rounds = await self.app.store.game_rounds.get_game_rounds_by_game_id(game_id=game.id)
        if not any(r.is_active for r in rounds):
            await create_round_with_question(app=self.app, game_id=game.id, chat_id=self.chat_id)
        else:
            await self.app.store.tg_api.send_message(
                Message(chat_id=self.chat_id, text="Есть активный раунд")
            )

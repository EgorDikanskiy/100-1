from app.store.tg_api.dataclasses import Message

from ..base import BaseCommandHandler


class JoinGameHandler(BaseCommandHandler):
    async def handle(self):
        callback_query = self.update.object.message
        user = await self.app.store.users.get_user_by_tg_id(callback_query.user_id)
        game = await self.app.store.game.get_game_by_chat_id(
            chat_id=callback_query.chat_id
        )

        if not game or not game.is_active:
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text="Нет активной игры для присоединения."
                )
            )
            return

        # Check if user is already in the game
        game_scores = await self.app.store.game_scores.get_scores_by_game(game.id)
        if any(score.player_id == user.id for score in game_scores):
            await self.app.store.tg_api.send_message(
                Message(
                    chat_id=self.chat_id,
                    text=f"{user.first_name}, вы уже в игре!"
                )
            )
            return

        # Add user to the game
        await self.app.store.game_scores.create_game_score(
            user.id, game.id
        )

        # Update the message to show who joined
        await self.app.store.tg_api.send_message(
            Message(
                chat_id=self.chat_id,
                text=f"{user.first_name} присоединился к игре!"
            )
        ) 
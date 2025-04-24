from app.store.tg_api.dataclasses import Message, Update
from app.web.app import Application

from ..base import BaseCommandHandler


class RulesHandler(BaseCommandHandler):
    def __init__(self, app: "Application", update: Update):
        super().__init__(app, update)

    async def handle(self):
        rules_text = """🎲 Правила игры «Сто к одному» 🎲

📝 Как играть:

1️⃣ Бот публикует вопрос в чат
2️⃣ Первый нажавший кнопку получает право ответить
3️⃣ За правильный ответ начисляются очки
4️⃣ При ошибке игрок не может ответить на вопрос
5️⃣ Побеждает тот, кто наберёт больше всех очков

🎮 Команды бота:
/start_game — начать новую игру
/stop_game — завершить текущую игру
/rules — показать правила

Удачи и пусть победит сильнейший! 🎉"""
        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text=rules_text)
        )

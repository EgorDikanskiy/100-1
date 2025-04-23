from app.store.tg_api.dataclasses import Message, Update
from app.web.app import Application
from ..base import BaseCommandHandler


class RulesHandler(BaseCommandHandler):
    def __init__(self, app: "Application", update: Update):
        super().__init__(app, update)

    async def handle(self):
        rules_text = (
            """🎲 Правила игры «Сто к одному» для Telegram-бота

1. Объявляется вопрос.
Бот публикует новый вопрос в чат.

2.Кто первый нажал – тот и отвечает.
Участники соревнуются за право первым дать ответ.

3. Верный ответ – начисляются баллы.
За каждый правильный ответ участник получает определённое количество очков.

4. Неверный ответ – выбываешь.
При ошибке участник выбывает и не может отвечать на вопрос.

5. Набрать больше всех баллов.
Побеждает игрок, который к концу игры наберёт наибольшее количество очков.

Команды бота

/start_game — начать новую игру

/stop_game — завершить текущую игру

Удачи и пусть победит сильнейший! 🎉"""
        )
        await self.app.store.tg_api.send_message(
            Message(chat_id=self.chat_id, text=rules_text)
        )
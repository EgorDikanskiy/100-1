import json
from typing import Any

want_answer_keyboard: dict[str, Any] = {
    "inline_keyboard": [
        [
            {
                "text": "Хочу ответить!",
                "callback_data": json.dumps({"button": "1"}),
            }
        ]
    ]
}

join_game_keyboard = {
    "inline_keyboard": [
        [
            {
                "text": "Присоединиться к игре",
                "callback_data": "join_game"
            }
        ]
    ]
}

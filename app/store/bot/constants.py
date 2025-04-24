import json
from typing import Any

want_answer_keyboard: dict[str, Any] = {
    "inline_keyboard": [
        [
            {
                "text": "Хочу ответить",
                "callback_data": "want_answer",
            }
        ]
    ]
}

join_game_keyboard: dict[str, Any] = {
    "inline_keyboard": [
        [
            {
                "text": "Присоединиться к игре",
                "callback_data": "join_game"
            }
        ]
    ]
}

yes_no_keyboard: dict[str, Any] = {
    "inline_keyboard": [
        [
            {
                "text": "Да",
                "callback_data": "yes_button"
            },
            {
                "text": "Нет",
                "callback_data": "no_button"
            }
        ]
    ]
}

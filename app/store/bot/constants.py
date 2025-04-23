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

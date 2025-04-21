import json
from typing import Any, Dict

want_answer_keyboard: Dict[str, Any] = {
    "inline_keyboard": [
        [
            {
                "text": "Хочу ответить!",
                "callback_data": json.dumps({"button": "1"})
            }
        ]
    ]
}
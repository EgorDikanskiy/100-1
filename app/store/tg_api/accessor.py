import json
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.tg_api.dataclasses import (
    Message,
    Update,
    UpdateMessage,
    UpdateObject,
)
from app.store.tg_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_URL_TEMPLATE = "https://api.telegram.org/bot{token}/"
GET_UPDATES_METHOD = "getUpdates"
SEND_MESSAGE_METHOD = "sendMessage"


class TelegramApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.session: ClientSession | None = None
        self.offset: int = 0
        self.poller: Poller | None = None

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        self.poller = Poller(app.store)
        self.logger.info("Start polling Telegram updates")
        self.poller.start()

    async def disconnect(self, app: "Application") -> None:
        if self.session:
            await self.session.close()

        if self.poller:
            await self.poller.stop()

    def _build_query(self, method: str, params: dict) -> str:
        base_url = API_URL_TEMPLATE.format(token=self.app.config.bot.token)
        params_encoded = urlencode(params)
        return urljoin(base_url, f"{method}?{params_encoded}")

    async def poll(self) -> None:
        params = {
            "offset": self.offset,
            "timeout": 30,
            "allowed_updates": ["message", "callback_query", "chat_member", "chat_join_request"]
        }
        url = self._build_query(GET_UPDATES_METHOD, params)
        async with self.session.get(url) as response:
            data = await response.json()
            if not data.get("ok"):
                self.logger.error("Ошибка в получении обновлений: %s", data)
                return

            updates_data = data.get("result", [])
            if updates_data:
                self.offset = updates_data[-1]["update_id"] + 1

            updates: list[Update] = []
            for upd in updates_data:
                message_data = upd.get("message")
                callback = upd.get("callback_query")

                if callback:
                    cb_msg = callback.get("message", {})
                    inline_kb = cb_msg.get("reply_markup", {}).get("inline_keyboard", [[]])
                    button_text = inline_kb[0][0].get("text") if inline_kb and inline_kb[0] else None
                    callback_data = callback.get("data")

                    update_msg = UpdateMessage(
                        id=cb_msg.get("message_id"),
                        chat_id=cb_msg.get("chat", {}).get("id"),
                        user_id=callback.get("from", {}).get("id"),
                        text=button_text or callback_data,
                        type="callback_query",
                    )

                elif message_data and "new_chat_member" in message_data:
                    new_member = message_data["new_chat_member"]
                    update_msg = UpdateMessage(
                        id=message_data.get("message_id"),
                        chat_id=message_data.get("chat", {}).get("id"),
                        new_user_tg_id=new_member.get("id"),
                        new_user_first_name=new_member.get("first_name"),
                        type="add_member"
                    )

                elif message_data and "text" in message_data:
                    update_msg = UpdateMessage(
                        id=message_data.get("message_id"),
                        user_id=message_data.get("from", {}).get("id"),
                        chat_id=message_data.get("chat", {}).get("id"),
                        text=message_data.get("text"),
                        type='text'
                    )

                else:
                    continue

                update_obj = UpdateObject(message=update_msg)
                updates.append(Update(type="message", object=update_obj))

            if updates:
                await self.app.store.bots_manager.handle_updates(updates)

    async def send_message(self, message: Message) -> None:
        params = {
            "chat_id": message.chat_id,
            "text": message.text,
        }
        body = {}
        if message.reply_markup is not None:
            body["reply_markup"] = json.dumps(message.reply_markup)

        url = self._build_query(SEND_MESSAGE_METHOD, params=params)
        async with self.session.post(url, json=body) as response:
            data = await response.json()
            self.logger.info("send_message response: %s", data)

    async def edit_message_reply_markup(self, chat_id: int, message_id: int):
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": json.dumps({"inline_keyboard": []})
        }
        url = self._build_query("editMessageReplyMarkup", params)
        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info("edit_message_reply_markup response: %s", data)

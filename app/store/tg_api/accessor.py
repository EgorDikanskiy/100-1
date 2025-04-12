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

            updates = []
            for upd in updates_data:
                message_data = upd.get("message")
                if not message_data or "text" not in message_data:
                    continue
                update_msg = UpdateMessage(
                    id=message_data.get("message_id"),
                    user_id=message_data.get("from", {}).get("id"),
                    chat_id=message_data.get("chat", {}).get("id"),
                    text=message_data.get("text"),
                )
                update_obj = UpdateObject(message=update_msg)
                update = Update(type="message", object=update_obj)
                updates.append(update)

            if updates:
                await self.app.store.bots_manager.handle_updates(updates)

    async def send_message(self, message: Message) -> None:
        params = {
            "chat_id": message.chat_id,
            "text": message.text,
        }
        url = self._build_query(SEND_MESSAGE_METHOD, params)
        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info("send_message response: %s", data)

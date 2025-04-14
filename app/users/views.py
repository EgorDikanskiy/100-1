from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp_apispec import request_schema, response_schema
from app.web.app import View
from app.web.utils import json_response
from app.users.schema import UserSchema


class UserAddView(View):
    @request_schema(UserSchema)
    @response_schema(UserSchema, 200)
    async def post(self):
        data = await self.request.json()
        tg_id = data["tg_id"]
        first_name = data["first_name"]
        if await self.store.users.get_user_by_tg_id(tg_id=tg_id):
            raise HTTPConflict
        user = await self.store.users.create_user(tg_id=tg_id, first_name=first_name)
        return json_response(data=UserSchema().dump(user))

class UserGetView(View):
    @response_schema(UserSchema, 200)
    async def get(self):
        tg_id_str = self.request.query.get("tg_id")
        if not tg_id_str or not tg_id_str.isdigit():
            raise HTTPBadRequest(text="Parameter 'tg_id' is required and must be an integer.")
        tg_id = int(tg_id_str)
        
        user = await self.store.users.get_user_by_tg_id(tg_id=tg_id)
        if not user:
            raise HTTPNotFound(text=f"User with tg_id {tg_id} not found.")
        
        return json_response(data=UserSchema().dump(user))
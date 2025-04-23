from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session

from app.admin.schemes import AdminRequestSchema, AdminResponseSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(
        tags=["admin"],
        summary="Admin login",
        description="Authenticate admin user with email and password",
        responses={
            200: {"description": "Successfully authenticated"},
            403: {"description": "Invalid credentials"}
        }
    )
    @request_schema(AdminRequestSchema)
    @response_schema(AdminResponseSchema, 200)
    async def post(self):
        data = await self.request.json()
        email = data["email"]
        password = data["password"]
        admin = await self.store.admins.get_by_email(email)
        if not admin or not admin.is_correct_password(password):
            raise HTTPForbidden
        admin_data = AdminResponseSchema().dump(admin)
        session = await new_session(self.request)
        session["token"] = self.request.app.config.session.key
        session["admin"] = admin_data
        return json_response(data=admin_data)


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"],
        summary="Get current admin",
        description="Get information about currently authenticated admin",
        responses={
            200: {"description": "Successfully retrieved admin info"},
            401: {"description": "Unauthorized - admin not authenticated"}
        }
    )
    @response_schema(AdminResponseSchema, 200)
    async def get(self):
        response = AdminResponseSchema().dump(self.request.admin)
        return json_response(data=response)

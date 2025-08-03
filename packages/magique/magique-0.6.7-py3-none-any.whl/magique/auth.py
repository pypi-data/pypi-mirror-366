import os

from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import Request
from fastapi.responses import HTMLResponse
from jose import jwt


class AuthManager:
    def __init__(self, redirect_uri: str | None = None):
        self._auth_response = None
        client_id = os.getenv("AUTH0_CLIENT_ID")
        client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        redirect_uri = os.getenv("AUTH0_REDIRECT_URI", redirect_uri)
        self.app_secret = os.getenv("MAGIQUE_SECRET_KEY")
        self.auth0_domain = os.getenv("AUTH0_DOMAIN")

        self.oauth = AsyncOAuth2Client(
            client_id,
            client_secret,
            redirect_uri=redirect_uri,
            scope="openid profile email",
        )

        self.login_timeout = 90.0  # seconds
        self._auth_callback = None

    def get_auth_url(self):
        authorization_base_url = f"https://{self.auth0_domain}/authorize"
        auth_url, _ = self.oauth.create_authorization_url(
            authorization_base_url)
        return auth_url

    async def auth_callback(self, request: Request):
        url = request.url
        self._auth_response = url.path + "?" + url.query
        return HTMLResponse(
            content="Login successful. You can close this window.")

    async def fetch_token(self):
        token_url = f"https://{self.auth0_domain}/oauth/token"
        token = await self.oauth.fetch_token(
            token_url, authorization_response=self._auth_response
        )
        self._auth_response = None
        return token

    async def get_user_info(self):
        userinfo_url = f"https://{self.auth0_domain}/userinfo"
        response = await self.oauth.get(userinfo_url)
        return response.json()

    def create_jwt(self, user_info):
        return jwt.encode(user_info, self.app_secret, algorithm="HS256")

    def decode_jwt(self, jwt_str: str):
        return jwt.decode(jwt_str, self.app_secret, algorithms=["HS256"])

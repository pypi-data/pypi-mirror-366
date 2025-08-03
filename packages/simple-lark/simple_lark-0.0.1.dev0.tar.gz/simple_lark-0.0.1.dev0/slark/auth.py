import time
from typing import Literal
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

UserIdType = Literal["open_id", "union_id", "user_id"]


class AccessToken(BaseModel):
    token: str
    expires_at: int

    def is_valid(self):
        return self.expires_at > time.time()

    @classmethod
    def dummy(cls) -> "AccessToken":
        return AccessToken(token="", expires_at=0)


class UserAccessTokenResp(BaseModel):
    token_type: str = ""
    access_token: str = ""
    expires_in: int = 0
    scope: str = ""
    refresh_token: str = ""
    refresh_token_expires_in: int = 0
    code: int = 0
    error: str = ""
    error_description: str = ""


class Auth:
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        base_url: str = "https://open.feishu.cn/open-apis",
        http_client: httpx.Client = None,
        async_http_client: httpx.AsyncClient = None,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url
        self.http_client = http_client or httpx.Client()
        self.async_http_client = async_http_client or httpx.AsyncClient()

    def get_tenant_access_token_internal(self) -> AccessToken:
        # https://open.larkoffice.com/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal/"
        post_data = {"app_id": self.app_id, "app_secret": self.app_secret}
        now = int(time.time()) - 10
        res = self.http_client.post(url, data=post_data).json()
        return AccessToken(token=res["tenant_access_token"], expires_at=res["expire"] + now)

    async def aget_tenant_access_token_internal(self) -> AccessToken:
        # https://open.larkoffice.com/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal/"
        post_data = {"app_id": self.app_id, "app_secret": self.app_secret}
        now = int(time.time()) - 10
        res = await self.async_http_client.post(url, data=post_data)
        res = res.json()
        return AccessToken(token=res["tenant_access_token"], expires_at=res["expire"] + now)

    def get_user_access_token(
        self, code: str, redirect_uri: str, code_verifier: str = "", scope: str = ""
    ) -> UserAccessTokenResp:
        """
        see https://open.larkoffice.com/document/authentication-management/access-token/get-user-access-token

        :param code:
        :param redirect_uri:
        :param code_verifier:
        :param scope:
        :return:
        """
        url = f"{self.base_url}/authen/v2/oauth/token"
        payload = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "scope": scope,
            "code_verifier": code_verifier,
        }
        res = self.http_client.post(url, data=payload)
        return UserAccessTokenResp.model_validate_json(res.text)

    async def aget_user_access_token(
        self, code: str, redirect_uri: str, code_verifier: str = "", scope: str = ""
    ) -> UserAccessTokenResp:
        """
        see https://open.larkoffice.com/document/authentication-management/access-token/get-user-access-token

        :param code:
        :param redirect_uri:
        :param code_verifier:
        :param scope:
        :return:
        """
        url = f"{self.base_url}/authen/v2/oauth/token"
        payload = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "scope": scope,
            "code_verifier": code_verifier,
        }
        res = await self.async_http_client.post(url, data=payload)
        return UserAccessTokenResp.model_validate_json(res.text)

    def make_auth_url(
        self,
        app_id: str,
        redirect_uri: str,
        scope: str = "",
        state: str = "",
        code_challenge: str = "",
        code_challenge_method="",
    ) -> str:
        """
        获取授权码
        see https://open.larkoffice.com/document/authentication-management/access-token/obtain-oauth-code
        权限列表：https://open.larkoffice.com/document/server-docs/application-scope/scope-list

        :param app_id:
        :param redirect_uri:
        :param scope:
        :param state:
        :param code_challenge:
        :param code_challenge_method:
        :return:
        """
        params = {
            "app_id": app_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        }
        # 1. 将用户浏览器重定向到下面的URL
        # 2. 用户在授权后会被重定向到 redirect_uri，并且会在URL中包含一个授权码（code）和一个状态值（state）
        # 3. 根据 code 获取 access_token
        return f"{self.base_url}/authen/v1/authorize?{urlencode(params)}"

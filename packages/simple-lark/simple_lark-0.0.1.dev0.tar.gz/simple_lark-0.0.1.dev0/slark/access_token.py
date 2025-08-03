import time

from pydantic import BaseModel


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


class TenantAccessTokenReq(BaseModel):
    app_id: str = ""
    app_secret: str = ""


class UserAccessTokenReq(BaseModel):
    client_id: str  # app_id
    client_secret: str  # app_secret
    code: str
    redirect_uri: str
    code_verifier: str = ""
    scope: str = ""
    grant_type: str = "authorization_code"


class TenantAccessTokenResp(BaseModel):
    tenant_access_token: str
    expire: int

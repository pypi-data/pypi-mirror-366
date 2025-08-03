import functools
import inspect
import json
import logging
from pathlib import Path
from string import Template
from typing import Callable, Generic, Optional, Set, TypeVar

import httpx
from pydantic import BaseModel

from slark.access_token import AccessToken, TenantAccessTokenResp, UserAccessTokenResp

from .auth import Auth

logger = logging.getLogger(__name__)


class TokenExchanger:
    def get_tenant_access_token_internal(self, body: dict) -> TenantAccessTokenResp: ...
    def get_user_access_token(self, body: dict) -> UserAccessTokenResp: ...
    async def aget_tenant_access_token_internal(self, body: dict) -> TenantAccessTokenResp: ...
    async def aget_user_access_token(self, body: dict) -> UserAccessTokenResp: ...


class ApiException(RuntimeError):
    def __init__(self, code, msg, err):
        super().__init__(f"{code}: {msg}", err)
        self.code = code
        self.msg = msg
        self.err = err


class App:
    def __init__(self, auth: Auth):
        self.auth = auth
        self.base_url = auth.base_url
        self._tat = self._load_tat()
        self._http_client = auth.http_client
        self._async_http_client = auth.async_http_client

    def _load_tat(self) -> AccessToken:
        filepath = Path(f"~/.cache/slark/tat-{self.auth.app_id}.json").expanduser()
        if not filepath.exists():
            return AccessToken.dummy()
        js = filepath.read_text()
        try:
            return AccessToken.model_validate_json(js)
        except ValueError as ex:
            logger.warning(f"invalid token cache: {ex}")
            return AccessToken.dummy()

    def _cache_tat(self, tat: AccessToken):
        filepath = Path(f"~/.cache/slark/tat-{self.auth.app_id}.json").expanduser()
        dir = filepath.parent
        if not dir.exists():
            dir.mkdir(parents=True)
        filepath.write_text(tat.model_dump_json())

    def get_tenant_access_token(self) -> str:
        # https://open.larkoffice.com/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        if not self._tat.is_valid():
            self._tat = self.auth.get_tenant_access_token_internal()
            self._cache_tat(self._tat)

        return self._tat.token

    async def aget_tenant_access_token(self) -> str:
        # https://open.larkoffice.com/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        if not self._tat.is_valid():
            self._tat = await self.auth.aget_tenant_access_token_internal()
            self._cache_tat(self._tat)

        return self._tat.token

    def fire(self, method: str, path: str, params: dict, body: dict, access_token: str = "") -> httpx.Response:
        if not access_token:
            access_token = self.get_tenant_access_token()

        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.base_url}{path}"
        resp = self._http_client.request(method, url, headers=headers, json=body, params=params)
        return resp

    async def afire(self, method: str, path: str, params: dict, body: dict, access_token: str = "") -> httpx.Response:
        if not access_token:
            access_token = await self.aget_tenant_access_token()

        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.base_url}{path}"
        resp = await self._async_http_client.request(method, url, headers=headers, json=body, params=params)
        return resp

    @staticmethod
    def parse_server_response(resp: httpx.Response) -> dict:
        logger.debug(f"{resp.request.method} {resp.url} RESP: {resp.text}")
        try:
            resp = resp.json()
        except json.JSONDecodeError as exc:
            raise ApiException(-1, resp.text, "response is not valid JSON") from exc

        code, msg, error = resp.get("code"), resp.get("msg"), resp.get("error")
        if code != 0:
            exc = ApiException(code, msg, error)
            exc.add_note(resp.url)
            raise exc
        return resp["data"]


class EndPointKit:
    def __init__(self, app: App):
        self.app = app


Q = TypeVar("Q", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)


class EndPoint(Generic[Q, R]):
    @staticmethod
    def make(path: str, func: Callable, method: Optional[str] = None) -> "EndPoint":
        sig = inspect.signature(func)
        resp_class = sig.return_annotation
        if not resp_class:
            raise ValueError(f"{func.__name__} must have a return annotation")
        assert issubclass(resp_class, BaseModel), f"{func.__name__} return annotation must be a subclass of BaseModel"

        # check path params
        tpl = Template(path.replace(":", "$"))
        # tpl.get_identifiers not in earlier version of Python
        path_ids = set()
        for it in path.split("/"):
            if it.startswith(":"):
                name = it[1:]
                path_ids.add(name)
                assert name in sig.parameters, f"{func.__name__} path param {name} must be in func params"

        req_class = None
        body_name = None
        for name, param in sig.parameters.items():
            assert param.kind == inspect._ParameterKind.POSITIONAL_OR_KEYWORD, (
                f"{func.__name__} argument '{name}' is not positional"
            )

            if param.annotation and isinstance(param.annotation, type):
                if issubclass(param.annotation, BaseModel):
                    assert not req_class, f"{func.__name__} only support one req class"
                    req_class = param.annotation
                    body_name = name

        if not method:
            method = "POST" if body_name else "GET"

        return EndPoint(tpl, method, body_name, req_class, resp_class, sig, path_ids)

    def __init__(
        self,
        path: Template,
        method: str,
        body_name: str,
        req_class: type[Q],
        resp_class: type[R],
        sig: inspect.Signature,
        path_ids: Set[str],  # NOQA
    ):
        self.path = path
        self.method = method
        self.body_name = body_name
        self.req_class = req_class
        self.resp_class = resp_class
        self.sig = sig
        self.path_ids = path_ids

    def _prepare(self, *args, **kwargs):
        params = self.sig.bind(self, *args, **kwargs)
        params.apply_defaults()

        params = params.arguments
        body = None
        if self.body_name:
            body = params.pop(self.body_name)
            if isinstance(body, self.req_class):
                body = body.model_dump()

        path_ids = self.path_ids
        url_params = {k: v for k, v in params.items() if k not in path_ids and k != "self"}
        path_params = {k: v for k, v in params.items() if k in path_ids and k != "self"}

        path = self.path.substitute(path_params)
        return path, url_params, body

    def fire(self, kit: EndPointKit, *args, **kwargs) -> R:
        access_token = kwargs.pop("_access_token", "")
        path, url_params, body = self._prepare(*args, **kwargs)
        resp = kit.app.fire(self.method, path, url_params, body, access_token)
        data = kit.app.parse_server_response(resp)
        return self.resp_class.model_validate(data)

    async def afire(self, kit: EndPointKit, *args, **kwargs) -> R:
        access_token = kwargs.pop("_access_token", "")
        path, url_params, body = self._prepare(*args, **kwargs)
        resp = await kit.app.afire(self.method, path, url_params, body, access_token)
        data = kit.app.parse_server_response(resp)
        return self.resp_class.model_validate(data)

    def make_fn(self, func):
        @functools.wraps(func)
        def fn(kit: EndPointKit, *args, **kwargs):
            return self.fire(kit, *args, **kwargs)

        fn.endpoint = self
        return fn

    def make_async_fn(self, func):
        @functools.wraps(func)
        async def afn(kit: EndPointKit, *args, **kwargs):
            return await self.afire(kit, *args, **kwargs)

        afn.endpoint = self
        return afn


def api(path: str, method: Optional[str] = None):
    def decorator(func):
        ep = EndPoint.make(path, func, method)
        if inspect.iscoroutinefunction(func):
            return ep.make_async_fn(func)
        return ep.make_fn(func)

    return decorator

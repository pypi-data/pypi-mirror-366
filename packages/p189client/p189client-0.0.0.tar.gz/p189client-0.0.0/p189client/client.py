#!/usr/bin/env python3
# encoding: utf-8

from __future__ import annotations

__all__ = ["check_response", "P189APIClient", "P189Client"]

from abc import abstractmethod, ABC
from base64 import b64encode
from binascii import hexlify
from collections.abc import (
    AsyncIterable, Awaitable, Buffer, Callable, Coroutine, 
    Iterable, Iterator, Mapping, MutableMapping, 
)
from datetime import datetime
from errno import EIO, EAUTH
from functools import partial
from hashlib import md5
from html import unescape
from http.cookiejar import Cookie, CookieJar
from http.cookies import Morsel
from inspect import isawaitable
from itertools import pairwise
from os import fsdecode, fstat, isatty, PathLike
from os.path import basename
from random import randrange
from re import compile as re_compile, Match
from sys import exc_info
from time import time
from typing import cast, overload, Any, Final, Literal, Self
from urllib.parse import parse_qsl, quote, unquote, urlsplit
from uuid import uuid4

from asynctools import ensure_async
from cookietools import cookies_str_to_dict, create_cookie
from dicttools import iter_items, get_first
from filewrap import (
    bio_chunk_iter, bio_chunk_async_iter, buffer_length, bio_skip_iter, bio_skip_async_iter, 
    bytes_to_chunk_iter, bytes_iter_to_reader, bytes_iter_to_async_reader, SupportsRead
)
from hashtools import file_digest, file_digest_async, ChunkedHash, HashObj
from http_request import headers_str_to_dict, SupportsGeturl
from iterutils import run_gen_step, through, with_iter_next
from orjson import dumps, loads, JSONDecodeError
from p189sign import make_signed_headers, make_hmac_signed_headers, make_encrypted_params_headers
from property import locked_cacheproperty
from yarl import URL

from .const import API_URL, WEB_URL
from .exception import P189OSError, P189LoginError


CRE_JS_unifyLoginForPC_search: Final = re_compile(r"(?<=/\*qr扫码登录客户端配置\*/)[\s\S]+?(?=</script>)").search
CRE_JS_NAME_DEF_finditer: Final = re_compile(r"\w+\s*=\s*[^,;]+").finditer

# 默认的请求函数
_httpx_request = None


def get_default_request():
    global _httpx_request
    if _httpx_request is None:
        from httpx_request import request
        _httpx_request = partial(
            request, 
            timeout=(5, 60, 60, 5), 
            raise_for_status=False, 
        )
    return _httpx_request


def default_parse(_, content: Buffer, /):
    try:
        if isinstance(content, (bytes, bytearray, memoryview)):
            return loads(content)
        else:
            return loads(memoryview(content))
    except JSONDecodeError:
        return content


def complete_url(
    path: str, 
    base_url: bool | str | Callable[[], str] = False, 
    path_prefix: bool | str | Callable[[], str] = False, 
    maybe_open: bool = True, 
) -> str:
    if path.startswith("//"):
        return "https:" + path
    elif path.startswith(("http://", "https://")):
        return path
    if base_url is True:
        base_url = API_URL
    elif base_url is False:
        base_url = WEB_URL
    elif callable(base_url):
        base_url = base_url()
    elif not base_url:
        base_url = WEB_URL
    if path_prefix:
        if path_prefix is True:
            if "/" not in path:
                path_prefix = "/family/file"
            elif path.startswith("file/"):
                path_prefix = "/family"
            else:
                path_prefix = ""
        else:
            if callable(path_prefix):
                path_prefix = path_prefix()
            if path_prefix := path_prefix.strip("/"):
                path_prefix = "/" + path_prefix
    elif path_prefix is False and maybe_open and "/" not in path:
        path_prefix = "/file"
    else:
        path_prefix = ""
    if path.startswith("api/"):
        path = "/" + path
    if not path.startswith("/"):
        if base_url.startswith(("http://api.", "https://api.")):
            if maybe_open and not path.startswith(("/", "portal/", "open/")):
                path_prefix = "/open" + path_prefix
        elif path.startswith(("/", "portal/", "open/")):
            path_prefix = "/api" + path_prefix
        elif maybe_open:
            path_prefix = "/api/open" + path_prefix
        path_prefix += "/"
    return base_url + path_prefix + path


@overload
def check_response(resp: dict, /) -> dict:
    ...
@overload
def check_response(resp: Awaitable[dict], /) -> Coroutine[Any, Any, dict]:
    ...
def check_response(resp: dict | Awaitable[dict], /) -> dict | Coroutine[Any, Any, dict]:
    """检测 189 的某个接口的响应，如果成功则直接返回，否则根据具体情况抛出一个异常，基本上是 OSError 的实例
    """
    def check(resp, /) -> dict:
        if not isinstance(resp, dict):
            raise P189OSError(EIO, resp)
        if "code" in resp:
            code = resp["code"]
            if code == "SUCCESS":
                return resp
            raise P189OSError(EIO, resp)
        if (get_first(resp, "errorCode", default="") or 
            int(get_first(resp, "res_code", "result", "status", default=0))
        ):
            raise P189OSError(EIO, resp)
        return resp
    if isawaitable(resp):
        async def check_await() -> dict:
            return check(await resp)
        return check_await()
    else:
        return check(resp)


class P189BaseClient(ABC):
    """电信天翼网盘客户端（基类）
    """
    def __init__(self, /):
        self.login()

    def __del__(self, /):
        self.close()

    @property
    def cookies(self, /):
        """请求所用的 Cookies 对象（同步和异步共用）
        """
        try:
            return self.__dict__["cookies"]
        except KeyError:
            from httpx import Cookies
            cookies = self.__dict__["cookies"] = Cookies()
            if "cookies_path" in self.__dict__:
                self._read_cookies()
            return cookies

    @cookies.setter
    def cookies(
        self, 
        cookies: None | str | Mapping[str, None | str] | Iterable[Mapping | Cookie | Morsel] = None, 
        /, 
    ):
        """更新 cookies
        """
        cookiejar = self.cookiejar
        if cookies is None:
            cookiejar.clear()
            return
        if isinstance(cookies, str):
            cookies = cookies.strip().rstrip(";")
            if not cookies:
                return
            cookies = cookies_str_to_dict(cookies.strip())
            if not cookies:
                return
        set_cookie = cookiejar.set_cookie
        clear_cookie = cookiejar.clear
        cookie: Mapping | Cookie | Morsel
        if isinstance(cookies, Mapping):
            if not cookies:
                return
            for key, val in iter_items(cookies):
                if val:
                    set_cookie(create_cookie(key, val, domain=".189.cn"))
                else:
                    for cookie in cookiejar:
                        if cookie.name == key:
                            clear_cookie(domain=cookie.domain, path=cookie.path, name=cookie.name)
                            break
        else:
            from httpx import Cookies
            if isinstance(cookies, Cookies):
                cookies = cookies.jar
            for cookie in cookies:
                set_cookie(create_cookie("", cookie))
        if "cookies_path" in self.__dict__:
            self._write_cookies()

    @property
    def cookiejar(self, /) -> CookieJar:
        """请求所用的 CookieJar 对象（同步和异步共用）
        """
        return self.cookies.jar

    @property
    def cookies_str(self, /) -> str:
        """所有 .189.com 域下的 cookie 值
        """
        return "; ".join(
            f"{cookie.name}={cookie.value}" 
            for cookie in self.cookiejar 
            if cookie.domain == "189.cn" or cookie.domain.endswith(".189.cn")
        )

    @property
    def headers(self, /) -> MutableMapping:
        """请求头，无论同步还是异步请求都共用这个请求头
        """
        try:
            return self.__dict__["headers"]
        except KeyError:
            from multidict import CIMultiDict
            headers = self.__dict__["headers"] = CIMultiDict({
                "accept": "application/json;charset=UTF-8", 
                "accept-encoding": "gzip, deflate", 
                "connection": "keep-alive", 
                "user-agent": "Mozilla/5.0 AppleWebKit/600 Safari/600 Chrome/124.0.0.0 Edg/124.0.0.0", 
            })
            return headers

    @locked_cacheproperty
    def session(self, /):
        """同步请求的 session 对象
        """
        import httpx_request
        from httpx import Client, HTTPTransport, Limits
        session = Client(
            limits=Limits(max_connections=256, max_keepalive_connections=64, keepalive_expiry=10), 
            transport=HTTPTransport(retries=5), 
            verify=False, 
        )
        setattr(session, "_headers", self.headers)
        if hasattr(self, "cookies"):
            setattr(session, "_cookies", self.cookies)
        return session

    @locked_cacheproperty
    def async_session(self, /):
        """异步请求的 session 对象
        """
        import httpx_request
        from httpx import AsyncClient, AsyncHTTPTransport, Limits
        session = AsyncClient(
            limits=Limits(max_connections=256, max_keepalive_connections=64, keepalive_expiry=10), 
            transport=AsyncHTTPTransport(retries=5), 
            verify=False, 
        )
        setattr(session, "_headers", self.headers)
        if hasattr(self, "cookies"):
            setattr(session, "_cookies", self.cookies)
        return session

    @locked_cacheproperty
    def access_token(self, /) -> str:
        resp = self.user_access_token()
        check_response(resp)
        return resp["accessToken"]

    def _read_cookies(
        self, 
        /, 
        encoding: str = "latin-1", 
    ) -> str:
        cookies_path = self.__dict__.get("cookies_path")
        if not cookies_path:
            return self.cookies_str
        try:
            with cookies_path.open("rb") as f:
                cookies = str(f.read(), encoding)
            set_cookie = self.cookiejar.set_cookie
            for key, val in cookies_str_to_dict(cookies.strip()).items():
                set_cookie(create_cookie(key, val, domain=".189.cn"))
            return cookies
        except OSError:
            return self.cookies_str

    def _write_cookies(
        self, 
        cookies: None | str = None, 
        /, 
        encoding: str = "latin-1", 
    ):
        cookies_path = self.__dict__.get("cookies_path")
        if not cookies_path:
            return
        if cookies is None:
            cookies = self.cookies_str
        cookies_bytes = bytes(cookies, encoding)
        with cookies_path.open("wb") as f:
            f.write(cookies_bytes)

    def close(self, /) -> None:
        """删除 session 和 async_session 属性，如果它们未被引用，则应该会被自动清理
        """
        self.__dict__.pop("session", None)
        self.__dict__.pop("async_session", None)

    def request(
        self, 
        /, 
        url: str, 
        method: str = "GET", 
        request: None | Callable = None, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ):
        """执行 HTTP 请求，默认为 GET 方法
        """
        request_kwargs.setdefault("parse", default_parse)
        request_kwargs.setdefault("raise_for_status", False)
        if request is None:
            request_kwargs["session"] = self.async_session if async_ else self.session
            return get_default_request()(
                url=url, 
                method=method, 
                async_=async_, 
                **request_kwargs, 
            )
        else:
            from multidict import CIMultiDict
            if headers := request_kwargs.get("headers"):
                request_kwargs["headers"] = CIMultiDict({**self.headers, **headers})
            else:
                request_kwargs["headers"] = CIMultiDict(self.headers)
            request_kwargs.setdefault("cookie", self.cookies_str)
            return request(
                url=url, 
                method=method, 
                **request_kwargs, 
            )

    @overload
    @abstractmethod
    def login(
        self, 
        /, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> Self:
        ...
    @overload
    @abstractmethod
    def login(
        self, 
        /, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, Self]:
        ...
    @abstractmethod
    def login(
        self, 
        /, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> Self | Coroutine[Any, Any, Self]:
        """扫码二维码登录
        """
        raise NotImplementedError

    ########## Login API ##########

    @overload
    @staticmethod
    def login_qrcode_conf(
        payload: dict | str = {"appKey": "cloud", "version": "2.0"}, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @staticmethod
    def login_qrcode_conf(
        payload: dict | str = {"appKey": "cloud", "version": "2.0"}, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @staticmethod
    def login_qrcode_conf(
        payload: dict | str = {"appKey": "cloud", "version": "2.0"}, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取二维码其它相关配置信息（支持 GET 和 POST）

        GET https://open.e.189.cn/api/logbox/oauth2/appConf.do

        :payload:
            - appId: str = <default>
            - version: str = <default>

        :headers:
            - lt: str    💡 来自 ``client.login_qrcode_url()``
            - reqId: str 💡 来自 ``client.login_qrcode_url()``
        """
        api = complete_url("/api/logbox/oauth2/appConf.do", base_url)
        if not isinstance(payload, dict):
            payload = {"appId": payload}
        request_kwargs.setdefault("parse", default_parse)
        if method.upper() == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        if request is None:
            request = get_default_request()
            request_kwargs["async_"] = async_
        return request(api, method=method, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_state(
        payload: dict, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @staticmethod
    def login_qrcode_state(
        payload: dict, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @staticmethod
    def login_qrcode_state(
        payload: dict, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取二维码扫码状态（支持 GET 和 POST）

        GET https://open.e.189.cn/api/logbox/oauth2/qrcodeLoginState.do

        :payload:
            - encryuuid: str 💡 来自 ``client.login_qrcode_uuid()``
            - uuid: str 💡 来自 ``client.login_qrcode_uuid()``
            - returnUrl: str 💡 来自 ``client.login_qrcode_conf()``
            - paramId: str 💡 来自 ``client.login_qrcode_conf()``
            - appId: str = "cloud"
            - clientType: int = 1
            - date: str = <default> 💡 默认值为 ``time.strftime("%Y-%m-%d%H:%M:%S", time.localtime()) + str(random.randrange(24))``
            - timeStamp: int | str = <default> 💡 默认值为 ``int(time.time()) * 1000``
            - cb_SaveName: str = "0"
            - isOauth2: "false" | "true" = "false"
            - state: str = ""

        :headers:
            - reqId: str    💡 来自 ``client.login_qrcode_conf()``
            - referer: str  💡 来自 ``client.login_qrcode_url()``，即其中的 "url" 字段
        """
        api = complete_url("/api/logbox/oauth2/qrcodeLoginState.do", base_url)
        request_kwargs.setdefault("parse", default_parse)
        now = datetime.now()
        payload = {
            "appId": "cloud", 
            "clientType": 1, 
            "date": now.strftime("%Y-%m-%d%H:%M:%S") + str(randrange(24)), 
            "timeStamp": int(now.timestamp()) * 1000, 
            "cb_SaveName": "0", 
            "isOauth2": "false", 
            "state": "", 
            **payload, 
        }
        if method.upper() == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        if request is None:
            request = get_default_request()
            request_kwargs["async_"] = async_
        return request(api, method=method, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_url(
        request: None | Callable = None, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @staticmethod
    def login_qrcode_url(
        request: None | Callable = None, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @staticmethod
    def login_qrcode_url(
        request: None | Callable = None, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取一些登录所需的参数

        GET https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https%3A%2F%2Fcloud.189.cn%2Fweb%2Fredirect.html&defaultSaveName=3&defaultSaveNameCheck=uncheck
        """
        api = "https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https%3A%2F%2Fcloud.189.cn%2Fweb%2Fredirect.html&defaultSaveName=3&defaultSaveNameCheck=uncheck"
        def parse(resp, _):
            url = str(resp.url)
            data = dict(parse_qsl(urlsplit(url).query))
            data["url"] = url
            return data
        request_kwargs.setdefault("parse", parse)
        if request is None:
            request = get_default_request()
            request_kwargs["async_"] = async_
        return request(api, **request_kwargs)

    @overload
    @staticmethod
    def login_qrcode_uuid(
        payload: dict | str = {"appId": "cloud"}, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @staticmethod
    def login_qrcode_uuid(
        payload: dict | str = {"appId": "cloud"}, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @staticmethod
    def login_qrcode_uuid(
        payload: dict | str = {"appId": "cloud"}, 
        /, 
        method = "GET", 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        request: None | Callable = None, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取二维码信息（支持 GET 和 POST）

        GET https://open.e.189.cn/api/logbox/oauth2/getUUID.do

        :payload:
            - appId: str = <default>
        """
        api = complete_url("/api/logbox/oauth2/getUUID.do", base_url)
        if not isinstance(payload, dict):
            payload = {"appId": payload}
        request_kwargs.setdefault("parse", default_parse)
        if method.upper() == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        if request is None:
            request = get_default_request()
            request_kwargs["async_"] = async_
        return request(api, method=method, **request_kwargs)

    @overload
    @staticmethod
    def login_session_pc(
        payload: dict | str, 
        /, 
        request: None | Callable = None, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @staticmethod
    def login_session_pc(
        payload: dict | str, 
        /, 
        request: None | Callable = None, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @staticmethod
    def login_session_pc(
        payload: dict | str, 
        /, 
        request: None | Callable = None, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 PC 端扫码登录后的信息

        GET https://cloud.189.cn/api/getSessionForPC.action

        :payload:
            - redirectURL: str
            - clientType: str = "TELEPC"
            - version: str = "1.0.0"
            - channelId: str = "web_cloud.189.cn"
        """
        api = "https://api.cloud.189.cn/getSessionForPC.action"
        if not isinstance(payload, dict):
            payload = {"redirectURL": payload}
        payload = {
            "clientType": "TELEPC", 
            "version": "1.0.0", 
            "channelId": "web_cloud.189.cn", 
            **payload, 
        }
        request_kwargs["headers"] = headers = dict(request_kwargs.get("headers") or ())
        headers.setdefault("accept", "application/json;charset=UTF-8")
        request_kwargs.setdefault("parse", default_parse)
        if request is None:
            request = get_default_request()
            request_kwargs["async_"] = async_
        return request(api, params=payload, **request_kwargs)

    @overload
    @staticmethod
    def login_unify_pc(
        payload: dict | int | str = 8025431004, 
        /, 
        request: None | Callable = None, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @staticmethod
    def login_unify_pc(
        payload: dict | int | str = 8025431004, 
        /, 
        request: None | Callable = None, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @staticmethod
    def login_unify_pc(
        payload: dict | int | str = 8025431004, 
        /, 
        request: None | Callable = None, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 PC 端登录相关的配置信息

        GET https://cloud.189.cn/api/portal/unifyLoginForPC.action

        :payload:
            - appId: int | str = 8025431004
            - clientType: int | str = 10020
            - returnURL: str = "https://m.cloud.189.cn/zhuanti/2020/loginErrorPc/index.html"
            - timeStamp: int | str = <default> 💡 时间戳，单位：毫秒
        """
        api = complete_url("api/portal/unifyLoginForPC.action")
        if not isinstance(payload, dict):
            payload = {"appId": payload}
        payload = {
            "appId": 8025431004, 
            "clientType": 10020, 
            "returnURL": "https://m.cloud.189.cn/zhuanti/2020/loginErrorPc/index.html", 
            "timeStamp": int(time() * 1000), 
            **payload, 
        }
        def parse(resp, content, /):
            globals_: dict = {}
            data = {"url": str(resp.url)}
            source = cast(Match, CRE_JS_unifyLoginForPC_search(content.decode("utf-8")))[0]
            for m in CRE_JS_NAME_DEF_finditer(source):
                exec(m[0].replace("\n", ""), globals_, data)
            return data
        request_kwargs.setdefault("parse", parse)
        if request is None:
            request = get_default_request()
            request_kwargs["async_"] = async_
        return request(api, params=payload, **request_kwargs)

    ########## User API ##########

    @overload
    def user_access_token(
        self, 
        payload: dict | str = {}, 
        /, 
        app_key: int | str = "600100422", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_access_token(
        self, 
        payload: dict | str = {}, 
        /, 
        app_key: int | str = "600100422", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_access_token(
        self, 
        payload: dict | str = {}, 
        /, 
        app_key: int | str = "600100422", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取 accessToken（有效期 1 个月）

        GET https://cloud.189.cn/api/open/oauth2/getAccessTokenBySsKey.action

        .. note::
            多次尝试可能获取同一个值，但是过期时间更新了

        :payload:
            - sessionKey: str
        """
        if isinstance(payload, dict):
            if "sessionKey" not in payload:
                payload = dict(payload, sessionKey=getattr(self, "session_key"))
        else:
            payload = {"sessionKey": payload}
        request_kwargs["headers"] = make_signed_headers(
            {"Appkey": str(app_key)}, 
            payload, 
            request_kwargs.get("headers")
        )
        return self.request(
            "https://cloud.189.cn/api/open/oauth2/getAccessTokenBySsKey.action", 
            params=payload, 
            async_=async_, 
            **request_kwargs, 
        )


# TODO: 这里有个 refreshToken，如何刷新
# TODO: 如何在不知道的情况下，用某个接口获取 sessionSecret
# TODO: 也支持 accessToken 获取数据，默认关闭
# TODO: 追平 P189Client 的接口，并且也要支持 portal 接口（必然使用 access_token）
class P189APIClient(P189BaseClient):
    """电信天翼网盘客户端 (用 SessionKey)
    """
    def __init__(
        self, 
        /, 
        session_data: None | dict | PathLike = None, 
        console_qrcode: bool = True, 
    ):
        if isinstance(session_data, PathLike):
            self.session_data_path = session_data
        elif session_data:
            self.session_data = session_data
        elif session_data is None:
            self.login(console_qrcode=console_qrcode)

    @property
    def refresh_token(self, /) -> str:
        return self.session_data["refreshToken"]

    @property
    def session_key(self, /) -> str:
        return self.session_data["sessionKey"]

    @property
    def session_secret(self, /) -> str:
        return self.session_data["sessionSecret"]

    @property
    def family_session_key(self, /) -> str:
        return self.session_data["familySessionKey"]

    @property
    def family_session_secret(self, /) -> str:
        return self.session_data["familySessionSecret"]

    @property
    def session_data(self, /) -> dict:
        try:
            return self.__dict__["session_data"]
        except KeyError:
            if "session_data_path" in self.__dict__:
                return self._read_session_data()
            else:
                self.login()
                return self.__dict__["session_data"]

    @session_data.setter
    def session_data(self, session_data: dict, /):
        self.__dict__["session_data"] = session_data
        if "session_data_path" in self.__dict__:
            self._write_session_data(session_data)

    def _read_session_data(self, /):
        session_data_path = self.__dict__.get("session_data_path")
        if not session_data_path:
            return self.__dict__["session_data"]
        try:
            with session_data_path.open("rb") as f:
                session_data = loads(f.read())
            self.session_data = session_data
            return session_data
        except OSError:
            return self.__dict__["session_data"]

    def _write_session_data(self, session_data, /):
        session_data_path = self.__dict__.get("session_data_path")
        if not session_data_path:
            return
        if session_data is None:
            session_data = self.session_data
        data = dumps(session_data)
        with session_data_path.open("wb") as f:
            f.write(data)

    @overload
    def login(
        self, 
        /, 
        console_qrcode: bool = True, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> Self:
        ...
    @overload
    def login(
        self, 
        /, 
        console_qrcode: bool = True, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, Self]:
        ...
    def login(
        self, 
        /, 
        console_qrcode: bool = True, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> Self | Coroutine[Any, Any, Self]:
        """扫码二维码登录
        """
        def gen_step():
            resp = yield self.login_with_qrcode(
                console_qrcode=console_qrcode, 
                async_=async_, 
                **request_kwargs, 
            )
            check_response(resp)
            self.session_data = resp
        return run_gen_step(gen_step, async_)

    def request_with_sign(
        self, 
        /, 
        api, 
        method: str = "GET", 
        payload: None | dict = None, 
        payload_key: str = "", 
        use_access_token: bool | str | dict = False, 
        **request_kwargs, 
    ):
        method = method.upper()
        if payload_key:
            request_kwargs[payload_key] = payload
        elif method == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        will_use_access_token = bool(isinstance(use_access_token, dict) or use_access_token)
        url = complete_url(
            api, 
            base_url=True, 
            path_prefix=bool(payload and "familyId" in payload), 
            maybe_open=will_use_access_token, 
        )
        if will_use_access_token:
            if use_access_token is True:
                use_access_token = self.access_token
            request_kwargs["headers"] = make_signed_headers(
                cast(dict | str, use_access_token), 
                payload, 
                request_kwargs.get("headers"), 
            )
        else:
            if payload and "familyId" in payload:
                session_key = self.session_key
                session_secret = self.session_secret
            else:
                session_key = self.family_session_key
                session_secret = self.family_session_secret
            request_kwargs["headers"] = make_hmac_signed_headers(
                session_key, 
                session_secret, 
                url, 
                method=method, 
                headers=request_kwargs.get("headers"), 
            )
        return self.request(url, method, **request_kwargs)

    @overload
    @classmethod
    def login_with_qrcode(
        cls, 
        /, 
        console_qrcode: bool = True, 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @classmethod
    def login_with_qrcode(
        cls, 
        /, 
        console_qrcode: bool = True, 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @classmethod
    def login_with_qrcode(
        cls, 
        /, 
        console_qrcode: bool = True, 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """二维码扫码登录

        :param console_qrcode: 在命令行输出二维码，否则在浏览器中打开
        :param base_url: 接口的基地址
        :param async_: 是否异步
        :param request_kwargs: 其它请求参数

        :return: 接口响应
        """
        def gen_step():
            headers = dict(request_kwargs.pop("headers", None) or ())
            conf = yield cls.login_unify_pc(
                headers=headers, 
                async_=async_, 
                **request_kwargs, 
            )
            resp = yield cls.login_qrcode_uuid(
                {"appId": 8025431004}, 
                base_url=base_url, 
                headers=headers, 
                async_=async_, 
                **request_kwargs, 
            )
            check_response(resp)
            encryuuid = resp["encryuuid"]
            uuid = resp["uuid"]
            if console_qrcode:
                from qrcode import QRCode # type: ignore
                qr = QRCode(border=1)
                qr.add_data(uuid)
                qr.print_ascii(tty=isatty(1))
            else:
                url = complete_url("/api/logbox/oauth2/image.do?uuid="+quote(uuid, safe=""), base_url)
                if async_:
                    from startfile import startfile_async
                    yield startfile_async(url)
                else:
                    from startfile import startfile
                    startfile(url)
            while True:
                resp = yield cls.login_qrcode_state(
                    {
                        "appId": 8025431004, 
                        "encryuuid": encryuuid, 
                        "uuid": uuid, 
                        "returnUrl": "https://m.cloud.189.cn/zhuanti/2020/loginErrorPc/index.html", 
                        "paramId": conf["paramId"], 
                    }, 
                    headers={**headers, "lt": conf["lt"], "reqid": conf["reqId"], "referer": conf["url"]}, 
                )
                match get_first(resp, "status", "result"):
                    case -106:
                        print("\r\x1b[K[status=-106] qrcode: waiting", end="")
                    case -11002:
                        print("\r\x1b[K[status=-11002] qrcode: scanned", end="")
                    case 0:
                        print("\r\x1b[K[status=0] qrcode: signed in", end="")
                        break
                    case -20099:
                        raise P189LoginError(EAUTH, "[status=-1] qrcode: expired")
                    case _:
                        raise P189LoginError(EAUTH, f"qrcode: aborted with {resp!r}")
            return cls.login_session_pc(
                resp["redirectUrl"], 
                headers=headers, 
                async_=async_, 
                **request_kwargs, 
            )
        return run_gen_step(gen_step, async_)

    ########## File System API ##########

    @overload
    def fs_list(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_list(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_list(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://api.cloud.189.cn/listFiles.action

        :payload:
            - folderId: int | str = "" 💡 所在目录 id

                - -10: 私密空间根目录
                - -11: 根目录
                - -12: 我的图片
                - -13: 我的音乐
                - -14: 我的视频
                - -15: 我的文档
                - -16: 我的应用
                -   0: 同步盘根目录

            - pageNum: int = 1    💡 第几页
            - pageSize: int = 100 💡 一页大小
            - flag: int = <default>
            - iconOption: int = <default>
            - mediaAttr: int = <default>
            - mediaType: int = <default> 💡 文件类型

                - 0: 全部（all）
                - 1: 图片（picture）
                - 2: 音乐（music）
                - 3: 视频（video）
                - 4: 文档（txt）

            - orderBy: int | str = <default> 💡 排序依据

                - "filename": 文件名
                - "filesize": 文件大小
                - "lastOpTime": 更新时间
                - "createDate": 上传时间

            - descending: "false" | "true" = <default> 💡 是否降序（从大到小）
            - needPath: "false" | "true" = <default>
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"folderId": payload}
        payload = {"pageNum": 1, "pageSize": 100, **payload}
        if "familyId" not in payload:
            payload.setdefault("folderId", -11)
        return self.request_with_sign(
            "listFiles.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )


# TODO: 如果 cookies 从文件中获取，但是文件不存在或里面为空，则可能需要扫码登录
# TODO: 批量创建目录，2 种办法
# TODO: 删除等操作还有其它方法，非 batch
class P189Client(P189BaseClient):
    """电信天翼网盘客户端

    .. note::
        支持 2 种请求方式：

        1. 不需要签名：请求头用 "Cookie"
        2. 需要签名：请求头用 "AccessToken"
    """
    def __init__(
        self, 
        /, 
        cookies: None | str | PathLike | Mapping[str, str] | Iterable[Mapping | Cookie | Morsel] = None, 
        console_qrcode: bool = True, 
    ):
        if isinstance(cookies, PathLike):
            self.cookies_path = cookies
        elif cookies:
            self.cookies = cookies
        elif cookies is None:
            self.login(console_qrcode=console_qrcode)

    @locked_cacheproperty
    def session_key(self, /) -> str:
        resp = self.user_info_brief()
        check_response(resp)
        return resp["sessionKey"]

    @locked_cacheproperty
    def upload_rsakey(self, /) -> dict:
        resp = self.upload_generate_rsakey()
        check_response(resp)
        return resp

    @locked_cacheproperty
    def upload_rsa_pubkey(self, /) -> str:
        return self.upload_rsakey["pubKey"]

    @property
    def upload_rsa_pkid(self, /) -> str:
        rsakey = self.upload_rsakey
        if (time() + 60) * 1000 > rsakey["expire"]:
            self.__dict__.pop("upload_rsakey", None)
            rsakey = self.upload_rsakey
        return rsakey["pkId"]

    def request_with_sign(
        self, 
        /, 
        api, 
        method: str = "GET", 
        payload: None | dict = None, 
        payload_key: str = "", 
        use_access_token: bool | str | dict = False, 
        **request_kwargs, 
    ):
        method = method.upper()
        if payload_key:
            request_kwargs[payload_key] = payload
        elif method == "POST":
            request_kwargs["data"] = payload
        else:
            request_kwargs["params"] = payload
        will_use_access_token = bool(isinstance(use_access_token, dict) or use_access_token)
        url = complete_url(
            api, 
            base_url=will_use_access_token, 
            path_prefix=bool(payload and "familyId" in payload), 
        )
        if will_use_access_token:
            if use_access_token is True:
                use_access_token = self.access_token
            request_kwargs["headers"] = make_signed_headers(
                cast(dict | str, use_access_token), 
                payload, 
                request_kwargs.get("headers"), 
            )
        return self.request(url, method, **request_kwargs)

    @overload
    def login(
        self, 
        /, 
        console_qrcode: bool = True, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> Self:
        ...
    @overload
    def login(
        self, 
        /, 
        console_qrcode: bool = True, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, Self]:
        ...
    def login(
        self, 
        /, 
        console_qrcode: bool = True, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> Self | Coroutine[Any, Any, Self]:
        """扫码二维码登录
        """
        def gen_step():
            resp = yield self.login_with_qrcode(
                console_qrcode=console_qrcode, 
                async_=async_, 
                **request_kwargs, 
            )
            setattr(self, "cookies", resp["cookie"])
            return self
        return run_gen_step(gen_step, async_)

    @overload
    @classmethod
    def login_with_qrcode(
        cls, 
        /, 
        console_qrcode: bool = True, 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    @classmethod
    def login_with_qrcode(
        cls, 
        /, 
        console_qrcode: bool = True, 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    @classmethod
    def login_with_qrcode(
        cls, 
        /, 
        console_qrcode: bool = True, 
        base_url: str | Callable[[], str] = "https://open.e.189.cn", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """二维码扫码登录

        :param console_qrcode: 在命令行输出二维码，否则在浏览器中打开
        :param base_url: 接口的基地址
        :param async_: 是否异步
        :param request_kwargs: 其它请求参数

        :return: 接口响应
        """
        def gen_step():
            headers = dict(request_kwargs.pop("headers", None) or ())
            resp = yield cls.login_qrcode_uuid(
                base_url=base_url, 
                headers=headers, 
                async_=async_, 
                **request_kwargs, 
            )
            check_response(resp)
            encryuuid = resp["encryuuid"]
            uuid = resp["uuid"]
            conf = yield cls.login_qrcode_url(
                headers=headers, 
                async_=async_, 
                **request_kwargs, 
            )
            resp = yield cls.login_qrcode_conf(
                headers={**headers, "lt": conf["lt"], "reqId": conf["reqId"]}, 
                async_=async_, 
                **request_kwargs, 
            )
            data = resp["data"]
            if console_qrcode:
                from qrcode import QRCode # type: ignore
                qr = QRCode(border=1)
                qr.add_data(uuid)
                qr.print_ascii(tty=isatty(1))
            else:
                from startfile import startfile, startfile_async
                url = complete_url("/api/logbox/oauth2/image.do?uuid="+quote(uuid, safe=""), base_url)
                if async_:
                    yield startfile_async(url)
                else:
                    startfile(url)
            while True:
                resp = yield cls.login_qrcode_state(
                    {
                        "encryuuid": encryuuid, 
                        "uuid": uuid, 
                        "returnUrl": quote(data["returnUrl"], safe=""), 
                        "paramId": data["paramId"], 
                    }, 
                    headers={**headers, "reqid": data["reqId"], "referer": conf["url"]}, 
                )
                match get_first(resp, "status", "result"):
                    case -106:
                        print("\r\x1b[K[status=-106] qrcode: waiting", end="")
                    case -11002:
                        print("\r\x1b[K[status=-11002] qrcode: scanned", end="")
                    case 0:
                        print("\r\x1b[K[status=0] qrcode: signed in", end="")
                        break
                    case -20099:
                        raise P189LoginError(EAUTH, "[status=-1] qrcode: expired")
                    case _:
                        raise P189LoginError(EAUTH, f"qrcode: aborted with {resp!r}")
            for key in ("allow_redirects", "follow_redirects", "redirect"):
                request_kwargs[key] = False
            request_kwargs["parse"] = ...
            request = request_kwargs.get("request")
            if request is None:
                request = get_default_request()
                request_kwargs["async_"] = async_
            resp = yield request(resp["redirectUrl"], **request_kwargs)
            cookie = resp.headers["set-cookie"]
            return {
                "result": 0, 
                "cookie": dict(a.partition(";")[0].split("=", 1) for a in cookie.split(", ")), 
                "url": resp.headers["location"], 
            }
        return run_gen_step(gen_step, async_)

    ########## Download API ##########

    @overload
    def download_url(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> str:
        ...
    @overload
    def download_url(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, str]:
        ...
    def download_url(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> str | Coroutine[Any, Any, str]:
        """从网盘（个人文件）或家庭共享中获取下载链接

        :param payload: 请求参数
        :param use_access_token: 是否使用 "AccessToken" 进行请求
        :param async_: 是否异步
        :param request_kwargs: 其它请求参数

        :return: 下载链接
        """
        def gen_step():
            resp = yield self.download_url_info(
                payload, 
                use_access_token=use_access_token, 
                async_=async_, 
                **request_kwargs, 
            )
            check_response(resp)
            return unescape(resp["fileDownloadUrl"])
        return run_gen_step(gen_step, async_)

    @overload
    def download_url_info(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def download_url_info(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def download_url_info(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取下载链接

        GET https://cloud.189.cn/api/open/file/getFileDownloadUrl.action

        :payload:
            - fileId: int | str 💡 文件 id
            - short: "true" | "false" = <default>
            - dt: int = <default>
            - forcedGet: "true" | "false" = <default>
            - type: int = <default>
            - familyId: int | str = <default> 💡 家庭共享 id
            - shareId: int | str = <defaylt>  💡 分享 id
        """
        if not isinstance(payload, dict):
            payload = {"fileId": payload}
        return self.request_with_sign(
            "file/getFileDownloadUrl.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def download_url_video(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def download_url_video(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def download_url_video(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频下载链接

        GET https://cloud.189.cn/api/open/file/getNewVlcVideoPlayUrl.action

        :payload:
            - fileId: int | str 💡 文件 id
            - type: int = <default>
            - familyId: int | str = <default> 💡 家庭共享 id
            - shareId: int | str = <defaylt>  💡 分享 id
            - dt: int = <default>
        """
        if not isinstance(payload, dict):
            payload = {"fileId": payload}
        if "type" not in payload:
            if "familyId" in payload:
                payload["type"] = 1
            elif "shareId" in payload:
                payload["type"] = 4
            else:
                payload["type"] = 2
        return self.request_with_sign(
            "file/getNewVlcVideoPlayUrl.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def download_url_video_portal(
        self, 
        payload: dict | int | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def download_url_video_portal(
        self, 
        payload: dict | int | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def download_url_video_portal(
        self, 
        payload: dict | int | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取视频下载链接

        GET https://cloud.189.cn/api/portal/getNewVlcVideoPlayUrl.action

        :payload:
            - fileId: int | str 💡 文件 id
            - type: int = <default>
            - familyId: int | str = <default> 💡 家庭共享 id
            - shareId: int | str = <defaylt>  💡 分享 id
        """
        if not isinstance(payload, dict):
            payload = {"fileId": payload}
        if "type" not in payload:
            if "familyId" in payload:
                payload["type"] = 1
            elif "shareId" in payload:
                payload["type"] = 4
            else:
                payload["type"] = 2
        return self.request_with_sign(
            "portal/getNewVlcVideoPlayUrl.action", 
            method, 
            payload, 
            async_=async_, 
            **request_kwargs, 
        )

    ########## File System API ##########

    @overload
    def fs_batch(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_batch(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_batch(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量操作文件

        POST https://cloud.189.cn/api/open/batch/createBatchTask.action

        :payload:
            - type: str 💡 操作类型

                - "COPY": 复制
                - "MOVE": 移动
                - "DELETE": 删除（移入回收站）
                - "RESTORE": 还原（移出回收站，回到原来的地方）
                - "CLEAR_RECYCLE": 彻底删除（从回收站删除）
                - "EMPTY_RECYCLE": 清空回收站
                - "SHARE_SAVE": 转存

            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] = <default> 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,   # 文件 id
                        "fileName"?: str,      # 文件名
                        "isFolder"?: 0 | 1,    # 是否目录
                        "isConflict"?: 0 | 1,  # 是否冲突
                        "srcParentId"?: 0 | 1, # 来源父目录 id
                        "dealWay"?: int,       # 处理冲突的策略：1:忽略 2:保留两者 3:替换
                    }

            - targetFolderId: int = <default> 💡 目标目录 id
            - familyId: int | str = <default> 💡 家庭共享 id
            - shareId: int | str = <default>  💡 分享 id
            - copyType: int = <default>
            - opScene: int = <default>
        """
        if not (
            isinstance(payload, dict) and 
            ("taskInfos" in payload or "targetFolderId" in payload)
        ):
            payload = {"taskInfos": payload}
        if "taskInfos" in payload:
            taskInfos = payload["taskInfos"]
            if not (isinstance(taskInfos, str) and taskInfos.startswith("[")):
                def encode(info, /) -> dict:
                    if isinstance(info, (int, str)):
                        return {"fileId": info, "fileName": "."}
                    elif isinstance(info, tuple):
                        fid, name, *_ = taskInfos
                        return {"fileId": fid, "fileName": name or "."}
                    else:
                        if not isinstance(info, dict):
                            info = dict(info)
                        info["fileName"] = info.get("fileName") or "."
                        return info
                if isinstance(taskInfos, (int, tuple, dict)):
                    taskInfos = [encode(taskInfos)]
                else:
                    taskInfos = list(map(encode, taskInfos))
                payload["taskInfos"] = dumps(taskInfos).decode("utf-8")
        return self.request_with_sign(
            "batch/createBatchTask.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_batch_cancel(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_batch_cancel(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_batch_cancel(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """查询任务中冲突项的信息

        POST https://cloud.189.cn/api/open/batch/cancelBatchTask.action

        :payload:
            - taskId: int | str 💡 任务 id
            - type: str 💡 操作类型
        """
        return self.request_with_sign(
            "batch/cancelBatchTask.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_batch_check(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_batch_check(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_batch_check(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """查询任务状态

        POST https://cloud.189.cn/api/open/batch/checkBatchTask.action

        .. note::
            返回值中，"taskStatus" 字段表示任务状态，目前已知：

            - -1: 参数错误
            -  2: 失败
            -  3: 运行中
            -  4: 完成（也可能失败）

        :payload:
            - taskId: int | str 💡 任务 id
            - type: str 💡 操作类型
        """
        return self.request_with_sign(
            "batch/checkBatchTask.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_batch_conflict(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_batch_conflict(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_batch_conflict(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """查询任务中冲突项的信息

        POST https://cloud.189.cn/api/open/batch/getConflictTaskInfo.action

        :payload:
            - taskId: int | str 💡 任务 id
            - type: str 💡 操作类型
        """
        return self.request_with_sign(
            "batch/getConflictTaskInfo.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_batch_manage(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_batch_manage(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_batch_manage(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """重新提交任务（往往用于处理冲突项）

        POST https://cloud.189.cn/api/open/batch/manageBatchTask.action

        :payload:
            - taskId: int | str 💡 任务 id
            - type: str
            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] = <default> 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,   # 文件 id
                        "fileName"?: str,      # 文件名
                        "isFolder"?: 0 | 1,    # 是否目录
                        "isConflict"?: 0 | 1,  # 是否冲突
                        "srcParentId"?: 0 | 1, # 来源父目录 id
                        "dealWay"?: int,       # 处理冲突的策略：1:忽略 2:保留两者 3:替换
                    }

            - targetFolderId: int = <default> 💡 目标目录 id
        """
        if not (
            isinstance(payload, dict) and 
            ("taskInfos" in payload or "targetFolderId" in payload)
        ):
            payload = {"taskInfos": payload}
        if "taskInfos" in payload:
            taskInfos = payload["taskInfos"]
            if not (isinstance(taskInfos, str) and taskInfos.startswith("[")):
                def encode(info, /) -> dict:
                    if isinstance(info, (int, str)):
                        return {"fileId": info, "fileName": "."}
                    elif isinstance(info, tuple):
                        fid, name, *_ = taskInfos
                        return {"fileId": fid, "fileName": name or "."}
                    else:
                        if not isinstance(info, dict):
                            info = dict(info)
                        info["fileName"] = info.get("fileName") or "."
                        return info
                if isinstance(taskInfos, (int, tuple, dict)):
                    taskInfos = [encode(taskInfos)]
                else:
                    taskInfos = list(map(encode, taskInfos))
                payload["taskInfos"] = dumps(taskInfos).decode("utf-8")
        return self.request_with_sign(
            "batch/manageBatchTask.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_clear_recycle(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_clear_recycle(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_clear_recycle(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量彻底删除（从回收站删除），此接口是对 `fs_batch` 的封装

        :payload:
            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,  # 文件 id
                        "fileName"?: str,     # 文件名
                        "isFolder"?: 0 | 1,   # 是否目录
                    }

            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not (
            isinstance(payload, dict) and 
            ("taskInfos" in payload or "targetFolderId" in payload)
        ):
            payload = {"taskInfos": payload}
        payload["type"] = "CLEAR_RECYCLE"
        return self.fs_batch(
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_copy(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_copy(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_copy(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量复制，此接口是对 `fs_batch` 的封装

        :payload:
            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,   # 文件 id
                        "fileName"?: str,      # 文件名
                        "isFolder"?: 0 | 1,    # 是否目录
                        "isConflict"?: 0 | 1,  # 是否冲突
                        "srcParentId"?: 0 | 1, # 来源父目录 id
                        "dealWay"?: int,       # 处理冲突的策略：1:忽略 2:保留两者 3:替换
                    }

            - targetFolderId: int = <default> 💡 目标目录 id
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not (
            isinstance(payload, dict) and 
            ("taskInfos" in payload or "targetFolderId" in payload)
        ):
            payload = {"taskInfos": payload}
        payload["type"] = "COPY"
        return self.fs_batch(
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_delete(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_delete(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_delete(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量删除（移入回收站），此接口是对 `fs_batch` 的封装

        :payload:
            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,  # 文件 id
                        "fileName"?: str,     # 文件名
                        "isFolder"?: 0 | 1,   # 是否目录
                    }

            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not (
            isinstance(payload, dict) and 
            ("taskInfos" in payload or "targetFolderId" in payload)
        ):
            payload = {"taskInfos": payload}
        payload["type"] = "DELETE"
        return self.fs_batch(
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_dirs(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_dirs(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_dirs(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录列表（仅获取目录节点）

        GET https://cloud.189.cn/api/open/file/getObjectFolderNodes.action

        :payload:
            - id: int | str = <default> 💡 所在目录 id

                - -10: 私密空间根目录
                - -11: 根目录
                - -12: 我的图片
                - -13: 我的音乐
                - -14: 我的视频
                - -15: 我的文档
                - -16: 我的应用
                -   0: 同步盘根目录

            - orderBy: int | str = 1
            - order: "ASC" | "DESC" = "ASC"
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"id": payload}
        payload = {"orderBy": 1, "order": "ASC", **payload}
        return self.request_with_sign(
            "open/file/getObjectFolderNodes.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_dirs_portal(
        self, 
        payload: dict | int | str = -11, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_dirs_portal(
        self, 
        payload: dict | int | str = -11, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_dirs_portal(
        self, 
        payload: dict | int | str = -11, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录列表（仅获取目录节点）

        GET https://cloud.189.cn/api/portal/getObjectFolderNodes.action

        :payload:
            - id: int | str = <default> 💡 所在目录 id

                - -10: 私密空间根目录
                - -11: 根目录
                - -12: 我的图片
                - -13: 我的音乐
                - -14: 我的视频
                - -15: 我的文档
                - -16: 我的应用
                -   0: 同步盘根目录

            - orderBy: int | str = 1
            - order: "ASC" | "DESC" = "ASC"
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"id": payload}
        payload = {"orderBy": 1, "order": "ASC", **payload}
        return self.request_with_sign(
            "portal/getObjectFolderNodes.action", 
            method, 
            payload, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_empty_recycle(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_empty_recycle(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_empty_recycle(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """清空回收站，此接口是对 `fs_batch` 的封装

        :payload:
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if isinstance(payload, dict):
            payload = payload.copy()
        else:
            payload = {"familyId": payload}
        payload["type"] = "EMPTY_RECYCLE"
        return self.fs_batch(
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_family_from(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_family_from(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_family_from(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """个人文件转存至家庭共享

        GET https://api.cloud.189.cn/open/family/file/shareFileToFamily.action

        :payload:
            - familyId: int | str   💡 家庭共享 id
            - fileIdList: int | str 💡 文件 id 列表，多个用逗号,隔开
        """
        return self.request_with_sign(
            "family/file/shareFileToFamily.action", 
            method, 
            payload, 
            use_access_token=True, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_family_list(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_family_list(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_family_list(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取家庭分享列表

        GET https://api.cloud.189.cn/open/family/manage/getFamilyList.action
        """
        return self.request_with_sign(
            "family/manage/getFamilyList.action", 
            method, 
            use_access_token=True, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_family_to(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_family_to(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_family_to(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """家庭共享的文件转存至个人文件

        GET https://api.cloud.189.cn/open/family/manage/saveFileToMember.action

        :payload:
            - familyId: int | str   💡 家庭共享 id
            - fileIdList: int | str 💡 文件 id 列表，多个用逗号,隔开
        """
        return self.request_with_sign(
            "family/manage/saveFileToMember.action", 
            method, 
            payload, 
            use_access_token=True, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_folder_info(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_folder_info(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_folder_info(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取目录信息

        GET https://cloud.189.cn/api/open/file/getFolderInfo.action

        :payload:
            - folderId: int | str 💡 文件或目录 id
            - familyId: int | str = <default> 💡 家庭共享 id
            - module: str = <default>
        """
        if not isinstance(payload, dict):
            payload = {"folderId": payload}
        return self.request_with_sign(
            "file/getFolderInfo.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_info(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_info(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_info(
        self, 
        payload: dict | int | str = -11, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件信息

        GET https://cloud.189.cn/api/open/file/getFileInfo.action

        :payload:
            - fileId: int | str 💡 文件或目录 id
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"fileId": payload}
        return self.request_with_sign(
            "file/getFileInfo.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_info_portal(
        self, 
        payload: dict | int | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_info_portal(
        self, 
        payload: dict | int | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_info_portal(
        self, 
        payload: dict | int | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件信息

        GET https://cloud.189.cn/api/portal/getFileInfo.action

        .. note::
            这个接口返回的信息更详细

        :payload:
            - fileId: int | str 💡 文件或目录 id
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"fileId": payload}
        return self.request_with_sign(
            "portal/getFileInfo.action", 
            method, 
            payload, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_list(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_list(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_list(
        self, 
        payload: dict | int | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/open/file/listFiles.action

        :payload:
            - folderId: int | str = "" 💡 所在目录 id

                - -10: 私密空间根目录
                - -11: 根目录
                - -12: 我的图片
                - -13: 我的音乐
                - -14: 我的视频
                - -15: 我的文档
                - -16: 我的应用
                -   0: 同步盘根目录

            - pageNum: int = 1    💡 第几页
            - pageSize: int = 100 💡 一页大小
            - flag: int = <default>
            - iconOption: int = <default>
            - mediaAttr: int = <default>
            - mediaType: int = <default> 💡 文件类型

                - 0: 全部（all）
                - 1: 图片（picture）
                - 2: 音乐（music）
                - 3: 视频（video）
                - 4: 文档（txt）

            - orderBy: int | str = <default> 💡 排序依据

                - "filename": 文件名
                - "filesize": 文件大小
                - "lastOpTime": 更新时间
                - "createDate": 上传时间

            - descending: "false" | "true" = <default> 💡 是否降序（从大到小）
            - needPath: "false" | "true" = <default>
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"folderId": payload}
        payload = {"pageNum": 1, "pageSize": 100, **payload}
        if "familyId" not in payload:
            payload.setdefault("folderId", -11)
        return self.request_with_sign(
            "file/listFiles.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_list_portal(
        self, 
        payload: dict | int | str = -11, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_list_portal(
        self, 
        payload: dict | int | str = -11, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_list_portal(
        self, 
        payload: dict | int | str = -11, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/portal/listFiles.action

        .. note::
            这个接口返回的信息更详细，并且包含下载链接

        :payload:
            - fileId: int | str 💡 所在目录 id

                - -10: 私密空间根目录
                - -11: 根目录
                - -12: 我的图片
                - -13: 我的音乐
                - -14: 我的视频
                - -15: 我的文档
                - -16: 我的应用
                -   0: 同步盘根目录

            - pageNum: int = 1    💡 第几页
            - pageSize: int = 100 💡 一页大小
            - iconOption: int = <default>
            - mediaAttr: int = <default>
            - mediaType: int = <default> 💡 文件类型

                - 0: 全部（all）
                - 1: 图片（picture）
                - 2: 音乐（music）
                - 3: 视频（video）
                - 4: 文档（txt）

            - orderBy: int = <default>
            - order: "ASC" | "DESC" = <default>
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"fileId": payload}
        payload = {"fileId": "", "pageNum": 1, "pageSize": 100, **payload}
        return self.request_with_sign(
            "portal/listFiles.action", 
            method, 
            payload, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_mkdir(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_mkdir(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_mkdir(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """新建目录

        POST https://cloud.189.cn/api/open/file/createFolder.action

        :payload:
            - folderName: str 💡 创建的目录名
            - parentFolderId: int | str = <default> 💡 所在目录 id
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"folderName": payload}
        return self.request_with_sign(
            "file/createFolder.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_move(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_move(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_move(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量移动，此接口是对 `fs_batch` 的封装

        :payload:
            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,   # 文件 id
                        "fileName"?: str,      # 文件名
                        "isFolder"?: 0 | 1,    # 是否目录
                        "isConflict"?: 0 | 1,  # 是否冲突
                        "srcParentId"?: 0 | 1, # 来源父目录 id
                        "dealWay"?: int,       # 处理冲突的策略：1:忽略 2:保留两者 3:替换
                    }

            - targetFolderId: int = <default> 💡 目标目录 id
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not (
            isinstance(payload, dict) and 
            ("taskInfos" in payload or "targetFolderId" in payload)
        ):
            payload = {"taskInfos": payload}
        payload["type"] = "MOVE"
        return self.fs_batch(
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_recyclebin_list(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_recyclebin_list(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_recyclebin_list(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/open/file/listRecycleBinFiles.action

        :payload:
            - pageNum: int = 1    💡 第几页
            - pageSize: int = 100 💡 一页大小
            - iconOption: int = <default>
            - family: "false" | "true" = "false" 💡 是否在家庭共享
        """
        if not isinstance(payload, dict):
            payload = {"pageNum": payload}
        payload = {"pageNum": 1, "pageSize": 100, "family": "false", **payload}
        return self.request_with_sign(
            "file/listRecycleBinFiles.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_recyclebin_list_v3(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_recyclebin_list_v3(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_recyclebin_list_v3(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/open/file/listRecycleBinFilesV3.action

        :payload:
            - pageNum: int = 1    💡 第几页
            - pageSize: int = 100 💡 一页大小
            - iconOption: int = <default>
            - family: "false" | "true" = "false" 💡 是否在家庭共享
        """
        if not isinstance(payload, dict):
            payload = {"pageNum": payload}
        payload = {"pageNum": 1, "pageSize": 100, "family": "false", **payload}
        return self.request_with_sign(
            "file/listRecycleBinFilesV3.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_recyclebin_list_v3_portal(
        self, 
        payload: dict | int = 1, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_recyclebin_list_v3_portal(
        self, 
        payload: dict | int = 1, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_recyclebin_list_v3_portal(
        self, 
        payload: dict | int = 1, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/portal/listRecycleBinFilesV3.action

        .. note::
            这个接口返回的信息更详细，并且包含下载链接

        :payload:
            - pageNum: int = 1    💡 第几页
            - pageSize: int = 100 💡 一页大小
            - iconOption: int = <default>
            - family: "false" | "true" = "false" 💡 是否在家庭共享
        """
        if not isinstance(payload, dict):
            payload = {"pageNum": payload}
        payload = {"pageNum": 1, "pageSize": 100, "family": "false", **payload}
        return self.request_with_sign(
            "portal/listRecycleBinFilesV3.action", 
            method, 
            payload, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_rename_dir(
        self, 
        payload: dict | tuple[int | str, str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_rename_dir(
        self, 
        payload: dict | tuple[int | str, str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_rename_dir(
        self, 
        payload: dict | tuple[int | str, str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """重命名目录

        POST https://cloud.189.cn/api/open/file/renameFolder.action

        :payload:
            - folderId: int | str 💡 目录的 id
            - destFolderName: str 💡 改动后的名字
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            fid, name, *_ = payload
            payload = {"folderId": fid, "destFolderName": name}
        return self.request_with_sign(
            "file/renameFolder.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_rename_file(
        self, 
        payload: dict | tuple[int | str, str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_rename_file(
        self, 
        payload: dict | tuple[int | str, str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_rename_file(
        self, 
        payload: dict | tuple[int | str, str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """重命名文件

        POST https://cloud.189.cn/api/open/file/renameFile.action

        :payload:
            - fileId: int | str 💡 目录的 id
            - destFileName: str 💡 改动后的名字
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            fid, name, *_ = payload
            payload = {"fileId": fid, "destFileName": name}
        return self.request_with_sign(
            "file/renameFile.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_restore(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_restore(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_restore(
        self, 
        payload: dict | str | int | tuple[int | str, str] | Iterable[int | str | tuple[int | str, str] | dict], 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量还原（移出回收站，回到原来的地方），此接口是对 `fs_batch` 的封装

        :payload:
            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,   # 文件 id
                        "fileName"?: str,      # 文件名
                        "isFolder"?: 0 | 1,    # 是否目录
                        "isConflict"?: 0 | 1,  # 是否冲突
                        "srcParentId"?: 0 | 1, # 来源父目录 id
                        "dealWay"?: int,       # 处理冲突的策略：1:忽略 2:保留两者 3:替换
                    }

            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not (
            isinstance(payload, dict) and 
            ("taskInfos" in payload or "targetFolderId" in payload)
        ):
            payload = {"taskInfos": payload}
        payload["type"] = "RESTORE"
        return self.fs_batch(
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def fs_search(
        self, 
        payload: dict | str = ".", 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def fs_search(
        self, 
        payload: dict | str = ".", 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def fs_search(
        self, 
        payload: dict | str = ".", 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/open/file/searchFiles.action

        :payload:
            - filename: str = "." 💡 搜索的文件名
            - folderId: int | str = "" 💡 所在目录 id

                - -10: 私密空间根目录
                - -11: 根目录
                - -12: 我的图片
                - -13: 我的音乐
                - -14: 我的视频
                - -15: 我的文档
                - -16: 我的应用
                -   0: 同步盘根目录

            - pageNum: int = 1    💡 第几页
            - pageSize: int = 100 💡 一页大小
            - iconOption: int = 5
            - mediaType: int = 0  💡 文件类型

                - 0: 全部（all）
                - 1: 图片（picture）
                - 2: 音乐（music）
                - 3: 视频（video）
                - 4: 文档（txt）

            - orderBy: int | str = "lastOpTime" 💡 排序依据

                - "filename": 文件名
                - "filesize": 文件大小
                - "lastOpTime": 更新时间
                - "createDate": 上传时间

            - descending: "false" | "true" = "true" 💡 是否降序（从大到小）
            - recursive: 0 | 1 = 0 💡 是否递归搜索：0:在当前目录中搜索 1:在全部文件中搜索
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        if not isinstance(payload, dict):
            payload = {"filename": payload}
        payload = {
            "filename": ".", "folderId": "", "pageNum": 1, "pageSize": 100, 
            "iconOption": 5, "mediaType": 0, "orderBy": "lastOpTime", 
            "descending": "true", "recursive": 0, **payload, 
        }
        return self.request_with_sign(
            "file/searchFiles.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    ########## Share API ##########

    @overload
    def share_cancel(
        self, 
        payload: dict | int | str | Iterable[int | str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_cancel(
        self, 
        payload: dict | int | str | Iterable[int | str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_cancel(
        self, 
        payload: dict | int | str | Iterable[int | str], 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """取消分享

        POST https://cloud.189.cn/api/portal/cancelShare.action

        :payload:
            - shareIdList: int | str 💡 分享 id，多个用逗号,隔开
            - cancelType: int = <default> 💡 取消类型
        """
        if not isinstance(payload, dict):
            if isinstance(payload, (int, str)):
                payload = {"shareIdList": payload}
            else:
                payload = {"shareIdList": ",".join(map(str, payload))}
        return self.request_with_sign(
            "portal/cancelShare.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_create(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_create(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_create(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """创建分享

        POST https://cloud.189.cn/api/open/share/createShareLink.action

        :payload:
            - fileId: int | str      💡 文件或目录的 id
            - shareType: int = 3     💡 分享类型

                - 1: 社交分享（会生成分享码，但可以忽略）
                - 2: 公开分享（暂不可用）
                - 3: 私密分享（只有输入访问码才能查看）
                - 4: 社交分享（相当于 1）
                - 5: 发布资源（发布资源到个人主页后，您的订阅者即可浏览、转存资源）

            - expireTime: int = 2099 💡 有效期，单位：天
        """
        if not isinstance(payload, dict):
            payload = {"fileId": payload}
        payload = {"shareType": 3, "expireTime": 2099, **payload}
        return self.request_with_sign(
            "share/createShareLink.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_create_batch(
        self, 
        payload: dict | int | str | Iterable[int | str], 
        /, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_create_batch(
        self, 
        payload: dict | int | str | Iterable[int | str], 
        /, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_create_batch(
        self, 
        payload: dict | int | str | Iterable[int | str], 
        /, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """创建批量分享

        POST https://cloud.189.cn/api/open/share/createBatchShare.action

        :payload:
            - fileIdList: list[int]  💡 文件或目录的 id 的列表
            - shareType: int = 3     💡 分享类型

                - 1: 社交分享（会生成分享码，但可以忽略）
                - 2: 公开分享（暂不可用）
                - 3: 私密分享（只有输入访问码才能查看）
                - 4: 社交分享（相当于 1）
                - 5: 发布资源（发布资源到个人主页后，您的订阅者即可浏览、转存资源）

            - expireTime: int = 2099 💡 有效期，单位：天
        """
        if isinstance(payload, (int, str)):
            payload = {"fileIdList": [payload]}
        elif not isinstance(payload, dict):
            if not isinstance(payload, (list, tuple)):
                payload = list(payload)
            payload = {"fileIdList": payload}
        payload = {"shareType": 3, "expireTime": 2099, **payload}
        return self.request(
            complete_url("share/createBatchShare.action"), 
            "POST", 
            json=payload, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_fs_list(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_fs_list(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_fs_list(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取分享中的文件列表

        GET https://cloud.189.cn/api/open/share/listShareDir.action

        :payload:
            - shareId: int | str 💡 分享 id
            - isFolder: "false" | "true" = "true" 💡 是不是目录
            - accessCode: str = <default> 💡 访问码
            - fileId: int | str = <default> 💡 文件 id
            - shareMode: int = <default> 💡 分享模式
            - pageNum: int = 1 💡 第几页
            - pageSize: int = 100 💡 一页大小
            - iconOption: int = <default>
            - orderBy: int | str = <default> 💡 排序依据

                - "filename": 文件名
                - "filesize": 文件大小
                - "lastOpTime": 更新时间
                - "createDate": 上传时间

            - descending: "false" | "true" = <default> 💡 是否降序（从大到小）
        """
        payload = {"pageNum": 1, "pageSize": 100, "isFolder": "true", **payload}
        if payload.get("isFolder") == "true":
            payload.setdefault("fileId", payload["shareId"])
        if payload.get("accessCode"):
            payload.setdefault("shareMode", 1)
        else:
            payload.setdefault("shareMode", 3)
        return self.request_with_sign(
            "share/listShareDir.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_info(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_info(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_info(
        self, 
        payload: dict | int | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/portal/getShareInfo.action

        :payload:
            - shareId: int | str 💡 分享 id
        """
        if not isinstance(payload, dict):
            payload = {"shareId": payload}
        return self.request_with_sign(
            "portal/getShareInfo.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_info_by_code(
        self, 
        payload: dict | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_info_by_code(
        self, 
        payload: dict | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_info_by_code(
        self, 
        payload: dict | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/open/share/getShareInfoByCode.action

        :payload:
            - shareCode: str 💡 分享码，可以包含访问码
        """
        if not isinstance(payload, dict):
            payload = {"shareCode": payload}
        return self.request_with_sign(
            "share/getShareInfoByCode.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_info_by_code_v2(
        self, 
        payload: dict | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_info_by_code_v2(
        self, 
        payload: dict | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_info_by_code_v2(
        self, 
        payload: dict | str, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/open/share/getShareInfoByCodeV2.action

        :payload:
            - shareCode: str 💡 分享码，可以包含访问码
        """
        if not isinstance(payload, dict):
            payload = {"shareCode": payload}
        return self.request_with_sign(
            "share/getShareInfoByCodeV2.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_last_save_path(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_last_save_path(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_last_save_path(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/open/getLastSavePath.action

        :payload:
            - shareCode: str 💡 分享码，可以包含访问码
        """
        return self.request_with_sign(
            "getLastSavePath.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_list(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_list(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_list(
        self, 
        payload: dict | int = 1, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取文件列表

        GET https://cloud.189.cn/api/portal/listShares.action

        :payload:
            - pageNum: int = 1     💡 第几页
            - pageSize: int = 100  💡 一页大小
            - shareType: 1 | 2 = 1 💡 分享类型：1:发出的分享 2:收到的分享
        """
        if not isinstance(payload, dict):
            payload = {"pageNum": payload}
        payload = {"pageNum": 1, "pageSize": 100, "shareType": 1, **payload}
        return self.request_with_sign(
            "portal/listShares.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def share_save(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def share_save(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def share_save(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """批量转存（来自分享），此接口是对 `fs_batch` 的封装

        :payload:
            - shareId: int | str 💡 分享 id
            - taskInfos: str | int | tuple[int | str, str] | FileInfo | Iterable[int | str | tuple[int | str, str] | FileInfo] 💡 操作对象列表

                .. code:: python

                    FileInfo = {
                        "fileId": int | str,   # 文件 id
                        "fileName"?: str,      # 文件名
                        "isFolder"?: 0 | 1,    # 是否目录
                        "isConflict"?: 0 | 1,  # 是否冲突
                        "srcParentId"?: 0 | 1, # 来源父目录 id
                        "dealWay"?: int,       # 处理冲突的策略：1:忽略 2:保留两者 3:替换
                    }

            - familyId: int | str = <default> 💡 家庭共享 id
        """
        payload["type"] = "SHARE_SAVE"
        return self.fs_batch(
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    ########## Upload API ##########

    @overload
    def _upload_request(
        self, 
        api: str, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def _upload_request(
        self, 
        api: str, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def _upload_request(
        self, 
        api: str, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        if api.startswith(("http://", "https://")):
            url = api
        elif "familyId" in payload:
            url = "https://upload.cloud.189.cn/family/" + api
        else:
            url = "https://upload.cloud.189.cn/person/" + api
        params, request_kwargs["headers"] = make_encrypted_params_headers(
            self.session_key, 
            self.upload_rsa_pubkey, 
            self.upload_rsa_pkid, 
            url=url, 
            method=method, 
            payload=payload, 
            headers=request_kwargs.get("headers"), 
        )
        if method.upper() == "POST":
            request_kwargs["data"] = params
        else:
            request_kwargs["params"] = params
        return self.request(url, method, async_=async_, **request_kwargs)

    @overload
    def upload_generate_rsakey(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_generate_rsakey(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_generate_rsakey(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取上传时加密参数所用的 RSA 公钥和私钥 id（1 小时内有效）

        GET https://cloud.189.cn/api/open/security/generateRsaKey.action
        """
        return self.request_with_sign(
            "security/generateRsaKey.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_init(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_init(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_init(
        self, 
        payload: dict, 
        /, 
        use_access_token: bool = False, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化上传任务

        GET https://cloud.189.cn/api/open/file/createUploadFile.action

        .. caution::
            这个接口的响应，会返回上传的链接和提交的链接，但是使用时需要签名，需要用到 "SessionSecret"

        :payload:
            **上传到个人文件所需字段**

            - md5: str
            - size: int
            - parentFolderId: int | str = <default>

            **上传到家庭共享所需字段**

            - fileMd5: str
            - fileSize: str
            - parentId: int | str = <default>
            - familyId: int | str = <default> 💡 家庭共享 id

            **公共字段**

            - fileName: str = <default>
            - flag: int = <default>
            - opertype: 1 | 2 | 3 = <default> 💡 处理同名冲突的策略：1:保留两者 2:忽略 3:替换
            - isLog: 0 | 1 = <default>
            - resumePolicy: int = 1
        """
        payload = {"fileName": str(uuid4()), "resumePolicy": 1, **payload}
        return self.request_with_sign(
            "file/createUploadFile.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_init_portal(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_init_portal(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_init_portal(
        self, 
        payload: dict, 
        /, 
        method: str = "POST", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化上传任务

        GET https://cloud.189.cn/api/createUploadFile.action

        .. caution::
            这个接口的响应，会返回上传的链接和提交的链接，但是使用时需要签名，需要用到 "SessionSecret"

        :payload:
            **上传到个人文件所需字段**

            - md5: str
            - size: int
            - parentFolderId: int | str = <default>

            **上传到家庭共享所需字段**

            - fileMd5: str
            - fileSize: str
            - parentId: int | str = <default>
            - familyId: int | str = <default> 💡 家庭共享 id

            **公共字段**

            - fileName: str = <default>
            - flag: int = <default>
            - opertype: 1 | 2 | 3 = <default> 💡 处理同名冲突的策略：1:保留两者 2:忽略 3:替换
            - isLog: 0 | 1 = <default>
            - resumePolicy: int = 1
        """
        payload = {"fileName": str(uuid4()), "resumePolicy": 1, **payload}
        return self.request_with_sign(
            "api/createUploadFile.action", 
            method, 
            payload, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_multipart_commit(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_multipart_commit(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_multipart_commit(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """提交分块上传事务

        GET https://upload.cloud.189.cn/person/commitMultiUploadFile

        :payload:
            - uploadFileId: str 💡 上传任务 id
            - opertype: 1 | 2 | 3 = <default> 💡 处理同名冲突的策略：1:保留两者 2:忽略 3:替换
            - fileMd5: str = <default>  💡 文件 MD5
            - sliceMd5: str = <default> 💡 文件的以分块方式计算的 MD5，计算方式为

                .. code:: python

                    from binascii import hexlify
                    from collections.abc import Buffer
                    from functools import partial
                    from hashlib import md5
                    from itertools import pairwise
                    from os import PathLike

                    def calc_slice_md5(file, slice_size=10485760):
                        if isinstance(file, Buffer):
                            m = memoryview(file)
                            chunks = (m[l:r] for l, r in pairwise(range(0, len(m)+slice_size, slice_size)))
                        else:
                            if isinstance(file, (str, PathLike)):
                                file = open(file, "rb")
                            chunks = iter(partial(file.read, slice_size), b"")
                        i = 0
                        first_md5 = ""
                        for i, chunk in enumerate(chunks, 1):
                            hashval = md5(chunk).digest()
                            if i > 1:
                                if i == 2:
                                    hashobj = md5()
                                    update = hashobj.update
                                    update(first_md5.upper().encode("ascii"))
                                else:
                                    update(b"\n")
                                update(hexlify(hashval).upper())
                            else:
                                first_md5 = hashval.hex()
                        if i == 0:
                            return "d41d8cd98f00b204e9800998ecf8427e"
                        elif i == 1:
                            return first_md5
                        else:
                            return hashobj.hexdigest()

            - lazyCheck: 0 | 1 = <default> 💡 是否延迟检查
        """
        return self._upload_request(
            "commitMultiUploadFile", 
            payload, 
            method=method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_multipart_init(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_multipart_init(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_multipart_init(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """初始化分块上传任务

        GET https://upload.cloud.189.cn/person/initMultiUpload

        .. note::
            如果响应数据中的字段 "fileDataExists" 值为 1，则说明秒传成功

        :payload:
            - fileSize: int 💡 文件大小
            - fileMd5: str  💡 文件 MD5
            - fileName: str 💡 文件名 = <default>
            - sliceSize: int = 10485760 💡 分块大小，默认为 10 MB
            - sliceMd5: str = <default> 💡 文件的以分块方式计算的 MD5，计算方式为

                .. code:: python

                    from binascii import hexlify
                    from collections.abc import Buffer
                    from functools import partial
                    from hashlib import md5
                    from itertools import pairwise
                    from os import PathLike

                    def calc_slice_md5(file, slice_size=10485760):
                        if isinstance(file, Buffer):
                            m = memoryview(file)
                            chunks = (m[l:r] for l, r in pairwise(range(0, len(m)+slice_size, slice_size)))
                        else:
                            if isinstance(file, (str, PathLike)):
                                file = open(file, "rb")
                            chunks = iter(partial(file.read, slice_size), b"")
                        i = 0
                        first_md5 = ""
                        for i, chunk in enumerate(chunks, 1):
                            hashval = md5(chunk).digest()
                            if i > 1:
                                if i == 2:
                                    hashobj = md5()
                                    update = hashobj.update
                                    update(first_md5.upper().encode("ascii"))
                                else:
                                    update(b"\n")
                                update(hexlify(hashval).upper())
                            else:
                                first_md5 = hashval.hex()
                        if i == 0:
                            return "d41d8cd98f00b204e9800998ecf8427e"
                        elif i == 1:
                            return first_md5
                        else:
                            return hashobj.hexdigest()

            - parentFolderId: int | str = "" 💡 父目录 id
            - lazyCheck: 0 | 1 = <default> 💡 是否延迟检查。也就是不提供文件的 MD5 信息而先上传，等待会检查计算完成，再进行二次检查
            - familyId: int | str = <default> 💡 家庭共享 id
        """
        payload = {"sliceSize": 10485760, "fileName": str(uuid4()), **payload}
        if "fileMd5" not in payload:
            payload.setdefault("lazyCheck", 1)
        if "familyId" not in payload:
            payload.setdefault("parentFolderId", -11)
        try:
            if int(payload["fileSize"]) <= int(payload["sliceSize"]):
                payload.setdefault("sliceMd5", payload["fileMd5"])
        except (KeyError, TypeError):
            pass
        return self._upload_request(
            "initMultiUpload", 
            payload, 
            method=method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_multipart_list_parts(
        self, 
        payload: dict | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_multipart_list_parts(
        self, 
        payload: dict | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_multipart_list_parts(
        self, 
        payload: dict | str, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """罗列已上传的分块信息

        GET https://upload.cloud.189.cn/person/getUploadedPartsInfo

        :payload:
            - uploadFileId: str 💡 上传任务 id
        """
        if not isinstance(payload, dict):
            payload = {"uploadFileId": payload}
        return self._upload_request(
            "getUploadedPartsInfo", 
            payload, 
            method=method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_multipart_second_check(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_multipart_second_check(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_multipart_second_check(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """分块上传时，延迟提交的二次验证，返回结果等于 ``client.upload_multipart_init({"lazyCheck": 0})``

        GET https://upload.cloud.189.cn/person/checkTransSecond

        :payload:
            - uploadFileId: str 💡 上传任务 id
            - fileMd5: str  💡 文件 MD5
            - sliceMd5: str = <default> 💡 文件的以分块方式计算的 MD5，计算方式为

                .. code:: python

                    from binascii import hexlify
                    from collections.abc import Buffer
                    from functools import partial
                    from hashlib import md5
                    from itertools import pairwise
                    from os import PathLike

                    def calc_slice_md5(file, slice_size=10485760):
                        if isinstance(file, Buffer):
                            m = memoryview(file)
                            chunks = (m[l:r] for l, r in pairwise(range(0, len(m)+slice_size, slice_size)))
                        else:
                            if isinstance(file, (str, PathLike)):
                                file = open(file, "rb")
                            chunks = iter(partial(file.read, slice_size), b"")
                        i = 0
                        first_md5 = ""
                        for i, chunk in enumerate(chunks, 1):
                            hashval = md5(chunk).digest()
                            if i > 1:
                                if i == 2:
                                    hashobj = md5()
                                    update = hashobj.update
                                    update(first_md5.upper().encode("ascii"))
                                else:
                                    update(b"\n")
                                update(hexlify(hashval).upper())
                            else:
                                first_md5 = hashval.hex()
                        if i == 0:
                            return "d41d8cd98f00b204e9800998ecf8427e"
                        elif i == 1:
                            return first_md5
                        else:
                            return hashobj.hexdigest()
        """
        return self._upload_request(
            "checkTransSecond", 
            payload, 
            method=method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_multipart_url(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_multipart_url(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_multipart_url(
        self, 
        payload: dict, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取执行分块上传的 url

        GET https://upload.cloud.189.cn/person/getMultiUploadUrls

        .. note::
            会返回上传所用的 url 以及所需携带的请求头，并需要你用 PUT 方法执行上传请求

        :payload:
            - uploadFileId: str 💡 上传任务 id
            - partInfo: str     💡 分块信息，格式为 f"{分块编号}-{分块的 MD5 的 base64 表示}"，例如 "1-x8KLqbSGxCsT7yP+qmOcvA=="
        """
        return self._upload_request(
            "getMultiUploadUrls", 
            payload, 
            method=method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def upload_file(
        self, 
        /, 
        file: ( str | PathLike | URL | SupportsGeturl | 
                Buffer | SupportsRead[Buffer] | Iterable[Buffer] | AsyncIterable[Buffer] ), 
        file_md5: str = "", 
        slice_md5: str = "", 
        file_name: str = "", 
        file_size: int = -1, 
        parent_id: int | str = "", 
        family_id: int | str = "", 
        lazy_check: bool = False, 
        opertype: Literal[1, 2, 3] = 2, 
        upload_file_id: None | str = None, 
        slice_size: int = 10485760, 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def upload_file(
        self, 
        /, 
        file: ( str | PathLike | URL | SupportsGeturl | 
                Buffer | SupportsRead[Buffer] | Iterable[Buffer] | AsyncIterable[Buffer] ), 
        file_md5: str = "", 
        slice_md5: str = "", 
        file_name: str = "", 
        file_size: int = -1, 
        parent_id: int | str = "", 
        family_id: int | str = "", 
        lazy_check: bool = False, 
        opertype: Literal[1, 2, 3] = 2, 
        upload_file_id: None | str = None, 
        slice_size: int = 10485760, 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def upload_file(
        self, 
        /, 
        file: ( str | PathLike | URL | SupportsGeturl | 
                Buffer | SupportsRead[Buffer] | Iterable[Buffer] | AsyncIterable[Buffer] ), 
        file_md5: str = "", 
        slice_md5: str = "", 
        file_name: str = "", 
        file_size: int = -1, 
        parent_id: int | str = "", 
        family_id: int | str = "", 
        lazy_check: bool = False, 
        opertype: Literal[1, 2, 3] = 3, 
        upload_file_id: None | str = None, 
        slice_size: int = 10485760, 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """上传文件

        .. attention::
            如果文件名里面包含 emoji 符号，则会报错。建议先用 UUID 为名把文件传上去，然后再进行改名即可

        :param file: 待上传的文件

            - 如果为 ``collections.abc.Buffer``，则作为二进制数据上传
            - 如果为 ``filewrap.SupportsRead``，则作为可读的二进制文件上传
            - 如果为 ``str`` 或 ``os.PathLike``，则视为路径，打开后作为文件上传
            - 如果为 ``yarl.URL`` 或 ``http_request.SupportsGeturl`` (``pip install python-http_request``)，则视为超链接，打开后作为文件上传
            - 如果为 ``collections.abc.Iterable[collections.abc.Buffer]`` 或 ``collections.abc.AsyncIterable[collections.abc.Buffer]``，则迭代以获取二进制数据，逐步上传

        :param file_md5: 文件的 MD5 散列值
        :param slice_md5: 文件的以分块方式计算的 MD5，计算方式为

            .. code:: python

                from binascii import hexlify
                from collections.abc import Buffer
                from functools import partial
                from hashlib import md5
                from itertools import pairwise
                from os import PathLike

                def calc_slice_md5(file, slice_size=10485760):
                    if isinstance(file, Buffer):
                        m = memoryview(file)
                        chunks = (m[l:r] for l, r in pairwise(range(0, len(m)+slice_size, slice_size)))
                    else:
                        if isinstance(file, (str, PathLike)):
                            file = open(file, "rb")
                        chunks = iter(partial(file.read, slice_size), b"")
                    i = 0
                    first_md5 = ""
                    for i, chunk in enumerate(chunks, 1):
                        hashval = md5(chunk).digest()
                        if i > 1:
                            if i == 2:
                                hashobj = md5()
                                update = hashobj.update
                                update(first_md5.upper().encode("ascii"))
                            else:
                                update(b"\n")
                            update(hexlify(hashval).upper())
                        else:
                            first_md5 = hashval.hex()
                    if i == 0:
                        return "d41d8cd98f00b204e9800998ecf8427e"
                    elif i == 1:
                        return first_md5
                    else:
                        return hashobj.hexdigest()

        :param file_name: 文件名
        :param file_size: 文件大小
        :param parent_id: 要上传的目标目录
        :param family_id: 家庭共享 id
        :param lazy_check: 是否延迟上传。当缺失 ``file_md5`` 或 ``slice_md5``，如果为 True，则先尝试计算这些值，再进行上传，否则直接上传，等提交时再补全信息
        :param opertype: 处理同名冲突的策略：1:保留两者 2:忽略 3:替换
        :param upload_file_id: 上传任务 id，可用于断点续传
        :param slice_size: 分块大小，默认为 10 MB
        :param async_: 是否异步
        :param request_kwargs: 其它请求参数

        :return: 接口响应
        """
        convert_block = lambda b: hexlify(b).upper()
        def calc_slice_md5(file, slice_size=10485760):
            if isinstance(file, Buffer):
                m = memoryview(file)
                chunks: Iterator[Buffer] = (m[l:r] for l, r in pairwise(range(0, len(m)+slice_size, slice_size)))
            else:
                if isinstance(file, (str, PathLike)):
                    file = open(file, "rb")
                chunks = iter(partial(file.read, slice_size), b"")
            i = 0
            first_md5 = ""
            for i, chunk in enumerate(chunks, 1):
                hashval = md5(chunk).digest()
                if i > 1:
                    if i == 2:
                        hashobj = md5()
                        update = hashobj.update
                        update(first_md5.upper().encode("ascii"))
                    else:
                        update(b"\n")
                    update(hexlify(hashval).upper())
                else:
                    first_md5 = hashval.hex()
            if i == 0:
                return "d41d8cd98f00b204e9800998ecf8427e"
            elif i == 1:
                return first_md5
            else:
                return hashobj.hexdigest()
        if file_size == 0:
            file_md5 = slice_md5 = "d41d8cd98f00b204e9800998ecf8427e"
        elif 0 < file_size <= slice_size:
            if file_md5:
                slice_md5 = file_md5
            elif slice_md5:
                file_md5 = slice_md5
        def gen_step():
            nonlocal file, file_md5, slice_md5, file_name, file_size, upload_file_id
            next_slice_no = 1
            uploaded_ok = False
            if upload_file_id:
                resp = yield self.upload_multipart_list_parts(
                    upload_file_id, 
                    async_=async_, 
                    **request_kwargs, 
                )
                check_response(resp)
                uploaded_part_list_str = resp["data"]["uploadedPartList"]
                if uploaded_part_list_str:
                    uploaded_part_list = list(map(int, uploaded_part_list_str.split(",")))
                    last_part_no = uploaded_part_list[-1]
                    if last_part_no != len(uploaded_part_list):
                        raise RuntimeError(f"temporarily unable to handle discontinuous uploaded parts: {uploaded_part_list!r}")
                    next_slice_no = last_part_no + 1
                uploaded_ok = 0 <= file_size <= slice_size * (next_slice_no - 1)
            elif file_size >= 0 and file_md5 and slice_md5:
                params = {
                    "fileMd5": file_md5, 
                    "fileName": quote(file_name or str(uuid4())), 
                    "fileSize": file_size, 
                    "sliceMd5": slice_md5, 
                    "sliceSize": slice_size, 
                    "lazyCheck": 0, 
                }
                if parent_id != "":
                    params["parentFolderId"] = parent_id
                if family_id != "":
                    params["family_id"] = family_id
                resp = yield self.upload_multipart_init(
                    params, 
                    async_=async_, 
                    **request_kwargs, 
                )
                check_response(resp)
                data = resp["data"]
                upload_file_id = data["uploadFileId"]
                uploaded_ok = data["fileDataExists"]
            if not uploaded_ok:
                hashobj: HashObj
                try:
                    file = getattr(file, "getbuffer")()
                except (AttributeError, TypeError):
                    pass
                skip_size = slice_size * (next_slice_no - 1)
                if isinstance(file, Buffer):
                    file_size = buffer_length(file)
                    if file_size == 0:
                        file_md5 = slice_md5 = "d41d8cd98f00b204e9800998ecf8427e"
                    if not lazy_check:
                        if not file_md5:
                            if slice_md5:
                                if file_size <= slice_size:
                                    file_md5 = slice_md5
                                else:
                                    file_md5 = md5(file).hexdigest()
                            elif file_size <= slice_size:
                                file_md5 = md5(file).hexdigest()
                                slice_md5 = file_md5
                            else:
                                hashobj = ChunkedHash(file, block_size=slice_size, sep=b"\n", convert_block=convert_block)
                                file_md5 = hashobj.hexdigest_total()
                                if file_size <= slice_size:
                                    slice_md5 = file_md5
                                else:
                                    slice_md5 = hashobj.hexdigest()
                        elif not slice_md5:
                            slice_md5 = calc_slice_md5(file)
                    if skip_size:
                        file = memoryview(file)[skip_size:]
                    file = bytes_to_chunk_iter(file, slice_size)
                else:
                    if isinstance(file, (str, PathLike)):
                        path = fsdecode(file)
                        if not file_name:
                            file_name = basename(path)
                        file = open(path, "rb")
                    elif isinstance(file, (URL, SupportsGeturl)):
                        if isinstance(file, URL):
                            url = str(file)
                        else:
                            url = file.geturl()
                        if async_:
                            from httpfile import AsyncHttpxFileReader
                            file = yield AsyncHttpxFileReader.new(url)
                        else:
                            from httpfile import HTTPFileReader
                            file = HTTPFileReader(url)
                    skipped = not skip_size
                    if isinstance(file, SupportsRead):
                        seek = getattr(file, "seek", None)
                        seekable = False
                        curpos = 0
                        if callable(seek):
                            if async_:
                                seek = ensure_async(seek, threaded=True)
                            try:
                                seekable = getattr(file, "seekable")()
                            except (AttributeError, TypeError):
                                try:
                                    curpos = yield seek(0, 1)
                                    seekable = True
                                except Exception:
                                    seekable = False
                        if not file_name:
                            file_name = basename(getattr(file, "name", ""))
                        if file_size < 0:
                            try:
                                fileno = getattr(file, "fileno")()
                                file_size = fstat(fileno).st_size - curpos
                            except (AttributeError, TypeError, OSError):
                                if size := getattr(file, "length", -1) >= 0:
                                    file_size = size - curpos
                                else:
                                    try:
                                        file_size = len(file) - curpos # type: ignore
                                    except TypeError:
                                        if seekable:
                                            try:
                                                file_size = (yield cast(Callable, seek)(0, 2)) - curpos
                                            finally:
                                                yield cast(Callable, seek)(curpos)
                        if file_size == 0:
                            file_md5 = slice_md5 = "d41d8cd98f00b204e9800998ecf8427e"
                        elif 0 < file_size <= slice_size:
                            if file_md5:
                                slice_md5 = file_md5
                            elif slice_md5:
                                file_md5 = slice_md5
                        if not lazy_check and not (file_md5 and slice_md5) and seekable:
                            try:
                                if 0 < file_size <= slice_size:
                                    if async_:
                                        file_size, hashobj = yield file_digest_async(file)
                                    else:
                                        file_size, hashobj = file_digest(file)
                                    file_md5 = slice_md5 = hashobj.hexdigest()
                                else:
                                    hashobj = ChunkedHash(block_size=slice_size, sep=b"\n", convert_block=convert_block)
                                    if async_:
                                        yield file_digest_async(file, hashobj)
                                    else:
                                        file_digest(file, hashobj)
                                    file_size = hashobj.count_read
                                    file_md5  = hashobj.hexdigest_total()
                                    if file_size <= slice_size:
                                        slice_md5 = file_md5
                                    else:
                                        slice_md5 = hashobj.hexdigest()
                            finally:
                                if exc_info()[0] or skipped:
                                    yield cast(Callable, seek)(curpos)
                        if not skipped and seekable:
                            yield cast(Callable, seek)(curpos + skip_size)
                            skipped = True
                    else:
                        if async_:
                            file = bytes_iter_to_async_reader(file) # type: ignore
                        else:
                            file = bytes_iter_to_reader(file) # type: ignore
                    if not skipped:
                        if async_:
                            yield through(bio_skip_async_iter(file, skip_size)) # type: ignore
                        else:
                            through(bio_skip_iter(file, skip_size)) # type: ignore
                    if async_:
                        file = bio_chunk_async_iter(file, chunksize=slice_size) # type: ignore
                    else:
                        file = bio_chunk_iter(file, chunksize=slice_size) # type: ignore
                file = cast(Iterable[Buffer] | AsyncIterable[Buffer], file)
                if not upload_file_id:
                    # TODO: 初始化上传任务时，文件大小是必要的，当未能获得文件大小时，则先把文件保存到临时文件（同时可以把哈希值计算出来），再执行后续操作
                    if file_size < 0:
                        raise RuntimeError("unable to get file size without consuming the file")
                    params = {
                        "fileSize": file_size, 
                        "fileMd5": file_md5, 
                        "fileName": quote(file_name or str(uuid4())), 
                        "sliceSize": slice_size, 
                        "sliceMd5": slice_md5, 
                        "lazyCheck": int(not (file_md5 and slice_md5)), 
                    }
                    if parent_id != "":
                        params["parentFolderId"] = parent_id
                    if family_id != "":
                        params["family_id"] = family_id
                    resp = yield self.upload_multipart_init(
                        params, 
                        async_=async_, 
                        **request_kwargs, 
                    )
                    check_response(resp)
                    data = resp["data"]
                    upload_file_id = data["uploadFileId"]
                    uploaded_ok = data["fileDataExists"]
                if not uploaded_ok:
                    is_lazy_check = next_slice_no == 1 and not (file_md5 and slice_md5)
                    with with_iter_next(file) as get_next:
                        while True:
                            chunk = yield get_next()
                            part_md5 = md5(chunk)
                            if is_lazy_check:
                                if next_slice_no == 1:
                                    file_hashobj = part_md5
                                    file_md5 = slice_md5 = file_hashobj.hexdigest()
                                else:
                                    if next_slice_no == 2:
                                        slice_hashobj = md5(hexlify(file_hashobj.digest()).upper())
                                    else:
                                        slice_hashobj.update(b"\n")
                                    file_hashobj.update(chunk)
                                    slice_hashobj.update(hexlify(part_md5.digest()).upper())
                                    file_md5 = file_hashobj.hexdigest()
                                    slice_md5 = slice_hashobj.hexdigest()
                            slice_md5_b64 = b64encode(bytes.fromhex(part_md5.hexdigest())).decode("ascii")
                            resp = yield self.upload_multipart_url(
                                {"uploadFileId": upload_file_id, "partInfo": f"{next_slice_no}-{slice_md5_b64}"}, 
                                async_=async_, 
                                **request_kwargs, 
                            )
                            check_response(resp)
                            upload_data = resp["uploadUrls"][f"partNumber_{next_slice_no}"]
                            upload_url = upload_data["requestURL"]
                            upload_headers = {k: unquote(v) for k, v in headers_str_to_dict(
                                upload_data["requestHeader"], kv_sep="=", entry_sep="&").items()}
                            resp = yield self.request(
                                upload_url, 
                                "PUT", 
                                data=chunk, 
                                headers=upload_headers, 
                                async_=async_, 
                                **request_kwargs, 
                            )
                            if isinstance(resp, dict):
                                check_response(resp)
                            next_slice_no += 1
            resp = yield self.upload_multipart_commit(
                {
                    "uploadFileId": upload_file_id, 
                    "opertype": opertype, 
                    "fileMd5": file_md5, 
                    "sliceMd5": slice_md5, 
                    "lazyCheck": int(bool(file_md5 and slice_md5)), 
                }, 
                async_=async_, 
                **request_kwargs, 
            )
            check_response(resp)
            return resp
        return run_gen_step(gen_step, async_)

    ########## User API ##########

    @overload
    def user_get(
        self, 
        payload: dict | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_get(
        self, 
        payload: dict | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_get(
        self, 
        payload: dict | str = {}, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户信息（基本信息）

        GET https://cloud.189.cn/api/open/subscribe/getUser.action

        :payload:
            - userId: str = <default> 💡 如果不传，则返回自己的信息
        """
        if not isinstance(payload, dict):
            payload = {"userId": payload}
        return self.request_with_sign(
            "subscribe/getUser.action", 
            method, 
            payload, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_info(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_info(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_info(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户信息（基本信息）

        GET https://cloud.189.cn/api/open/user/getUserInfo.action
        """
        return self.request_with_sign(
            "user/getUserInfo.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_info_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_info_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_info_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户信息（基本信息）

        GET https://cloud.189.cn/api/getUserInfo.action
        """
        return self.request_with_sign(
            "api/getUserInfo.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_info_base(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_info_base(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_info_base(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户信息（基本信息 + 扩展信息）

        GET https://cloud.189.cn/api/open/user/getUserInfoForPortal.action

        .. note::
            相当于 ``client.user_info()`` 和 ``client.user_info_ext()`` 的响应的合集
        """
        return self.request_with_sign(
            "user/getUserInfoForPortal.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_info_base_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_info_base_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_info_base_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户信息（基本信息 + 扩展信息）

        GET https://cloud.189.cn/api/portal/getUserInfoForPortal.action

        .. note::
            相当于 ``client.user_info()`` 和 ``client.user_info_ext()`` 的响应的合集
        """
        return self.request_with_sign(
            "portal/getUserInfoForPortal.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_info_brief(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_info_brief(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_info_brief(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户简略信息（可以获取 "sessionKey" 等)

        GET https://cloud.189.cn/api/portal/v2/getUserBriefInfo.action
        """
        return self.request_with_sign(
            "portal/v2/getUserBriefInfo.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_info_ext(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_info_ext(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_info_ext(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户信息（扩展信息）

        GET https://cloud.189.cn/api/open/user/getUserInfoExt.action
        """
        return self.request_with_sign(
            "user/getUserInfoExt.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_info_ext_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_info_ext_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_info_ext_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户信息（扩展信息）

        GET https://cloud.189.cn/api/getUserInfoExt.action
        """
        return self.request_with_sign(
            "api/getUserInfoExt.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_logined_infos(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_logined_infos(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_logined_infos(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户登录信息（也可以获取 "sessionKey" 等)

        GET https://cloud.189.cn/api/open/user/getLoginedInfos.action
        """
        return self.request_with_sign(
            "user/getLoginedInfos.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_logined_infos_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_logined_infos_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_logined_infos_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户登录信息（也可以获取 "sessionKey" 等)

        GET https://cloud.189.cn/api/portal/getLoginedInfos.action
        """
        return self.request_with_sign(
            "portal/getLoginedInfos.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_privileges(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_privileges(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_privileges(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户权限信息

        GET https://cloud.189.cn/api/open/user/getUserPrivileges.action
        """
        return self.request_with_sign(
            "user/getUserPrivileges.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_privileges_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_privileges_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_privileges_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户权限信息

        GET https://cloud.189.cn/api/getUserPrivileges.action
        """
        return self.request_with_sign(
            "api/getUserPrivileges.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_privileges_v2(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_privileges_v2(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_privileges_v2(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户权限信息

        GET https://cloud.189.cn/api/open/user/getUserPrivilegesV2.action
        """
        return self.request_with_sign(
            "user/getUserPrivilegesV2.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_privileges_v2_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_privileges_v2_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_privileges_v2_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """用户权限信息

        GET https://cloud.189.cn/api/getUserPrivilegesV2.action
        """
        return self.request_with_sign(
            "api/getUserPrivilegesV2.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_size_info(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_size_info(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_size_info(
        self, 
        /, 
        use_access_token: bool = False, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户空间容量和占用的统计

        GET https://cloud.189.cn/api/open/user/getUserSizeInfo.action
        """
        return self.request_with_sign(
            "user/getUserSizeInfo.action", 
            method, 
            use_access_token=use_access_token, 
            async_=async_, 
            **request_kwargs, 
        )

    @overload
    def user_size_info_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False] = False, 
        **request_kwargs, 
    ) -> dict:
        ...
    @overload
    def user_size_info_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[True], 
        **request_kwargs, 
    ) -> Coroutine[Any, Any, dict]:
        ...
    def user_size_info_portal(
        self, 
        /, 
        method: str = "GET", 
        *, 
        async_: Literal[False, True] = False, 
        **request_kwargs, 
    ) -> dict | Coroutine[Any, Any, dict]:
        """获取用户空间容量和占用的统计

        GET https://cloud.189.cn/api/portal/getUserSizeInfo.action
        """
        return self.request_with_sign(
            "portal/getUserSizeInfo.action", 
            method, 
            async_=async_, 
            **request_kwargs, 
        )

# TODO: 还有个开放平台：https://id.dlife.cn/api

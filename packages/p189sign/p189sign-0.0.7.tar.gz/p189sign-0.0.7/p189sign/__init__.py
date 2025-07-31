#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__license__ = "GPLv3 <https://www.gnu.org/licenses/gpl-3.0.txt>"
__version__ = (0, 0, 7)
__all__ = ["make_signed_headers", "make_hmac_signed_headers"]

from collections.abc import ItemsView, Iterable, Mapping
from datetime import datetime
from hashlib import md5
from hmac import digest as hmac_digest
from time import time
from urllib.parse import urlsplit


def make_signed_headers(
    auth_headers: str | Mapping[str, str] | Iterable[tuple[str, str]], 
    payload: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
    headers: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
) -> dict[str, str]:
    """制作携带签名的请求头，专供基于 "AccessToken" 请求头的访问

    :param auth_headers: 访问令牌 或者 与签名有关的请求头
    :param payload: 请求参数
    :param headers: 其它的请求头字段

    :return: 加上签名的请求头字典
    """
    if isinstance(auth_headers, str):
        auth_headers = {
            "AccessToken": auth_headers, 
            "Timestamp": str(int(time() * 1000)), 
        }
    else:
        auth_headers = dict(auth_headers)
        auth_headers.setdefault("Timestamp", str(int(time() * 1000)))
    if payload:
        payload = dict(payload, **auth_headers)
        payload = sorted(payload.items())
    else:
        payload = auth_headers.items()
    signature = md5(bytes("&".join(f"{k}={v}" for k, v in payload), "utf-8")).hexdigest()
    return dict(
        headers or (), 
        **auth_headers, 
        **{"Sign-Type": "1", "Signature": signature}, 
    )


def make_hmac_signed_headers(
    session_key: str, 
    session_secret: str, 
    url: str, 
    method: str = "GET", 
    payload: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
    headers: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
):
    """制作携带签名的请求头，专供基于 "SessionKey" 请求头的访问

    :param session_key: 会话 key
    :param session_secret: 会话密码
    :param url: 请求链接
    :param method: 请求方法
    :param payload: 请求参数
    :param headers: 其它的请求头字段

    :return: 加上签名的请求头字典
    """
    date = datetime.now().strftime("%y-%m-%d%H:%M:%S")
    data = {
        "SessionKey": session_key, 
        "Operate": method.upper(), 
        "RequestURI": urlsplit(url).path, 
        "Date": date, 
    }
    if payload:
        if isinstance(payload, Mapping):
            payload = ItemsView(payload)
        data["params"] = "&".join(f"{k}={v}" for k, v in sorted(payload))
    signature = hmac_digest(
        bytes(session_secret, "ascii"), 
        bytes("&".join(f"{k}={v}" for k, v in data.items()), "utf-8"), 
        "sha1"
    ).hex().upper()
    return dict(
        headers or (), 
        **{
            "Date": date,
            "SessionKey": session_key,
            "Signature": signature, 
        }
    )


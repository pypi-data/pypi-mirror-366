#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__license__ = "GPLv3 <https://www.gnu.org/licenses/gpl-3.0.txt>"
__version__ = (0, 0, 8)
__all__ = ["make_signed_headers", "make_hmac_signed_headers", "make_encrypted_params_headers"]

from base64 import b64encode
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
from hashlib import md5
from hmac import digest as hmac_digest
from time import time
from typing import Any
from urllib.parse import urlencode, urlsplit


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
    headers: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
):
    """制作携带签名的请求头，专供基于 "SessionKey" 请求头的访问

    :param session_key: 会话 key
    :param session_secret: 会话密码
    :param url: 请求链接
    :param method: 请求方法
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


def make_encrypted_params_headers(
    session_key: str, 
    pkid: str, 
    url: str, 
    method: str = "GET", 
    payload: None | Mapping[Any, Any] | Iterable[tuple[Any, Any]] = None, 
    headers: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
    aes_key: bytes = b"0"*16, 
) -> tuple[dict, dict]:
    """对请求参数进行 RSA 加密，并制作

    :param session_key: 会话 key
    :param pkid: PkId
    :param url: 请求链接
    :param method: 请求方法
    :param payload: 请求参数
    :param headers: 其它的请求头字段
    :param aes_key: AES 密钥，16 字节，只允许 0-9 和 a-f

    :return: 加上签名的请求头字典
    """
    params = ""
    if aes_key == b"0"*16:
        encrypted_key = "aDxvEkKJy4z8h9dDBWSTyc9XtUOS5MP/CgPG2Ed4JHmG1fZo/UgMuf6YsSPUqi7qXvUE7l5Ypdkw8rpMADUP09PIXqDn6DQZ6HgSy95FEpg/1aZQ/AGBQr6d3+DTy42CxRu9wCnDgwGJuUxmKsZFNvstwuA+8bSCKudu6cJ5ZT0="
        if not payload:
            params = "346bce0b8eed34da10f6a8fabb844494"
    else:
        from .util import rsa_encrypt
        encrypted_key = b64encode(rsa_encrypt(aes_key)).decode("ascii")
    if not params:
        from .util import aes_ecb_encrypt
        if payload:
            if not isinstance(payload, (Mapping, Sequence)):
                payload = tuple(payload)
            params = aes_ecb_encrypt(bytes(urlencode(payload), "utf-8"), aes_key).hex()
        else:
            params = aes_ecb_encrypt(b"", aes_key).hex()
    timestamp = str(int(time() * 1000))
    headers = dict(
        headers or (), 
        **{
            "EncryptionText": encrypted_key, 
            "PkId": pkid, 
            "SessionKey": session_key, 
            "Signature": hmac_digest(
                aes_key, 
                bytes(f"SessionKey={session_key}&Operate={method}&RequestURI={urlsplit(url).path}&Date={timestamp}&params={params}", "utf-8"), 
                "sha1", 
            ).hex(), 
            "X-Request-Date": timestamp, 
        }, 
    )
    return {"params": params}, headers


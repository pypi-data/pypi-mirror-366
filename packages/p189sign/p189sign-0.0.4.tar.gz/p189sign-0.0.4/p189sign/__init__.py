#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__version__ = (0, 0, 4)
__all__ = ["encode", "signature", "make_signed_headers"]
__license__ = "GPLv3 <https://www.gnu.org/licenses/gpl-3.0.txt>"

from collections.abc import Buffer, ItemsView, Iterable, Mapping
from hashlib import md5
from urllib.parse import urlencode


def signature(
    payload: ( Buffer | str | Mapping[str, str] | Mapping[bytes, bytes] | 
               Iterable[tuple[str, str]] | Iterable[tuple[bytes, bytes]] ), 
    /, 
) -> str:
    "用请求参数计算签名，最后返回 16 进制表示"
    if not isinstance(payload, (Buffer, str)):
        if isinstance(payload, Mapping):
            params: list = list(ItemsView(payload))
        elif isinstance(payload, list):
            params = payload
        else:
            params = list(payload)
        params.sort()
        payload = urlencode(params)
    return md5(payload.encode("utf-8")).hexdigest()


def make_signed_headers(
    auth_headers: str | Mapping[str, str] | Iterable[tuple[str, str]], 
    payload: None | Mapping[str, str] = None, 
    headers: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
) -> dict[str, str]:
    """制作携带签名的请求头

    :param auth_headers: 请求头中和产生签名有关的字段（大小写敏感），如果为 str，则视为 "AccessToken"
    :param payload: 请求参数
    :param headers: 其它的请求头字段

    :return: 加上签名的请求头字典
    """
    if isinstance(auth_headers, str):
        auth_headers = {"AccessToken": auth_headers}
    else:
        auth_headers = dict(auth_headers)
    auth_headers["Timestamp"] = auth_headers.get("Timestamp") or "0"
    return dict(
        headers or (), 
        **auth_headers, 
        **{
            "Sign-Type": "1", 
            "Signature": signature({
                **auth_headers, 
                **(payload or {}), 
            }), 
        }, 
    )


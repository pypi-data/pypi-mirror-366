#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__all__ = ["urlencode", "aes_ecb_encrypt", "rsa_encrypt", "rsa_encrypt_with_perm"]

from collections.abc import Buffer, ItemsView, Iterable, Mapping
from itertools import pairwise


from_bytes = int.from_bytes
to_bytes   = int.to_bytes


def urlencode(payload: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, /) -> str:
    if not payload:
        return ""
    if isinstance(payload, Mapping):
        payload = ItemsView(payload)
    return "&".join(map("%s=%s".__mod__, payload))


def pad_pkcs1_v1_5(data: Buffer, /) -> bytearray:
    view = memoryview(data)
    b = bytearray(b"\x00")
    b += b"\x02" * (126 - len(view))
    b += b"\x00"
    b += view
    return b


def pad_pkcs7(data: Buffer, /) -> bytearray:
    view = memoryview(data)
    b = bytearray(view)
    if pad_len := 16 - (len(view) & 15):
        b += bytes((pad_len,)) * pad_len
    return b


def aes_ecb_encrypt(
    data: Buffer, 
    key: Buffer = b"0" * 16, 
) -> bytes:
    """使用 AES CBC 模式进行加密

    :param data: 待加密的数据
    :param key:  加密密钥，16 字节

    :return: 密文
    """
    from Crypto.Cipher import AES
    cipher = AES.new(memoryview(key), AES.MODE_ECB)
    return cipher.encrypt(pad_pkcs7(data))


def rsa_encrypt(
    data: Buffer, 
    /, 
    key_n: int, 
    key_e: int, 
) -> bytearray:
    """把数据用 RSA 公钥加密

    :param data: 待加密的数据
    :param key_n: 公钥的 n 系数
    :param key_e: 公钥的 e 系数

    :return: 密文
    """
    cipher_data = bytearray()
    view = memoryview(data)
    for l, r in pairwise(range(0, len(view) + 117, 117)):
        cipher_data += to_bytes(pow(from_bytes(pad_pkcs1_v1_5(view[l:r])), key_e, key_n), 128)
    return cipher_data


def rsa_encrypt_with_perm(
    data: Buffer, 
    /, 
    perm, 
) -> bytearray:
    """把数据用 RSA 公钥加密

    :param data: 待加密的数据
    :param perm: 公钥证书内容

    :return: 密文
    """
    from Crypto.PublicKey import RSA
    if isinstance(perm, str):
        if not perm.startswith("-----"):
            perm = f"-----BEGIN PUBLIC KEY-----\n{perm}\n-----END PUBLIC KEY-----"
        pubkey = RSA.import_key(perm)
    else:
        pubkey = perm
    return rsa_encrypt(data, pubkey.n, pubkey.e)


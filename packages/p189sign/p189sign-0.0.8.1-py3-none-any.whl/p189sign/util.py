#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__all__ = ["aes_ecb_encrypt", "rsa_encrypt"]

from collections.abc import Buffer
from itertools import pairwise
from typing import Final


RSA_PUBKEY_PAIR: Final = (
    0xc2ef62fcd3798d9ab420caf694b75d794b98121ee0dc4be9c676a05a90762a152844c2b11aa8ab2bd99ffb0d0b7d0286c1d277b6bc84945b4b578e181fe6f7e5d34913ecaf89e23faddd62e443a67073d2ad6479125bafdf905482d449d284f60bb06eab1d86b9fb07de7ce6363fbc84151b1de43182a87356933399725b176b, 
    0x10001, 
)


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
    key_n: int = RSA_PUBKEY_PAIR[0], 
    key_e: int = RSA_PUBKEY_PAIR[1], 
) -> bytearray:
    """把数据用 RSA 公钥加密

    :param data: 待加密的数据
    :param key_n: 公钥的 n 系数
    :param key_e: 公钥的 e 系数

    :return: 密文
    """
    from_bytes = int.from_bytes
    to_bytes   = int.to_bytes
    cipher_data = bytearray()
    view = memoryview(data)
    for l, r in pairwise(range(0, len(view) + 117, 117)):
        cipher_data += to_bytes(pow(from_bytes(pad_pkcs1_v1_5(view[l:r])), key_e, key_n), 128)
    return cipher_data


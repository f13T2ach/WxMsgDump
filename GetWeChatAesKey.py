#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import struct

from pymem import Pymem
from win32api import HIWORD, LOWORD, GetFileVersionInfo

def error():
    print("[-]Exit code : -1")
    exit(-1)


def getVersionBase(pm):
    WeChatWindll_base = 0
    WeChatWindll_path = ""
    for m in list(pm.list_modules()):
        path = m.filename
        if path.endswith("WeChatWin.dll"):
            WeChatWindll_base = m.lpBaseOfDll
            WeChatWindll_path = path
            break

    if not WeChatWindll_path:
        print("[-]获取微信版本失败")
        error()

    version = GetFileVersionInfo(WeChatWindll_path, "\\")

    msv = version['FileVersionMS']
    lsv = version['FileVersionLS']
    version = f"{str(HIWORD(msv))}.{str(LOWORD(msv))}.{str(HIWORD(lsv))}.{str(LOWORD(lsv))}"

    return version, WeChatWindll_base


def getAesKey(pm, base, offset):
    try:
        result = pm.read_bytes(base + offset, 4)    # 读取 AES Key 的地址
        addr = struct.unpack("<I", result)[0]       # 地址为小端 4 字节整型
        aesKey = pm.read_bytes(addr, 0x20)          # 读取 AES Key
        result = binascii.b2a_hex(aesKey)           # 解码
    except Exception as e:
        print(f"{e}")
        print(f"[-]微信未登录")
        error()

    return result.decode()


AESKEY_OFFSETS = {
    "3.3.0.115": 0x1DDF914,
    "3.3.5.34": 0x1D2FB34,
    "3.6.0.18": 0x222EFE4,
    "3.7.0.29": 0x2363524,
    "3.7.0.30": 0x2366524,
    "3.7.5.23": 0x242413C,
    "3.8.1.26": 0x2C429FC,
    "3.9.0.28": 0x2E2D1AC
}

def main():
    try:
        pm = Pymem("WeChat.exe")
    except Exception as e:
        print(f"[-]异常抛出：{e} 微信登录状态异常")
        error()

    version, base = getVersionBase(pm)
    print(f"[+]微信版本：{version}\n[+]微信基址：{hex(base)}")

    offset = AESKEY_OFFSETS.get(version, None)
    if not offset:
        print(f"[-]不支持的版本 {version} 请访问其它项目获取")
        error()

    print(f"[+]偏移地址：{hex(offset)}")

    aesKey = getAesKey(pm, base, offset)
    print(f"[+]数据库密钥：{aesKey}")

    return aesKey

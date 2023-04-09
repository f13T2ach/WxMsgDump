#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import struct

import pymem
import sys
from urllib import parse
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

def getUserBasicInfo(base):
    p = pymem.Pymem()
    p.open_process_from_name("WeChat.exe")
    base_address = pymem.process.module_from_name(p.process_handle, "wechatwin.dll").lpBaseOfDll
    wechat_addr = base_address
    bytes_path = b'-----BEGIN PUBLIC KEY-----\n...'
    # Find a string and re Find addr
    base_address = pattern_scan_all(p.process_handle, bytes_path, return_multiple=True)

    # 通过字符串的地址反向寻找地址
    for i in base_address:
        # base_address = base_address[len(base_address) - 1]
        bytes_path1 = (i).to_bytes(4, byteorder="little", signed=True)
        cc = pattern_scan_all(p.process_handle, bytes_path1, return_multiple=True)
        if cc == []:
            continue
        if cc[0] > wechat_addr:
            base_address = cc[0]
            break
    
    int_wxid_len = p.read_int(base_address - 0x44)
    wxid_addr = p.read_int(base_address - 0x54)
    WXID = p.read_bytes(wxid_addr, int_wxid_len)

    # Get_UserName
    int_wxprofile_len = p.read_int(base_address - 0x5c)
    WxProfile = p.read_bytes(base_address - 0x6c, int_wxprofile_len)

    return WXID,WxProfile

def pattern_scan_all(handle, pattern, *, return_multiple=False):
    from pymem.pattern import scan_pattern_page
    next_region = 0
    found = []
    user_space_limit = 0x7FFFFFFF0000 if sys.maxsize > 2 ** 32 else 0x7fff0000
    while next_region < user_space_limit:
        next_region, page_found = scan_pattern_page(
            handle,
            next_region,
            pattern,
            return_multiple=return_multiple
        )
        if not return_multiple and page_found:
            return page_found
        if page_found:
            found += page_found
    if not return_multiple:
        return None
    return found

def main():
    try:
        pm = pymem.Pymem("WeChat.exe")
    except Exception as e:
        print(f"[-]异常抛出：{e} 微信登录状态异常")
        error()

    version, base = getVersionBase(pm)
    wxhex_offset = list(GLOBAL_OFFSETS.get(version, None))[4]
    if not wxhex_offset:
        print(f"[-]不支持的版本 {version} 请访问其它项目获取")
        error()
    aesKey = getAesKey(pm, base, wxhex_offset)
    
    ret = getUserBasicInfo(base)
    wxid = ret[0].decode()
    wxprofile = ret[1].decode()
    
    

    print(f"[+]微信版本：{version}\n[+]微信基址：{hex(base)}")
    print(f"[+]数据库密钥：{aesKey}")
    print(f"[+]WXID：{wxid}")
    return aesKey,wxid,wxprofile

GLOBAL_OFFSETS = {
    "3.2.1.154":
    {
        328121948,
        328122328,
        328123056,
        328121976,
        328123020
    },
    "3.3.0.115":
    {
        31323364,
        31323744,
        31324472,
        31323392,
        31324436
    },
    "3.3.0.84":
    {
        31315212,
        31315592,
        31316320,
        31315240,
        31316284
    },
    "3.3.0.93":
    {
        31323364,
        31323744,
        31324472,
        31323392,
        31324436
    },
    "3.3.5.34":
    {
        30603028,
        30603408,
        30604120,
        30603056,
        30604100
    },
    "3.3.5.42":
    {
        30603012,
        30603392,
        30604120,
        30603040,
        30604084
    },
    "3.3.5.46":
    {
        30578372,
        30578752,
        30579480,
        30578400,
        30579444
    },
    "3.4.0.37":
    {
        31608116,
        31608496,
        31609224,
        31608144,
        31609188
    },
    "3.4.0.38":
    {
        31604044,
        31604424,
        31605152,
        31604072,
        31605116
    },
    "3.4.0.50":
    {
        31688500,
        31688880,
        31689608,
        31688528,
        31689572
    },
    "3.4.0.54":
    {
        31700852,
        31701248,
        31700920,
        31700880,
        31701924
    },
    "3.4.5.27":
    {
        32133788,
        32134168,
        32134896,
        32133816,
        32134860
    },
    "3.4.5.45":
    {
        32147012,
        32147392,
        32147064,
        32147040,
        32148084
    },
    "3.5.0.20":
    {
        35494484,
        35494864,
        35494536,
        35494512,
        35495556
    },
    "3.5.0.29":
    {
        35507980,
        35508360,
        35508032,
        35508008,
        35509052
    },
    "3.5.0.33":
    {
        35512140,
        35512520,
        35512192,
        35512168,
        35513212
    },
    "3.5.0.39":
    {
        35516236,
        35516616,
        35516288,
        35516264,
        35517308
    },
    "3.5.0.42":
    {
        35512140,
        35512520,
        35512192,
        35512168,
        35513212
    },
    "3.5.0.44":
    {
        35510836,
        35511216,
        35510896,
        35510864,
        35511908
    },
    "3.5.0.46":
    {
        35506740,
        35507120,
        35506800,
        35506768,
        35507812
    },
    "3.6.0.18":
    {
        35842996,
        35843376,
        35843048,
        35843024,
        35844068
    },
    "3.6.5.7":
    {
        35864356,
        35864736,
        35864408,
        35864384,
        35865428
    },
    "3.6.5.16":
    {
        35909428,
        35909808,
        35909480,
        35909456,
        35910500
    },
    "3.7.0.26":
    {
        37105908,
        37106288,
        37105960,
        37105936,
        37106980
    },
    "3.7.0.29":
    {
        37105908,
        37106288,
        37105960,
        37105936,
        37106980
    },
    "3.7.0.30":
    {
        37118196,
        37118576,
        37118248,
        37118224,
        37119268
    },
    "3.7.5.11":
    {
        37883280,
        37884088,
        37883136,
        37883008,
        37884052
    },
    "3.7.5.23":
    {
        37895736,
        37896544,
        37895592,
        37883008,
        37896508
    },
    "3.7.5.27":
    {
        37895736,
        37896544,
        37895592,
        37895464,
        37896508
    },
    "3.7.5.31":
    {
        37903928,
        37904736,
        37903784,
        37903656,
        37904700
    },
    "3.7.6.24":
    {
        38978840,
        38979648,
        38978696,
        38978604,
        38979612
    },
    "3.7.6.29":
    {
        38986376,
        38987184,
        38986232,
        38986104,
        38987148
    },
    "3.7.6.44":
    {
        39016520,
        39017328,
        39016376,
        38986104,
        39017292
    },
    "3.8.0.31":
    {
        46064088,
        46064912,
        46063944,
        38986104,
        46064876
    },
    "3.8.0.33":
    {
        46059992,
        46060816,
        46059848,
        38986104,
        46060780
    },
    "3.8.0.41":
    {
        46064024,
        46064848,
        46063880,
        38986104,
        46064812
    },
    "3.8.1.26":
    {
        46409448,
        46410272,
        46409304,
        38986104,
        46410236
    },
    "3.9.0.28":
    {
        48418376,
        48419280,
        48418232,
        38986104,
        48419244
    },
    "3.9.2.23":
    {
        50320784,
        50321712,
        50320640,
        38986104,
        50321676
    }
}
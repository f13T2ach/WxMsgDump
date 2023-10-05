# coding=utf-8

import binascii
import pymem.process
from pymem import Pymem
from win32api import GetFileVersionInfo, HIWORD, LOWORD


class Wechat:
    def __init__(self, pm):
        module = pymem.process.module_from_name(pm.process_handle, "WeChatWin.dll")
        self.pm = pm
        self.dllBase = module.lpBaseOfDll
        self.sizeOfImage = module.SizeOfImage
        self.bits = self.GetPEBits()

    # 通过解析PE来获取位数
    def GetPEBits(self):
        address = self.dllBase + self.pm.read_int(self.dllBase + 60) + 4 + 16
        SizeOfOptionalHeader = self.pm.read_short(address)

        # 0XF0 64bit
        if SizeOfOptionalHeader == 0xF0:
            return 64

        return 32

    def GetInfo(self):
        version = self.GetVersion()
        if not version:
            print("[!]获取 WeChatWin.dll 失败")
            return

        print(f"[-]WeChat 版本：{version}")
        print(f"[-]WeChat 架构: {self.bits}")

        keyBytes = b'-----BEGIN PUBLIC KEY-----\n...'

        # 从内存中查找 BEGIN PUBLIC KEY 的地址
        publicKeyList = pymem.pattern.pattern_scan_all(self.pm.process_handle, keyBytes, return_multiple=True)
        if len(publicKeyList) == 0:
            print("[!]无法找到公钥")
            return

        keyAddr = self.GetKeyAddr(publicKeyList)
        if keyAddr is None:
            print("[!]无法找到密钥的地址")
            return

        keyLenOffset = 0x8c if self.bits == 32 else 0xd0

        for addr in keyAddr:
            try:
                keyLen = self.pm.read_uchar(addr - keyLenOffset)
                if self.bits == 32:
                    key = self.pm.read_bytes(self.pm.read_int(addr - 0x90), keyLen)
                else:
                    key = self.pm.read_bytes(self.pm.read_longlong(addr - 0xd8), keyLen)

                key = binascii.b2a_hex(key).decode()
                if self.CheckKey(key):
                    print(f"[+]找到公钥 {key}")
                    print("[+]密钥破解完成")
                    return addr,key
            except:
                print("[!]发生异常，密钥轮询失败")
                pass

        
        


    @staticmethod
    def CheckKey(key):
        # 目前key位数是32位
        if key is None or len(key) != 64:
            return False

        return True

    # 内存搜索特征码
    @staticmethod
    def SearchMemory(parent, child):
        offset = []
        index = -1

        while True:
            index = parent.find(child, index + 1)
            if index == -1:
                break
            offset.append(index)

        return offset

    # 获取key的地址
    def GetKeyAddr(self, publicKeyList):
        # 存放真正的key地址
        keyAddr = []

        # 读取整个 WeChatWin.dll 的内容
        buffer = self.pm.read_bytes(self.dllBase, self.sizeOfImage)

        byteLen = 4 if self.bits == 32 else 8
        for publicKeyAddr in publicKeyList:
            keyBytes = publicKeyAddr.to_bytes(byteLen, byteorder="little", signed=True)
            offset = self.SearchMemory(buffer, keyBytes)

            if not offset or len(offset) == 0:
                continue

            offset[:] = [x + self.dllBase for x in offset]
            keyAddr += offset

        if len(keyAddr) == 0:
            return None

        return keyAddr

    # 获取微信版本
    def GetVersion(self):
        WeChatWindll_path = ""
        for m in list(self.pm.list_modules()):
            path = m.filename
            if path.endswith("WeChatWin.dll"):
                WeChatWindll_path = path
                break

        if not WeChatWindll_path:
            return False

        version = GetFileVersionInfo(WeChatWindll_path, "\\")

        msv = version['FileVersionMS']
        lsv = version['FileVersionLS']
        version = f"{str(HIWORD(msv))}.{str(LOWORD(msv))}.{str(HIWORD(lsv))}.{str(LOWORD(lsv))}"

        return version
    
    def GetUserBasicInfo(self,base_address):
        print(base_address)
        # 获取wxid
        int_wxid_len = self.pm.read_int(base_address - 0x44)
        wxid_addr = self.pm.read_int(base_address - 0x54)
        print(wxid_addr)
        WXID = self.pm.read_bytes(wxid_addr, int_wxid_len)

        # 获取用户名
        int_wxprofile_len = self.pm.read_int(base_address - 0x5c)
        WxProfile = self.pm.read_bytes(base_address - 0x6c, int_wxprofile_len)

        return WXID.decode(),WxProfile.decode()


if __name__ == '__main__':

    try:
        wechat = Pymem("WeChat.exe")
        Wechat(wechat).GetInfo()
    except pymem.exception.ProcessNotFound:
        print("[!]微信没有登录")
    except pymem.exception.CouldNotOpenProcess:
        print("[!]权限不足")
    except Exception as e:
        print(e)

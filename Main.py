# WARNING | 警告
# 任何组织和个人都不得利用本项目窥探、篡改用户的聊天记录；
# Any organization or person can not use this program to peep into or edit the chat history which belongs to Wechat users;
# 中华人民共和国公民的聊天记录受到法律保护。
# The personal chat history of citizens of the People's Republic of China is protected by law.
# 版本号
VER = "V1.1"
import GetWeChatInfo
import CrackWeChatDB
import os
import sys
import sqlite3
import SQLManager
import keyboard
from win32com.shell import shell


# Msg目录下的表
msg_table = ["MicroMsg.db"] 
# Mutil目录下的表 除了msgn.db
mutil_table = []
# Micromsg.db的路径
micromsg_path = ""
# MSGn.db文件数组
msgn_path = []

# 聊天列表 下标对应UserName,Alias,Remark,NickName
wxlist = []

def main():
    res = [] #所有db文件的名称数组
    isSkipDc = False #跳过解密

    print("WxMsgDump%s | 微信聊天记录导出"%VER)
    print()
    print("Copyright(c) UvgenTechno 2023 Authorized")
    print("----------------------------------------")
    print("[+]Follow me on Github: https://github.com/f13T2ach/WxMsgDump")

    # 获取密钥和其它个人信息
    ret =  GetWeChatInfo.main()
    aeskey = ret[0]
    wxid = ret[1]
    wxprofile = ret[2]

    # 自动获取文件路径
    win_user = os.path.expandvars('$HOMEPATH')
    wx_config = open(os.getenv("SystemDrive") + win_user + '\\AppData\\Roaming\\Tencent\\WeChat\\All Users\\config\\3ebffe94.ini')

    if wx_config.read() == 'MyDocument:':
        wx_path = shell.SHGetFolderPath(0, 5, None, 0)+"\\WeChat Files\\"+wxid+"\\Msg" # 如果目录在 文档 下
    else:
        wx_path = wx_config.read() + "\\WeChat Files\\"+wxid+"\\Msg"
    dir_path = wx_path + "\\Multi"

    print("[+]微信号: "+wxprofile+" 工作路径: "+wx_path)


    # 检查是否有留存过的解密文件
    files = os.listdir(dir_path)

    for name in files:
        if name.endswith(".dec.db"):
            key = input("[>]发现上次解密过的文件。跳过解密步骤->Y 删除全部解密文件->D 覆盖解密->回车:").capitalize()
            if key == 'Y':
                isSkipDc = True
            if key == 'D':
                del_decryptf(wx_path)
                del_decryptf(dir_path)
                input("[+]操作完成，任意键退出")
                exit(0)
            break

    # 获取Mutil下的表
    try:
        for path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, path)) and path.endswith(".db") and path.endswith("dec.db") is not True:
                if path.startswith("MSG") or path in mutil_table:
                    res.append(path)
            #TODO 需要额外询问
    except:
        #输入d可以打开debug
        #if(dir_path == "d\\Msg\\Multi"):
        #    print("[Opening Debug]")
        #    DBManagement.main()
        #    return
        #else:
        print("[-]路径无效。请注意，你可能忽略了点击“打开文件夹”按钮这个步骤")
        exit(-1)
    
    # 获取Msg目录下的表
    for path in os.listdir(wx_path):
        if os.path.isfile(os.path.join(wx_path, path)) and path in msg_table:
            res.append(path)

    print("[+]发现以下表: "+str(list(res)))
    if res is []:
        print("[+]解密完成，没有发现任何聊天文件，或者已经解密过")
        exit(0)
    
    
    if isSkipDc is not True:
        #删除以前的解密
        for file_name in os.listdir(dir_path):
            if file_name.endswith(".dec.db"):
                try:
                    os.remove(file_name)
                except:
                    pass
        #执行加密
        decryptMsg(res,dir_path,wx_path,aeskey)
    
    

    # 将之转换成路径数组
    for path in res:
        if(path.startswith("MSG")):
            msgn_path.append(dir_path+"\\"+path+".dec.db")
        elif path in msg_table:
            if path == "MicroMsg.db":
                micromsg_path = wx_path+"\\"+path+".dec.db"

    print("[+]正在获取聊天列表")
    wxlist = SQLManager.get_chatlist(micromsg_path)

    while True:
        print("[+]请输入要导出的聊天名称，或者你给他/她的备注。空表示退出操作")
        aimChat = input("[>]")
        if aimChat=="":
            break
        repeat_count = 1
        for chat in wxlist:
            #print(chat[3])
            if chat[3]==aimChat or chat[2]==aimChat:
                print("============FOUND TARGET===========")
                print("[+]匹配到第"+str(repeat_count)+"个聊天: ",chat[0])
                print("[+]微信号: ", chat[1])
                print("[+]备注: ",chat[2])
                print("[+]昵称: ",chat[3])
                export_msg(msgn_path,chat[0],chat[3]+" "+chat[1])
                repeat_count = repeat_count+1
                print("=============END OUTPUT============")
        if repeat_count == 1:
            print("[!]找不到此聊天: ",aimChat)



def decryptMsg(res,dir_path,wx_path,aeskey):
    for path in res:
        if(path.startswith("MSG")): # 解密Mutil下的文件
            CrackWeChatDB.decrypt_msg(dir_path+"\\"+path,aeskey,res.index(path)+1,len(res))
        else: # 解密Msg下的文件
             CrackWeChatDB.decrypt_msg(wx_path+"\\"+path,aeskey,res.index(path)+1,len(res))
        if(res.index(path)+1!=len(res)):
             # 覆盖原来的进度条
            print("\r","                                                                                  ",end="",flush=True)
    print()

def del_decryptf(path):
    for root , dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".dec.db"):   #指定要删除的格式，这里是jpg 可以换成其他格式
                os.remove(os.path.join(root, name))

def export_msg(msg_paths,wxid,chatname):
    outputPath = ""
    for path in msg_paths:
        flag,outputPath = SQLManager.msg_export(path,wxid,chatname,msg_paths.index(path)+1)
    print("[+]完成，导出到"+outputPath)

if __name__ == '__main__':
    main()
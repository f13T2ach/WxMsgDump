<div align="center">

# WxMsgDump

**开源的导出微信聊天记录的程序**

</div>

## 介绍

**运行要求:** Python 2.0以上环境

**运行系统:** Windows 7至11

**版本** 1.1

请在Cmd中运行以下代码，来下载依赖库（如果没有）

```
pip install pywin32
pip install pymem
pip install pycryptodome
```

## 运行方法

方法一、运行源码

```
python Main.py
```

方法二、运行可执行文件

1.解压缩

2.双击运行目录内唯一的一个exe文件

## 更新日志

### 2023/4/8 1.1 Update

**Add**

1.支持自动获取用户文件地址，无需手动输入

2.支持判定是否有解密过的文件出现

3.移除基址库，主动寻址

**Repair**

4.修复SqlManager类里的一个疏忽：没有根据时间戳排序，导致导出的数据异常。

## 鸣谢
**lich0821 / 微信数据库逆向和数据库密钥逆向** https://github.com/lich0821/WeChatDB

**x1hy9 / 微信进程逆向** https://github.com/x1hy9/WeChatUserDB

## 警告

**逆向是微信条款中不允许的行为，窃取、篡改聊天记录是违法行为。程序仅供学习交流。**

严禁以此程序为基础，窃取他人聊天记录；

严禁以此程序为基础，制作有窃取、篡改用户微信聊天记录的功能的程序；

严禁以此程序为基础，制作以勒索或者其它暴力盈利行为为目的的程序；

严禁以此程序为基础，向其它用户提供“导出聊天记录”或者类似以盈利为目的的服务，这同时会威胁到其它用户的账号安全；

严禁以此程序为基础，记录、保存、分享、上传、分析或有类似的不经过被收集用户同意来收集用户隐私的程序；

严禁销售贩卖此程序的本体，或者以此程序为基础制作的衍生版本的程序；

在转载代码片段时，必须注明正确的代码出处，“鸣谢”部分提到的项目中的代码应注明原作者的联系方式或者主页。

**说明：** 本应用程序由用户自愿下载安装、编译使用，自愿逆向自己或其它用户的账号聊天记录，接受将解密后的聊天记录暴露在文件系统中的危险性。并且，用户使用此应用程序非法侵害其它用户权利的行为与本应用程序作者无关，本应用程序的作者已经尽到了警告的义务。

**下载、保存、进一步浏览源代码或者下载安装、编译使用本程序，表示你同意本警告，并承诺遵守它。**


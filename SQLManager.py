import sqlite3
import os
import time
import ProgressBar

workDirName = "微信聊天导出"

def get_chatlist(path):
    conn = sqlite3.connect(path)
    cursor = conn.execute("SELECT UserName,Alias,Remark,NickName from Contact")
    output = cursor.fetchall()
    conn.close()
    return output

def msg_export(path,wxid,chatname):
    conn = sqlite3.connect(path)
    try:
        cursor = conn.execute("SELECT Type,IsSender,CreateTime,StrTalker,StrContent from MSG WHERE StrTalker = '%s'"% wxid+" ORDER BY CreateTime ASC")
        cursor = cursor.fetchall()
    except Exception as ex:
        print("[-]不存在该聊天的聊天记录，这是异常信息: ",ex)
        conn.close()
        return False
    desktop_path = os.path.abspath(".")  # 存放路径
    full_path =  "%s\\%s\\%s(%s).csv"%(desktop_path,workDirName,chatname,wxid) 

    folder = os.path.exists(desktop_path+"\\"+workDirName)
    if not folder:
        os.makedirs(desktop_path+"\\"+workDirName)

    file = open(full_path, 'w', encoding='utf-8-sig')
    # 写入表头
    file.write("时间,对方,你的回复\n")

    for msg in cursor:
        date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg[2])) #转换时间戳
        if msg[0] == 49:
            content = '[应用消息或表情]'
        elif msg[0] == 47:
            content = '[动画表情]'
        elif msg[0] == 3:
            content = '[图片]'
        elif msg[0] == 42:
            content = '[名片]'
        elif msg[0] == 43:
            content = '[视频]'
        elif msg[0] == 34:
            content = '[语音]'
        else:
            content = msg[4].replace("\n", " ") #TODO 使用表格来允许换行

        if msg[1]==1:  #是自己发的
            file.write(str(date)+", ,"+str(content)+"\n")
        elif msg[1]==0:
            file.write(str(date)+","+str(content)+", \n")
        
        ProgressBar.progress_bar("正在导出第"+str(cursor.index(msg)+1)+"条, 共"+str(len(cursor))+"条",cursor.index(msg)+1,len(cursor))
        msg=[]
    
    print()
    print("[+]完成，导出到",full_path)
    file.close()
    conn.close()
    return True

def merge_databases(db1, db2):
    con = sqlite3.connect(db1)

    con.execute("ATTACH '" + db2 +  "' as dba")

    con.execute("BEGIN")
    for row in con.execute("SELECT * FROM dba.sqlite_master WHERE type='table'"):
        combine = "INSERT OR IGNORE INTO "+ row[1] + " SELECT * FROM dba." + row[1]
        con.execute(combine)
    con.commit()
    con.execute("detach database dba")


def batch_merge(paths):
    for db_file in paths:
        merge_databases(paths[0], db_file)    
    return paths[0]
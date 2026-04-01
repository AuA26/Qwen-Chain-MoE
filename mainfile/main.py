#2026年4月1日预留，解释一下变量名字
#miss_model是没有安装的model model_li是检查电脑已经安装的model model_li_a是需要的model库
#m_name是检查电脑安装model库字典分离出来的单个库名 model是检查电脑for循环的临时寄存变量 mm是比较有和没有model的for循环临时寄存变量

import ollama
import sys
import msvcrt
import time
import os
import shutil
import platform
from flask import Flask
import threading
import subprocess
import webbrowser

web_process = None

yanseR = "\033[91m"
yanseW = "\033[0m"
yanseG = "\033[92m"
yanseB = "\033[94m"    
yanseY = "\033[93m"

A_Version = "0.0.1"
miss_model = []
model_li = []
model_li_a = ['qwen3:0.6b','qwen2-math:1.5b','qwen3:4b','qwen3-vl:4b','qwen3-embedding:4b','qwen2.5-coder:3b']

def py_ver():                                #检查版本，写于4月2日1：50，删除了简略数字版本打印
    print("Python Version INFO:",sys.version)
    print("OS_Version:",platform.system(),platform.release())
    print("Arc:",platform.machine())

def get_ollama_dir():                       #检查ollama目录，写于4.1
    try:
        model_li2 = ollama.list()
        fm = model_li2.models[0]
        dir_m_p = fm.model
        dir_m_p_add = os.path.splitdrive(dir_m_p)[0]
        return dir_m_p_add + "\\"
    except Exception as e:
        pass

    return os.path.splitdrive(os.getcwd())[0] + "\\"

def ck_dir_40g():                             #剩余空间判断，4.1
    dir_m22 = get_ollama_dir()
    free_bytes = shutil.disk_usage(dir_m22).free
    free_g = free_bytes / 1024 / 1024 / 1024
    return free_g >= 40

def xuanze_yesorno():                    #左右选择，4.1
    opt = ["yes","no"]
    current = 0
    return opt,current

def down_a_mmd(mmd):                              #下载进度条 4.1
    print(f"\nDownload...:{mmd}")
    for mmd_dd_li in ollama.pull(mmd,stream=True):
        if "status" in mmd_dd_li:
            zhuangtai = mmd_dd_li["status"]
            if "completed" in mmd_dd_li and "total" in mmd_dd_li:
                done = mmd_dd_li["completed"]
                zong = mmd_dd_li["total"]
                baifenjindu = round((done / zong)*100,1)
                tiao = "█" * int(baifenjindu //2)
                sys.stdout.write(f"\r[{yanseG}{tiao}{yanseW}]{baifenjindu}%  ")
                sys.stdout.flush()
    print(f"\n{yanseG}{mmd}successful!{yanseW}")

print (yanseB +"Qwen-chain-moe V0.0.1 Apr02,2026",yanseW,"\n")
if __name__ == "__main__":
    py_ver()

for model in ollama.list()["models"]:
    m_name = model.model.strip()
    model_li.append(m_name)

for mm in model_li_a:
    if mm not in model_li:
        miss_model.append(mm)

if miss_model:
    print(yanseR + "缺少模型/Missing Models:",miss_model,yanseW)
    opt,current = xuanze_yesorno()

    while True:
        if current == 0:
            sys.stdout.write(f"{yanseB}\r开始安装? Download? {yanseW} [{yanseB}Yes{yanseW}] No")
        else:
            sys.stdout.write(f"{yanseB}\r开始安装? Download? {yanseW} Yes [{yanseB}No{yanseW}] {yanseR}不安装将无法使用！Cant't used it whitout downloading!{yanseW}")

        sys.stdout.flush()

        keya = msvcrt.getch()

        if keya == b'\xe0':
            keya = msvcrt.getch()
            if keya == b'K':
                current = 0
            elif keya == b'M':
                current = 1
        elif keya == b'\r':
            print()
            break
        else:
            continue
    if current == 0:
        print(yanseY + "检测磁盘空间 Checking ROM FreeSize")
        time.sleep(1)
        cs = ck_dir_40g()
        if cs != True:
            print(yanseR + "磁盘空间不足40GB ROM isn't enought 40GB",yanseW)
            print("\n无法安装 Can't Download!")
            time.sleep(8)
            sys.exit(0)
        else:
            print(yanseG + "磁盘充足! ROM Enough!",yanseW)
        print(yanseG + "开始安装... Downloading...",yanseW)
        for mmd in miss_model:
            down_a_mmd(mmd)
        print(f"\n{yanseG}所有模型安装完成！Full models success!{yanseW}")
    else:
        print(f"{yanseR}取消安装/Canceled{yanseW}5秒后结束程序")
        time.sleep(5)
        os._exit(0)
else:
    print(yanseG + "模型齐全/Full Models" + yanseW)
    print(yanseB + "Started Successfully!",yanseW,yanseR,"Need help? input'help'",yanseW)
    while True:
        User_input = input("User >>> ").lower().strip()
        if User_input == "stop":
            print("Syst >>> Closing!")
            if web_process is not None and web_process.poll() is None:
                web_process.terminate()
                web_process = None
                print("Syst >>>",yanseG,"Web Service been cosled",yanseW)
            time.sleep(2)
            break
        elif User_input == "help":
            print()
        elif User_input == "start":
            print("Syst >>> ",yanseG,"Initializing Date...",yanseW)
            if web_process and web_process.poll() is None:
                print("Syst >>> ",yanseR,"WebService is working,Can't Repeat",yanseW)
                continue
            if sys.platform == "win32":
                devnull = open(os.devnull,"w")
                web_process = subprocess.Popen([sys.executable,"webser.py"],stdout=devnull,stderr=devnull)
                print("Syst >>> ",yanseG,"Web Started Successful!",yanseW)
                time.sleep(0.5)
                weburl = "http://127.0.0.1:11888"
                webbrowser.open(weburl)
                continue
        elif not User_input:
            continue
        else:
            print ("Syst >>> ",yanseR,"Unknown Command!",yanseW)
            continue


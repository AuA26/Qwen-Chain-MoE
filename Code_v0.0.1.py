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
from flask import Flask, render_template_string, request, jsonify
import threading
import subprocess
import webbrowser
import requests as rq
import json
import base64
from io import BytesIO
from PIL import Image

# ------------------- 原main.py 全局变量 -------------------
web_process = None
yanseR = "\033[91m"
yanseW = "\033[0m"
yanseG = "\033[92m"
yanseB = "\033[94m"    
yanseY = "\033[93m"
A_Version = "0.0.1"
miss_model = []
model_li = []
model_li_a = ['qwen3:0.6b','qwen2-math:1.5b','qwen3.5:4b','qwen3-vl:4b','qwen3-embedding:4b','qwen2.5-coder:3b']

# ------------------- 原webser.py 全局变量 -------------------
port=11888
app = Flask(__name__)
# 新增：标记Web服务是否运行（替代原subprocess的进程判断，无逻辑修改）
web_running = False

# ------------------- 原main.py 所有函数 -------------------
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
def work_ollama():            #检测ollama是否工作
    try:
        res = rq.get("http://127.0.0.1:11434/api/tags",timeout=3)
        return res.status_code == 200
    except:
        return False
    
def build_ly_ollama_model():         #问题内容，懒得修复了，直接在webser里面写进提示词
    modelfile = """FROM qwen3:0.6b
SYSTEM "You are a MoE task router.You ONLY output a JSON array of task names in oder. Do NOT answer the question.Do NOT add any explanation. Do NOT add any extra words.Tasks:long_text,math,code."
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER max_tokens 64
PARAMETER repeat_penalty 1.05
PARAMETER stop ["\\n", "#", ";", "."]
"""
    with open("qwen-rt.modelfile", "w", encoding="utf-8") as f: f.write(modelfile) 
    try: 
        ollama.create(model="qwen-rt", path="qwen-rt.modelfile")
        print(yanseG +"Router is build successful!",yanseW)
    except Exception as e:
        print(yanseR + f"创建模型失败: {e}", yanseW)

# ------------------- 原webser.py 所有函数 -------------------
def d(user_input, image_base64=None):
    prompt = f"""
You are a MoE task router. STRICT RULES:
1. ONLY output a JSON array, no extra words/explanation/chat.
2. Allowed tasks: long_text, reasoning, code, vision.
3. vision task only when there is an image, others according to text demand.
4. One task for one demand, call on demand.
Input text: {user_input}
Has image: {True if image_base64 else False}
Example output: ["vision"], ["reasoning"], ["code"], ["long_text"]
"""
    try:
        response = ollama.chat(
            model='qwen3:0.6b',
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "max_tokens": 64, "repeat_penalty": 1.05}
        )
        return json.loads(response.message.content.strip())
    except:
        return ["long_text"]

def long_text_deal(text):
    resp = ollama.chat(
        model='qwen3.5:4b',
        messages=[{"role": "user", "content": f"清晰整理并通俗解释这段内容：{text}"}]
    )
    ollama.close(model='qwen3.5:4b')
    return resp.message.content.strip()

def reasoning_deal(text):
    resp = ollama.chat(
        model='qwen3.5:4b',
        messages=[{"role": "user", "content": f"一步步完成推理/计算/逻辑分析：{text}"}]
    )
    ollama.close(model='qwen3.5:4b')
    return resp.message.content.strip()

def code_deal(text):
    resp = ollama.chat(
        model='qwen2.5-coder:3b',
        messages=[{"role": "user", "content": f"根据需求写可运行代码并加简单注释，仅输出代码+必要解释：{text}"}]
    )
    ollama.close(model='qwen2.5-coder:3b')
    return resp.message.content.strip()

def vision_deal(image_base64, text):
    resp = ollama.chat(
        model='qwen3-vl:4b',
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
            {"type": "text", "text": f"分析这张图片的内容，结合问题：{text}，详细描述并解答"}
        ]}]
    )
    ollama.close(model='qwen3-vl:4b')
    return resp.message.content.strip()

def get_embedding(text):
    resp = ollama.embeddings(model='qwen3-embedding:4b', prompt=text)
    ollama.close(model='qwen3-embedding:4b')
    return resp['embedding']

def image_to_base64(image_file):
    try:
        img = Image.open(image_file)
        if img.format not in ['PNG', 'JPEG', 'JPG']:
            return None
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except:
        return None

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>QCM Web Service</title>
<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Microsoft YaHei", sans-serif;
}
body {
  background: #ffffff;
  color: #000;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.github-btn {
  background:#000 !important; color:#fff; 
  border:none; padding:8px 12px; 
  border-radius:8px; cursor:pointer;
}
.header {
  position: sticky;
  top: 0;
  background: #fff;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}
.header h1 {
  font-size: 22px;
  font-weight: bold;
}
.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.msg {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
}
.user {
  align-self: flex-end;
  background: #007bff;
  color: #fff;
}
.bot {
  align-self: flex-start;
  background: #f5f5f5;
  color: #000;
}
.loading {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid #ccc;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.footer {
  position: sticky;
  bottom: 0;
  background: #fff;
  padding: 12px 16px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
  align-items: center;
}
#input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
}
button {
  padding: 10px 16px;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 8px;
}
</style>
</head>
<body>
<div class="header" style="display:flex;justify-content:space-between;align-items:center">
  <h1>Qwen-Chain-Moe（QCM） V0.0.1 Web Service</h1>
  <div style="display:flex;align-items:center;gap:8px">
    <span style="font-size:12px;color:#999">由 /AuA/ 编写</span>
    <button class="github-btn" onclick="window.open('https://github.com/AuA26/Qwen-Chain-MoE')">GitHub</button>
  </div>
</div>
<div class="chat-box" id="box"></div>
<img class="img-preview" id="imgPreview" src="" style="position: absolute;bottom: 80px;left: 20px;width: 100px;height: 100px;object-fit: cover;border-radius: 8px;border: 1px solid #eee;display: none;">
<div class="footer">
  <label for="file" class="file-label" style="padding: 10px 12px;border: 1px solid #ddd;border-radius: 8px;font-size: 14px;cursor: pointer;color: #666;">📷 图片</label>
  <input type="file" id="file" accept="image/png,image/jpeg,image/jpg" style="display: none;">
  <input type="text" id="input" placeholder="输入消息...">
  <button onclick="send()">发送</button>
</div>
<script>
const box = document.getElementById('box');
const input = document.getElementById('input');
const file = document.getElementById('file');
const imgPreview = document.getElementById('imgPreview');
let selectedImage = null;

// 图片选择预览
file.addEventListener('change', (e) => {
  const fileObj = e.target.files[0];
  if (!fileObj) return;
  selectedImage = fileObj;
  const reader = new FileReader();
  reader.onload = (e) => {
    imgPreview.src = e.target.result;
    imgPreview.style.display = 'block';
  };
  reader.readAsDataURL(fileObj);
});

// 发送消息
async function send() {
  const msg = input.value.trim();
  if (!msg && !selectedImage) return;
  // 显示用户消息
  let userMsg = msg;
  if (selectedImage) userMsg += ' [附带图片]';
  addMsg(userMsg, 'user');
  input.value = '';
  file.value = '';
  imgPreview.style.display = 'none';
  const loadNode = addMsg('<div class="loading"></div>', 'bot');

  // 构造FormData
  const formData = new FormData();
  formData.append('msg', msg);
  if (selectedImage) formData.append('image', selectedImage);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    box.removeChild(loadNode);
    addMsg(data.reply, 'bot');
  } catch (e) {
    box.removeChild(loadNode);
    addMsg('发送失败，请重试', 'bot');
  } finally {
    selectedImage = null;
    box.scrollTop = box.scrollHeight;
  }
}

// 添加消息
function addMsg(text, className) {
  const div = document.createElement('div');
  div.className = 'msg ' + className;
  div.innerHTML = text;
  box.appendChild(div);
  if (box.children.length > 50) box.removeChild(box.firstChild);
  return div;
}

// 回车发送
input.addEventListener('keydown', (e) => {if (e.key === 'Enter') send();});
</script>
</body>
</html>
''')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        msg = request.form.get('msg', '').strip()
        image_file = request.files.get('image')
        image_b64 = None
        # 处理图片（仅PNG/JPEG）
        if image_file and image_file.filename:
            image_b64 = image_to_base64(image_file)
            if not image_b64:
                return jsonify({'reply': '仅支持上传PNG/JPEG/JPG格式图片'})
        
        # 调用路由获取任务列表
        tasks = d(msg, image_b64)
        current_result = msg if msg else '分析这张图片的内容'

        # 按需执行任务，加载一个用一个释放一个
        for task in tasks:
            if task == "long_text":
                current_result = long_text_deal(current_result)
            elif task == "reasoning":
                current_result = reasoning_deal(current_result)
            elif task == "code":
                current_result = code_deal(current_result)
            elif task == "vision" and image_b64:
                current_result = vision_deal(image_b64, current_result)
        
        return jsonify({'reply': current_result})
    except Exception as e:
        return jsonify({'reply': f'错误：{str(e)}'})

# ------------------- 新增：Flask线程启动函数（仅为合并，无业务逻辑） -------------------
def start_flask_server():
    global web_running
    web_running = True
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    web_running = False

# ------------------- 原main.py 主程序入口（仅修改start命令的启动方式，其余完全保留） -------------------
print (yanseB +"Qwen-chain-moe V0.0.1 Apr02,2026",yanseW,"\n")
if work_ollama() == True:
    print("ollama working")
else:
    print(yanseR +"ollama server in not work,please make sure ollama is work",yanseW,yanseY,"Error Code 101",yanseW)
    time.sleep(10)
    os._exit(0)
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
        elif User_input == "info":
            print(yanseY +"https://github.com/AuA26/Qwen-Chain-MoE",yanseW)
        elif User_input == "help":
            print()
        elif User_input == "start":
            print("Syst >>> ",yanseG,"Initializing Date...",yanseW)
            # 仅修改此处：替换subprocess调用为线程启动Flask，其余原代码完全保留
            if web_running:
                print("Syst >>> ",yanseR,"WebService is working,Can't Repeat",yanseW)
                continue
            if sys.platform == "win32":
                # 启动Flask守护线程，无控制台输出
                flask_thread = threading.Thread(target=start_flask_server, daemon=True)
                flask_thread.start()
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
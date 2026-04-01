from flask import Flask, render_template_string, request, jsonify
import ollama

port=11888
app = Flask(__name__)

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

<div class="footer">
  <input type="text" id="input" placeholder="输入消息...">
  <input type="file" id="file">
  <button onclick="send()">发送</button>
</div>

<script>
const box = document.getElementById('box');
const input = document.getElementById('input');

async function send() {
  const msg = input.value.trim();
  if (!msg) return;

  addMsg(msg, 'user');
  input.value = '';

  const loadNode = addMsg('<div class="loading"></div>', 'bot');

  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ msg })
  });

  const data = await res.json();
  box.removeChild(loadNode);
  addMsg(data.reply, 'bot');
  box.scrollTop = box.scrollHeight;
}

function addMsg(text, className) {
  const div = document.createElement('div');
  div.className = 'msg ' + className;
  div.innerHTML = text;
  box.appendChild(div);

  if (box.children.length > 50) {
    box.removeChild(box.firstChild);
  }
  return div;
}

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') send();
});
</script>
</body>
</html>
''')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        msg = data.get('msg', '').strip()
        if not msg:
            return jsonify({'reply': '请输入内容'})

        response = ollama.chat(
            model='qwen3:0.6b',
            messages=[{'role': 'user', 'content': msg}]
        )
        reply = response.message.content.strip()
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'错误：{str(e)}'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=11888, debug=False, use_reloader=False)
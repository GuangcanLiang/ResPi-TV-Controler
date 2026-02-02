#!/usr/bin/env python3
"""
TV Remote Control Server - 简化版
使用xdotool实现可靠的TV导航
"""

import subprocess
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CHROMIUM_CMD = "chromium"
CDP_PORT = 9222

def run_command(cmd):
    """执行shell命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def send_key(key):
    """发送键盘按键"""
    cmd = f"DISPLAY=:0 xdotool key {key}"
    success, _, _ = run_command(cmd)
    return success

@app.route('/api/open', methods=['POST'])
def open_chromium():
    """打开Chromium浏览器"""
    success, stdout, _ = run_command("pgrep chromium")
    if success:
        return jsonify({"success": True, "message": "Chromium已在运行"})
    
    try:
        # 使用chromium启动，启用远程调试
        cmd = f"DISPLAY=:0 nohup {CHROMIUM_CMD} --kiosk --no-first-run --disable-infobars --remote-debugging-port={CDP_PORT} --remote-allow-origins=* about:blank > /tmp/chromium.log 2>&1 &"
        os.system(cmd)
        import time
        time.sleep(3)
        return jsonify({"success": True, "message": "Chromium已启动"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/close', methods=['POST'])
def close_chromium():
    """关闭Chromium"""
    run_command("pkill chromium")
    return jsonify({"success": True, "message": "已关闭"})

@app.route('/api/navigate', methods=['POST'])
def navigate():
    """导航控制 - 使用Tab和方向键"""
    data = request.get_json()
    direction = data.get('direction', '')
    
    key_map = {
        'up': 'Up',
        'down': 'Down', 
        'left': 'Left',
        'right': 'Right',
        'enter': 'Return',
        'back': 'Escape',
        'tab': 'Tab',      # Tab键在网页间移动焦点
        'shift_tab': 'shift+Tab'  # Shift+Tab反向移动
    }
    
    if direction not in key_map:
        return jsonify({"success": False, "message": "无效的方向"}), 400
    
    key = key_map[direction]
    
    # 先激活Chromium窗口
    run_command("DISPLAY=:0 xdotool search --class chromium windowactivate")
    
    if send_key(key):
        return jsonify({"success": True, "message": f"已发送: {direction}"})
    else:
        return jsonify({"success": False, "message": "发送失败"}), 500

@app.route('/api/text', methods=['POST'])
def input_text():
    """输入文本"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"success": False, "message": "文本不能为空"}), 400
    
    # 激活窗口
    run_command("DISPLAY=:0 xdotool search --class chromium windowactivate")
    
    # 转义特殊字符
    escaped_text = text.replace('"', '\\"').replace("'", "\\'")
    cmd = f'DISPLAY=:0 xdotool type "{escaped_text}"'
    
    success, _, _ = run_command(cmd)
    if success:
        return jsonify({"success": True, "message": "文本已输入"})
    else:
        return jsonify({"success": False, "message": "输入失败"}), 500

@app.route('/api/url', methods=['POST'])
def open_url():
    """打开指定URL"""
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({"success": False, "message": "URL不能为空"}), 400
    
    # 确保Chromium已打开
    success, stdout, _ = run_command("pgrep chromium")
    if not success:
        open_chromium()
        import time
        time.sleep(2)
    
    # 激活窗口
    run_command("DISPLAY=:0 xdotool search --class chromium windowactivate")
    
    # 发送Ctrl+L聚焦地址栏
    run_command("DISPLAY=:0 xdotool key ctrl+l")
    
    # 输入URL
    escaped_url = url.replace('"', '\\"')
    run_command(f'DISPLAY=:0 xdotool type "{escaped_url}"')
    
    # 发送回车
    run_command("DISPLAY=:0 xdotool key Return")
    
    return jsonify({"success": True, "message": f"正在打开: {url}"})

@app.route('/api/click', methods=['POST'])
def mouse_click():
    """鼠标点击（发送回车键）"""
    run_command("DISPLAY=:0 xdotool search --class chromium windowactivate")
    if send_key('Return'):
        return jsonify({"success": True, "message": "已点击"})
    else:
        return jsonify({"success": False, "message": "点击失败"}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取状态"""
    success, stdout, _ = run_command("pgrep chromium")
    is_running = success and stdout.strip() != ""
    
    return jsonify({
        "success": True,
        "chromium_running": is_running,
        "server": "running"
    })

if __name__ == '__main__':
    print("=" * 50)
    print("TV Remote Control Server (简化版)")
    print("=" * 50)
    print("服务器启动在 http://0.0.0.0:5000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

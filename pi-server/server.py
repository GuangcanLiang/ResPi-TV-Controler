#!/usr/bin/env python3
"""
TV Remote Control Server for Raspberry Pi 5
通过HTTP API接收控制命令，控制Chromium浏览器
"""

import subprocess
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CHROMIUM_CMD = "chromium-browser"
CHROMIUM_PROCESS = None


def run_command(cmd):
    """执行shell命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def send_key(key):
    """发送键盘按键到Chromium窗口"""
    # 使用xdotool发送按键
    cmd = f"xdotool key {key}"
    success, stdout, stderr = run_command(cmd)
    return success


@app.route('/api/open', methods=['POST'])
def open_chromium():
    """打开Chromium浏览器"""
    global CHROMIUM_PROCESS
    
    # 检查Chromium是否已经在运行
    success, stdout, _ = run_command("pgrep chromium")
    if success:
        return jsonify({"success": True, "message": "Chromium已在运行"})
    
    # 在Kiosk模式下启动Chromium（适合电视显示）
    try:
        # 使用nohup让进程在后台运行
        cmd = f"DISPLAY=:0 nohup {CHROMIUM_CMD} --kiosk --no-first-run --disable-infobars about:blank > /tmp/chromium.log 2>&1 &"
        os.system(cmd)
        return jsonify({"success": True, "message": "Chromium已启动"})
    except Exception as e:
        return jsonify({"success": False, "message": f"启动失败: {str(e)}"}), 500


@app.route('/api/navigate', methods=['POST'])
def navigate():
    """导航控制：上下左右"""
    data = request.get_json()
    direction = data.get('direction', '')
    
    key_map = {
        'up': 'Up',
        'down': 'Down',
        'left': 'Left',
        'right': 'Right',
        'enter': 'Return',
        'back': 'Escape',
        'home': 'Home'
    }
    
    if direction not in key_map:
        return jsonify({"success": False, "message": "无效的方向"}), 400
    
    key = key_map[direction]
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
    
    # 转义特殊字符
    escaped_text = text.replace('"', '\\"').replace("'", "\\'")
    cmd = f'xdotool type "{escaped_text}"'
    
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
        # 先启动Chromium
        open_chromium()
        import time
        time.sleep(2)  # 等待启动
    
    # 激活Chromium窗口并输入URL
    cmd = f"xdotool search --class chromium windowactivate"
    run_command(cmd)
    
    # 发送Ctrl+L聚焦地址栏
    run_command("xdotool key ctrl+l")
    
    # 输入URL
    escaped_url = url.replace('"', '\\"')
    run_command(f'xdotool type "{escaped_url}"')
    
    # 发送回车
    run_command("xdotool key Return")
    
    return jsonify({"success": True, "message": f"正在打开: {url}"})


@app.route('/api/close', methods=['POST'])
def close_chromium():
    """关闭Chromium浏览器"""
    success, _, _ = run_command("pkill chromium")
    if success:
        return jsonify({"success": True, "message": "Chromium已关闭"})
    else:
        return jsonify({"success": False, "message": "关闭失败或Chromium未运行"}), 500


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


@app.route('/api/click', methods=['POST'])
def mouse_click():
    """鼠标点击（在电视遥控场景下，Enter键更常用）"""
    if send_key('Return'):
        return jsonify({"success": True, "message": "已点击"})
    else:
        return jsonify({"success": False, "message": "点击失败"}), 500


if __name__ == '__main__':
    # 在树莓派上运行，监听所有接口，端口5000
    print("=" * 50)
    print("TV Remote Control Server")
    print("=" * 50)
    print("服务器启动在 http://0.0.0.0:5000")
    print("API端点:")
    print("  POST /api/open     - 打开Chromium")
    print("  POST /api/close    - 关闭Chromium")
    print("  POST /api/navigate - 导航 (direction: up/down/left/right/enter/back)")
    print("  POST /api/text     - 输入文本 (text: 要输入的内容)")
    print("  POST /api/url      - 打开URL (url: 网址)")
    print("  POST /api/click    - 点击/确认")
    print("  GET  /api/status   - 获取状态")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
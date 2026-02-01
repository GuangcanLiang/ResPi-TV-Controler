#!/usr/bin/env python3
"""
TV Remote Control Server - Chrome DevTools Protocol版本
通过CDP实现TV模式的焦点导航（带红色高亮框）
"""

import asyncio
import json
import subprocess
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CDP_PORT = 9222
current_focus_index = -1

# 高亮框JavaScript
HIGHLIGHT_SCRIPT = """
(function() {
    var old = document.getElementById('tv-focus-highlight');
    if (old) old.remove();
    
    var div = document.createElement('div');
    div.id = 'tv-focus-highlight';
    div.style.cssText = 'position: fixed; z-index: 999999; pointer-events: none; border: 4px solid #ff0000; box-shadow: 0 0 20px #ff0000; transition: all 0.2s ease; border-radius: 4px;';
    document.body.appendChild(div);
    
    function update() {
        var focused = document.activeElement;
        if (focused && focused !== document.body) {
            var rect = focused.getBoundingClientRect();
            div.style.left = (rect.left - 4) + 'px';
            div.style.top = (rect.top - 4) + 'px';
            div.style.width = (rect.width + 8) + 'px';
            div.style.height = (rect.height + 8) + 'px';
            div.style.display = 'block';
        } else {
            div.style.display = 'none';
        }
    }
    
    update();
    setInterval(update, 100);
    return 'TV highlight initialized';
})()
"""

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def get_cdp_url():
    try:
        resp = requests.get(f'http://localhost:{CDP_PORT}/json', timeout=2)
        data = resp.json()
        if data:
            return data[0].get('webSocketDebuggerUrl')
    except:
        pass
    return None

def execute_js(script):
    """通过CDP执行JavaScript"""
    import websocket
    ws_url = get_cdp_url()
    if not ws_url:
        return None
    try:
        ws = websocket.create_connection(ws_url, timeout=5)
        ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
        response = ws.recv()
        ws.close()
        return json.loads(response)
    except:
        return None

def find_elements():
    """查找所有可聚焦元素"""
    script = """
    (function() {
        var all = document.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"]), [onclick], [role="button"], h1, h2, h3, h4, h5, h6, p, span, div');
        var visible = [];
        all.forEach(function(el) {
            var rect = el.getBoundingClientRect();
            if (rect.width > 10 && rect.height > 10 && rect.top >= 0 && rect.left >= 0) {
                visible.push({
                    x: rect.left + rect.width/2,
                    y: rect.top + rect.height/2,
                    tag: el.tagName
                });
            }
        });
        return visible;
    })()
    """
    resp = execute_js(script)
    if resp and 'result' in resp:
        return resp['result'].get('value', [])
    return []

def focus_element(index):
    """聚焦指定索引的元素"""
    global current_focus_index
    elements = find_elements()
    if 0 <= index < len(elements):
        current_focus_index = index
        script = f"""
        (function() {{
            var all = document.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"]), [onclick], [role="button"], h1, h2, h3, h4, h5, h6, p, span, div');
            var visible = Array.from(all).filter(el => {{
                var rect = el.getBoundingClientRect();
                return rect.width > 10 && rect.height > 10;
            }});
            if (visible[{index}]) {{
                visible[{index}].focus();
                visible[{index}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                // 添加点击效果
                visible[{index}].style.outline = '4px solid #ff0000';
                setTimeout(() => visible[{index}].style.outline = '', 500);
                return 'focused';
            }}
            return 'not found';
        }})()
        """
        execute_js(script)
        return True
    return False

def navigate_direction(direction):
    """按方向导航"""
    global current_focus_index
    elements = find_elements()
    if not elements:
        return False
    
    if current_focus_index < 0:
        current_focus_index = 0
        return focus_element(0)
    
    current = elements[current_focus_index]
    candidates = []
    
    for i, el in enumerate(elements):
        if i == current_focus_index:
            continue
        dx = el['x'] - current['x']
        dy = el['y'] - current['y']
        dist = (dx**2 + dy**2) ** 0.5
        
        if direction == 'up' and dy < -30:
            candidates.append((i, dist, abs(dx)))
        elif direction == 'down' and dy > 30:
            candidates.append((i, dist, abs(dx)))
        elif direction == 'left' and dx < -30:
            candidates.append((i, dist, abs(dy)))
        elif direction == 'right' and dx > 30:
            candidates.append((i, dist, abs(dy)))
    
    if candidates:
        candidates.sort(key=lambda x: (x[1], x[2]))
        return focus_element(candidates[0][0])
    
    return False

@app.route('/api/open', methods=['POST'])
def open_chromium():
    success, stdout, _ = run_command("pgrep chromium")
    if success:
        execute_js(HIGHLIGHT_SCRIPT)
        return jsonify({"success": True, "message": "Chromium已在运行"})
    
    try:
        cmd = f"DISPLAY=:0 nohup chromium-browser --kiosk --no-first-run --disable-infobars --remote-debugging-port={CDP_PORT} --remote-allow-origins=* about:blank > /tmp/chromium.log 2>&1 &"
        os.system(cmd)
        import time
        time.sleep(4)
        execute_js(HIGHLIGHT_SCRIPT)
        return jsonify({"success": True, "message": "Chromium已启动"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/close', methods=['POST'])
def close_chromium():
    global current_focus_index
    run_command("pkill chromium")
    current_focus_index = -1
    return jsonify({"success": True, "message": "已关闭"})

@app.route('/api/navigate', methods=['POST'])
def navigate():
    data = request.get_json()
    direction = data.get('direction', '')
    
    if direction in ['enter', 'back']:
        key = 'Return' if direction == 'enter' else 'Escape'
        run_command(f"xdotool key {key}")
        return jsonify({"success": True, "message": direction})
    
    result = navigate_direction(direction)
    if result:
        return jsonify({"success": True, "message": f"已{direction}导航"})
    return jsonify({"success": False, "message": "无可用元素"})

@app.route('/api/text', methods=['POST'])
def input_text():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"success": False, "message": "文本为空"}), 400
    
    escaped = text.replace('"', '\\"')
    run_command(f'xdotool type "{escaped}"')
    return jsonify({"success": True, "message": "已输入"})

@app.route('/api/url', methods=['POST'])
def open_url():
    data = request.get_json()
    url = data.get('url', '')
    if not url:
        return jsonify({"success": False, "message": "URL为空"}), 400
    
    success, _, _ = run_command("pgrep chromium")
    if not success:
        open_chromium()
        import time
        time.sleep(2)
    
    try:
        requests.post(f'http://localhost:{CDP_PORT}/json', timeout=1)
    except:
        pass
    
    script = f'window.location.href = "{url}"'
    execute_js(script)
    import time
    time.sleep(1)
    execute_js(HIGHLIGHT_SCRIPT)
    
    return jsonify({"success": True, "message": f"打开: {url}"})

@app.route('/api/click', methods=['POST'])
def mouse_click():
    run_command("xdotool key Return")
    return jsonify({"success": True, "message": "已点击"})

@app.route('/api/status', methods=['GET'])
def get_status():
    success, stdout, _ = run_command("pgrep chromium")
    is_running = success and stdout.strip() != ""
    return jsonify({"success": True, "chromium_running": is_running, "server": "running"})

if __name__ == '__main__':
    print("=" * 50)
    print("TV Remote Server (TV模式/CDP)")
    print("=" * 50)
    print("地址: http://0.0.0.0:5000")
    print("功能: TV焦点导航 + 红色高亮框")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)

# TV Remote Control Server

在树莓派5上运行的控制服务端，通过HTTP API接收来自Android手机的控制命令。

## 功能

- 打开/关闭 Chromium 浏览器
- 方向键控制（上、下、左、右）
- 输入文本
- 打开指定URL
- 确认/返回操作

## 系统要求

- Raspberry Pi 5
- Raspberry Pi OS (64-bit)
- Python 3.9+
- HDMI连接的显示设备（电视）

## 安装

```bash
cd pi-server
chmod +x install.sh
./install.sh
```

## 手动安装依赖

```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3 python3-pip xdotool chromium-browser

# 安装Python依赖
pip3 install flask flask-cors
```

## 启动服务器

### 方式1：直接运行

```bash
python3 server.py
```

### 方式2：使用systemd服务（推荐）

```bash
sudo cp tv-remote.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tv-remote
sudo systemctl start tv-remote
```

查看服务状态：
```bash
sudo systemctl status tv-remote
```

## API接口

服务器运行在 `http://<树莓派IP>:5000`

### 1. 打开Chromium
```bash
POST /api/open
```

### 2. 关闭Chromium
```bash
POST /api/close
```

### 3. 导航控制
```bash
POST /api/navigate
Content-Type: application/json

{
  "direction": "up"  // up, down, left, right, enter, back, home
}
```

### 4. 输入文本
```bash
POST /api/text
Content-Type: application/json

{
  "text": "要输入的文本"
}
```

### 5. 打开URL
```bash
POST /api/url
Content-Type: application/json

{
  "url": "https://www.youtube.com"
}
```

### 6. 点击/确认
```bash
POST /api/click
```

### 7. 获取状态
```bash
GET /api/status
```

## 网络配置

确保树莓派和手机在同一个WiFi网络下。获取树莓派IP地址：

```bash
hostname -I
```

## 日志

如果使用systemd服务，查看日志：
```bash
sudo journalctl -u tv-remote -f
```
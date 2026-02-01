#!/bin/bash

# TV Remote Control Server 安装脚本
# 用于在树莓派5上安装必要的依赖

echo "======================================"
echo "TV Remote Control Server 安装"
echo "======================================"

# 更新系统
echo "[1/5] 更新系统包..."
sudo apt-get update

# 安装Python3和pip
echo "[2/5] 安装Python3和pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# 安装xdotool（用于模拟键盘输入）
echo "[3/5] 安装xdotool..."
sudo apt-get install -y xdotool

# 安装Chromium浏览器
echo "[4/5] 安装Chromium浏览器..."
sudo apt-get install -y chromium-browser

# 创建虚拟环境并安装Python依赖
echo "[5/5] 安装Python依赖..."
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "======================================"
echo "安装完成！"
echo "======================================"
echo "启动服务器命令:"
echo "  cd pi-server && source venv/bin/activate && python server.py"
echo ""
echo "或者使用systemd服务（推荐）:"
echo "  sudo cp tv-remote.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable tv-remote"
echo "  sudo systemctl start tv-remote"
echo "======================================"
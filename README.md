# TV Remote Control Project

这是一个电视遥控器项目，包含两个部分：
1. **树莓派服务端** (pi-server/) - 在树莓派5上运行的Python服务
2. **Android遥控器** (android-app/) - 在安卓手机上运行的遥控应用

## 项目结构

```
tv-remote-control/
├── pi-server/           # 树莓派服务端
│   ├── server.py       # 主服务程序
│   ├── requirements.txt # Python依赖
│   ├── install.sh      # 安装脚本
│   ├── tv-remote.service # systemd服务配置
│   └── README.md       # 服务端说明文档
├── android-app/        # Android遥控器应用
│   ├── app/           # App模块
│   ├── build.gradle   # 项目构建配置
│   └── README.md      # Android应用说明文档
├── AGENTS.md          # 本文件 - 项目指南
└── README.md          # 项目总说明
```

## 快速开始

### 1. 树莓派服务端

```bash
cd pi-server
chmod +x install.sh
./install.sh
python3 server.py
```

### 2. Android应用

用Android Studio打开 `android-app` 文件夹，构建并安装到手机。

## 依赖安装记录

### 树莓派已安装依赖

#### 系统包
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv xdotool chromium-browser
```

#### Python包
```bash
pip3 install flask flask-cors
```

### Android开发环境
- Android Studio Hedgehog (2023.1.1)
- Kotlin 1.9.0
- Gradle 8.0+
- Android SDK 34

## 网络配置

确保树莓派和手机连接在同一WiFi网络下。

获取树莓派IP：
```bash
hostname -I
```

## 技术栈

- **服务端**: Python 3, Flask, xdotool, Chromium
- **客户端**: Kotlin, Android SDK, Retrofit, Material Design 3
- **通信**: HTTP REST API (端口5000)

## 版本信息

- 项目版本: 1.0.0
- 创建日期: 2026-01-31
- 目标平台: Raspberry Pi 5 + Android 7.0+
#!/bin/bash
# 手动构建TV Remote Control APK脚本
# 不依赖Gradle，直接使用Android SDK命令行工具

set -e

echo "=== TV Remote Control 手动APK构建脚本 ==="
echo ""

# 设置环境变量
export ANDROID_HOME=/usr/lib/android-sdk
export PATH=$PATH:$ANDROID_HOME/build-tools/debian:$ANDROID_HOME/platform-tools

# 项目路径
PROJECT_DIR="$HOME/controler/tv-remote-control/android-app"
APP_DIR="$PROJECT_DIR/app"
BUILD_DIR="$APP_DIR/build"

# 创建工作目录
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/gen"
mkdir -p "$BUILD_DIR/obj"
mkdir -p "$BUILD_DIR/apk"
mkdir -p "$BUILD_DIR/classes"

echo "1. 生成R.java..."
aapt package -f -m \
    -J "$BUILD_DIR/gen" \
    -S "$APP_DIR/src/main/res" \
    -M "$APP_DIR/src/main/AndroidManifest.xml" \
    -I "$ANDROID_HOME/platforms/android-28/android.jar"

echo "2. 编译Kotlin源文件..."
# 找到kotlin-stdlib.jar
KOTLIN_STDLJAR=$(find /usr/share/java -name "kotlin-stdlib*.jar" 2>/dev/null | head -1)
if [ -z "$KOTLIN_STDLJAR" ]; then
    echo "错误: 找不到kotlin-stdlib.jar"
    exit 1
fi

echo "   使用: $KOTLIN_STDLJAR"

# 编译Kotlin文件（使用kotlinc if available）
# 注意：这种方法需要kotlin编译器，但apt安装的gradle不包含kotlinc

echo ""
echo "注意：此方法需要Kotlin编译器(kotlinc)，但系统安装的Gradle不包含。"
echo ""
echo "建议改用以下方法之一："
echo ""
echo "方法1: 在PC上构建（推荐）"
echo "   - 在Windows/Mac/Linux上安装Android Studio"
echo "   - 导入tv-remote-control/android-app项目"
echo "   - 点击'Build -> Build APK'"
echo ""
echo "方法2: 使用Docker构建"
echo "   docker run --rm -v $(pwd):/project mingc/android-build-box:latest bash -c \"cd /project && ./gradlew assembleDebug\""
echo ""
echo "方法3: 使用在线构建服务"
echo "   - GitHub Actions"
echo "   - GitLab CI"
echo "   - 或其他CI/CD服务"
echo ""

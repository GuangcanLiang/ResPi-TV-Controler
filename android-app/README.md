# TV Remote - Android App

电视遥控器Android应用，用于控制连接在树莓派5上的Chromium浏览器。

## 功能

- 连接树莓派服务器
- 打开/关闭Chromium浏览器
- 方向键控制（上、下、左、右）
- 确认/返回操作
- 输入文本到浏览器

## 系统要求

- Android 7.0 (API 24) 或更高版本
- 与树莓派在同一WiFi网络下

## 开发环境

- Android Studio Hedgehog (2023.1.1) 或更高版本
- Kotlin 1.9.0
- Gradle 8.0+

## 构建步骤

### 1. 打开项目

在Android Studio中打开 `android-app` 文件夹。

### 2. 同步Gradle

等待Gradle同步完成，下载必要的依赖。

### 3. 构建APK

**方式1：通过Android Studio**
- Build → Build Bundle(s) / APK(s) → Build APK(s)

**方式2：命令行**
```bash
cd android-app
./gradlew assembleDebug
```

APK文件将生成在：`app/build/outputs/apk/debug/app-debug.apk`

### 4. 安装到手机

**方式1：通过Android Studio**
- 连接手机，点击 Run 按钮

**方式2：通过ADB**
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

**方式3：手动安装**
- 将APK文件复制到手机
- 在文件管理器中点击安装

## 使用说明

1. 确保树莓派服务端已启动
2. 在应用设置中输入树莓派的IP地址
3. 点击"连接"按钮
4. 连接成功后即可使用遥控器功能

## 查找树莓派IP

在树莓派终端执行：
```bash
hostname -I
```

## 项目结构

```
android-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/tvremote/app/
│   │   │   ├── MainActivity.kt          # 主界面
│   │   │   ├── RemoteApiService.kt      # API接口定义
│   │   │   └── RetrofitClient.kt        # HTTP客户端
│   │   └── res/                         # 资源文件
│   └── build.gradle                     # App模块构建配置
├── build.gradle                         # 项目构建配置
└── settings.gradle                      # 项目设置
```

## 依赖库

- Retrofit 2.9.0 - HTTP客户端
- Gson Converter - JSON解析
- OkHttp Logging Interceptor - 日志记录
- Material Design 3 - UI组件

## 注意事项

- 应用需要网络权限，请确保已授权
- 树莓派和手机必须在同一局域网内
- 默认使用HTTP协议（端口5000）
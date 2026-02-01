# AGENTS.md - TV Remote Control Project

This file provides guidance for AI agents working on this codebase.

## Project Overview

A TV remote control system consisting of:
1. **Pi Server** (`pi-server/`) - Python Flask server running on Raspberry Pi 5
2. **Android App** (`android-app/`) - Kotlin Android remote control application

The Android app communicates with the Pi server via HTTP API to control a Chromium browser displayed on TV via HDMI.

## Build & Development Commands

### Pi Server (Python)

```bash
cd pi-server

# Install dependencies
./install.sh
# OR manually:
sudo apt-get install -y python3 python3-pip xdotool chromium-browser
pip3 install flask flask-cors

# Run server
python3 server.py

# Test endpoints
curl -X POST http://localhost:5000/api/open
curl -X POST http://localhost:5000/api/navigate -H "Content-Type: application/json" -d '{"direction":"up"}'
curl -X POST http://localhost:5000/api/text -H "Content-Type: application/json" -d '{"text":"hello"}'
```

### Android App

```bash
cd android-app

# Build debug APK
./gradlew assembleDebug

# Install to device
adb install app/build/outputs/apk/debug/app-debug.apk

# Clean build
./gradlew clean
```

## Code Style Guidelines

### Python (Pi Server)

- **Imports**: Standard library first, then third-party, then local
- **Formatting**: PEP 8, 4-space indentation
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Types**: Use type hints where beneficial
- **Error Handling**: Use try-except blocks, return meaningful error messages in JSON
- **Comments**: Docstrings for functions, inline comments for complex logic

Example:
```python
def send_key(key: str) -> bool:
    """Send keyboard key to Chromium window."""
    try:
        cmd = f"xdotool key {key}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        print(f"Error sending key: {e}")
        return False
```

### Kotlin (Android)

- **Imports**: Android/Jetpack first, then Kotlin stdlib, then third-party
- **Formatting**: Kotlin Coding Conventions, 4-space indentation
- **Naming**: `camelCase` for functions/properties, `PascalCase` for classes
- **Null Safety**: Use `?` and `?:` operators, avoid `!!` unless necessary
- **Coroutines**: Use for async operations (currently using callbacks, can be improved)
- **View Binding**: Always use view binding, avoid `findViewById` in new code

Example:
```kotlin
private fun sendNavigate(direction: String) {
    apiService?.navigate(NavigateRequest(direction))
        ?.enqueue(createCallback(direction))
}
```

## Architecture

### Pi Server Architecture

- **server.py**: Main Flask application
- **Routes**: RESTful API endpoints under `/api/`
- **External Tools**: Uses `xdotool` for keyboard/mouse simulation
- **CORS**: Enabled for cross-origin requests from Android app

### Android App Architecture

- **MainActivity.kt**: Single activity with all UI controls
- **RemoteApiService.kt**: Retrofit interface for API calls
- **RetrofitClient.kt**: Singleton HTTP client configuration
- **Layout**: XML-based with ConstraintLayout and LinearLayout

## API Endpoints

Base URL: `http://<pi-ip>:5000`

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/api/open` | - | Open Chromium |
| POST | `/api/close` | - | Close Chromium |
| POST | `/api/navigate` | `{"direction":"up"}` | Navigation (up/down/left/right/enter/back) |
| POST | `/api/text` | `{"text":"input"}` | Type text |
| POST | `/api/url` | `{"url":"http://..."}` | Open URL |
| POST | `/api/click` | - | Mouse click |
| GET | `/api/status` | - | Get server/browser status |

## Dependencies

### System Requirements (Pi)

- Python 3.9+
- xdotool (for input simulation)
- Chromium browser

### Android Dependencies

- Retrofit 2.9.0 (HTTP client)
- Gson (JSON parsing)
- Material Design 3 (UI)

## Testing

### Manual Testing Checklist

- [ ] Server starts without errors
- [ ] Android app connects successfully
- [ ] Can open Chromium browser
- [ ] Direction buttons work
- [ ] Text input works
- [ ] Can close browser
- [ ] Status endpoint returns correct info

## Common Issues

1. **Cannot connect**: Check firewall, ensure port 5000 is open
2. **xdotool fails**: Ensure X11 display is available (`DISPLAY=:0`)
3. **Chromium won't start**: Check if already running with `pgrep chromium`
4. **Android HTTP errors**: Ensure `android:usesCleartextTraffic="true"` in manifest

## Git Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add text input feature"

# View history
git log --oneline -10
```

## Security Notes

- Server listens on all interfaces (`0.0.0.0`) - only use on trusted networks
- No authentication implemented - add if exposing to internet
- HTTP (not HTTPS) - acceptable for local network only

## Future Improvements

- Add WebSocket support for real-time bidirectional communication
- Implement voice control
- Add configuration UI for custom URLs
- Support multiple browser profiles
- Add media control buttons (play/pause/volume)
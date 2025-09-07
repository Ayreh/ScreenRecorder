# OBS Companion Tracker V2 LATEST

## 核心原理
1. **OBS 同步机制**：通过 OBS WebSocket 接口实时监测 OBS 录制状态（开始/停止），实现输入记录与 OBS 录制的自动同步，确保时间戳对齐。
2. **输入捕获方式**：
   - 使用 `pynput` 库捕获鼠标（移动轨迹、按键、滚轮）和键盘（按键按下/释放）事件
   - 对键盘事件转换为 Windows 虚拟键码（VK_CODE），便于标准化处理
3. **日志生成逻辑**：
   - 生成与 OBS 视频文件同名的 JSONL 格式日志
   - 首行为元数据（设备信息、OBS 版本、采样率等）
   - 后续行为输入事件，包含 OBS 对齐的时间戳、事件类型和详细数据

## 呈现效果
1. **GUI 界面**：
   - 包含 OBS 连接配置区（主机、端口、密码输入）
   - 显示连接状态、录制状态（是否同步中）
   - 提供手动开始/停止录制的控制按钮
   - 实时展示事件计数（总事件、鼠标事件、键盘事件）
2. **日志文件**：
   - 默认保存在用户「Videos」文件夹，与 OBS 视频文件同名（后缀为 .jsonl）
   - 每行一个 JSON 对象，可直接用于后期分析（如与视频同步回放输入操作）
3. **运行表现**：
   - 随 OBS 录制自动启停，无需手动干预
   - 30Hz 固定采样率，平衡记录精度与性能消耗
   - 支持硬件级输入捕获，适配多数鼠标和键盘设备   
***
# OBS Companion Tracker V2 LATEST

## Core Principles
1. **OBS Sync Mechanism**: Monitors OBS recording status (start/stop) in real-time via the OBS WebSocket interface, enabling automatic synchronization between input recording and OBS video capture for precise timestamp alignment.
2. **Input Capture Method**:
   - Captures mouse (movement轨迹, clicks, scroll) and keyboard (key press/release) events using the `pynput` library
   - Converts keyboard events to Windows Virtual Key Codes (VK_CODE) for standardized processing
3. **Log Generation Logic**:
   - Generates JSONL format logs with the same name as OBS video files
   - First line contains metadata (device info, OBS version, sampling rate, etc.)
   - Subsequent lines record input events with OBS-aligned timestamps, event types, and detailed data

## Presentation Effects
1. **GUI Interface**:
   - Includes OBS connection configuration area (host, port, password input)
   - Displays connection status and recording status (whether sync is active)
   - Provides control buttons for manual start/stop of recording
   - Shows real-time event counters (total events, mouse events, keyboard events)
2. **Log Files**:
   - Saved by default in the user's "Videos" folder, with the same name as OBS video files (suffix `.jsonl`)
   - Each line is a JSON object, directly usable for post-analysis (e.g., syncing input operations with video playback)
3. **Operational Performance**:
   - Automatically starts/stops with OBS recording, no manual intervention required
   - Fixed 30Hz sampling rate, balancing recording precision and performance consumption
   - Supports hardware-level input capture, compatible with most mouse and keyboard devices
***   
# ScreenRecorder --- OLD VERSION
A dedicated screen recording tool optimized for capturing gameplay footage, with additional tracking of mouse and keyboard inputs. This tool uses FFmpeg for high-performance video encoding and provides an easy-to-use GUI.
## Features
* Full-Screen Recording: Captures entire desktop with customizable frame rates
* Input Logging: Records detailed mouse movements, clicks, and keyboard activity
* Quality Presets: Three quality settings (low/medium/high) to balance file size and performance
* FPS Control: Choose from 15, 24, 30, or 60 frames per second
* Convenient Controls: Simple GUI with start/stop buttons and F10 hotkey to stop recording
* Bundled FFmpeg: Includes FFmpeg for out-of-the-box functionality (no separate installation required)
* Timestamped Files: Automatically names files with timestamps to prevent overwrites
* Real-time Duration Tracking: Displays elapsed recording time
## Usage Guide
* Select Save Location: Click "Choose Directory" to select where your recordings will be saved
* Adjust Settings:
  * Select desired frame rate (FPS)
  * Choose quality preset:
     * Low: Fast encoding, smaller file size
    * Medium: Balanced quality and performance (default)
    * High: Best quality, larger file size
* Start Recording: Click "🔴 Start Recording"
* Stop Recording: Either click "⏹️ Stop Recording" in the GUI or press the F10 key
*View your recordings in the selected save directory

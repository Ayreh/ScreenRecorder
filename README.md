# obs tracker V2.1 update

## Gamepad Tracking
Gamepad tracking is a core extension of this tool, implemented using the Pygame library. It focuses on accurately capturing input operations from various gamepads, providing structured input data for scenarios such as game operation review, live stream interaction analysis, and player behavior research. This feature is compatible with mainstream gamepad devices, requiring no manual configuration of device protocols, and can automatically recognize and record complete operation processes.

### 1. Feature Overview
- **Device Compatibility**: Supports Xbox Series X/S controllers, PS5 controllers, Switch Pro controllers, generic USB gamepads, and other mainstream devices. Achieves cross-device adaptation through Pygame's unified interface, eliminating the need to distinguish between XInput/DirectInput protocols.
- **Core Value**: Real-time synchronization with OBS recording progress. All input events carry timestamps to ensure precise alignment between gamepad operation data and video content, facilitating subsequent frame-by-frame analysis.
- **Data Integrity**: Covers all types of gamepad inputs (buttons, sticks, triggers, D-pad) without missing operations, while filtering invalid jitter data to ensure log conciseness.


### 2. Supported Event Types

#### 1. Button Events
- Capture Range: Covers the complete operation lifecycle of all physical buttons on the gamepad, including:
  - Core action buttons: A/B/X/Y (or equivalent buttons on corresponding platforms, such as ×/○/□/△ on PS controllers);
  - Shoulder buttons: LB (left shoulder), RB (right shoulder);
  - Function buttons: Back, Start, Home (device wake-up button);
  - Stick press buttons: Physical press actions of left stick (L3) and right stick (R3).
- Recording Dimensions: Each event includes "universal button name", "raw hardware key code", and "operation state (press/release)" to ensure unique identification of each button.

#### 2. Analog Stick Events
- Capture Range: X-axis (horizontal) and Y-axis (vertical) displacement of both left and right sticks, reflecting real-time physical offset of the sticks.
- Recording Dimensions:
  - Stick identifier: Clearly distinguishes between "left_stick" and "right_stick";
  - Axis direction: Indicates the axis (x/y) of displacement;
  - Value precision: Records both "raw hardware values (-32768~32767, corresponding to physical stick travel)" and "normalized values (-1.0~1.0, facilitating cross-device proportion calculation)";
  - Jitter filtering: Only records displacements with normalized values exceeding 0.1 in absolute value (filters minor hardware jitter to reduce redundant logs).

#### 3. Trigger Events
- Capture Range: Linear pressure input from left and right triggers (LT/left trigger, RT/right trigger), supporting detailed operation recording for pressure-sensitive devices.
- Recording Dimensions:
  - Trigger identifier: Clearly distinguishes between "left_trigger" and "right_trigger";
  - Pressure value: Range 0~1023 (0 indicates full release, 1023 indicates full press), accurately reflecting pressure intensity.

#### 4. D-pad Events
- Capture Range: All directional inputs from the cross-shaped D-pad, including single directions (up/down/left/right), combined directions (up-left/down-left/up-right/down-right), and neutral state.
- Recording Dimensions:
  - D-pad identifier: Uniformly labeled as "dpad_0" (adapts to single D-pad devices);
  - Direction description: Human-readable direction names (e.g., "up", "left_down", "neutral");
  - Raw coordinates: Original X/Y axis input values (-1/0/1, corresponding to directional offsets), facilitating low-level data verification.

### 3. Technical Implementation Details
1. **Dependency Library**: Developed based on the `pygame.joystick` module of the Pygame framework, utilizing its native support for gamepads to simplify device detection and event monitoring logic.
2. **Device Management**:
   - Automatically scans for connected gamepads in the system and returns the number of devices in real-time;
   - By default, tracks the "first detected active gamepad" (index 0). Multi-gamepad simultaneous recording is not currently supported to avoid data confusion.
3. **Performance Optimization**:
   - Fixed sampling rate: 30Hz (approximately one data collection every 33ms), balancing operation precision and system resource usage. CPU usage remains below 5% during single-device tracking;
   - Thread isolation: Gamepad event monitoring runs in an independent thread, with no blocking conflicts with GUI rendering or OBS status monitoring, ensuring smooth interface performance.
4. **Data Synchronization**:
   - Timestamp reference: Uses OBS recording-synchronized internal timestamps (millisecond precision) to eliminate time differences between operations and video;
   - Log integration: Gamepad events, mouse events, and keyboard events are uniformly written to the same JSONL log file, arranged in chronological order for convenient batch parsing.
  
## UI Update
### Modern Visual Design
- Adopts a dark theme color scheme (#1a1a1a for background, #2a2a2a for frames, #00d4ff for accent color), enhancing visual comfort and reducing eye fatigue during prolonged use.

### Scroll Function Support
- Newly added scrollable areas with mouse wheel support, solving the display issue when there is excessive content. All functional areas can be viewed completely even in small windows.

### Partition Layout Optimization
- Functions are divided into four independent areas - "OBS Connection", "Recording Status", "Settings", and "Manual Control", resulting in clearer logic.

***
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

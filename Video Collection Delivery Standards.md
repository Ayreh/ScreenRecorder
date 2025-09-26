# Video Collection Delivery Standards

## 1. Introduction
To clarify the collection standards and delivery process for game screen recording, this MD document is introduced.

## 2. Basic Environment and Compatibility Requirements  

### 2.1 System Environment  
#### 2.1.1 Operating System Version Requirements  
- **Supported Systems**:  
  - Windows 10 64-bit (Professional/Enterprise Edition, version ≥1903)  
  - Windows 11 64-bit (Professional/Enterprise Edition, version ≥21H2)  
- **Excluded Scope**:  
  - 32-bit Windows systems (do not support 64-bit exe programs)  
  - Linux/macOS systems (exe programs depend on Windows environment)  
  - Windows Home Edition (some group policy restrictions may cause OBS performance instability)  

#### 2.1.2 Minimum Hardware Configuration Standards  
| Hardware Type       | Minimum Configuration                          | Recommended Configuration                          | Remarks                                  |  
|---------------------|------------------------------------------------|----------------------------------------------------|------------------------------------------|  
| CPU                 | Intel i5-8400 / AMD Ryzen 5 2600               | Intel i7-10700 / AMD Ryzen 7 5800X                | Ensure multi-threaded collection (video + input) without lag    |  
| Memory              | 8GB DDR4 2666MHz                               | 16GB DDR4 3200MHz                                  | Avoid memory overflow during high-resolution video recording        |  
| Storage             | 100GB free space (SSD/HDD)                     | 500GB free space (NVMe SSD)                        | SSD preferred: Improve video write speed, reduce frame drops  |  
| Graphics Card       | Intel UHD 630 / NVIDIA GTX 1050                | NVIDIA RTX 3060 / AMD RX 6600                      | Support hardware encoding (NVENC/AMF), reduce CPU load |  
| Network (Optional)  | 100Mbps wired network                          | 1Gbps wired network                                | Only for data upload phase, no mandatory requirement for local collection |  


### 2.2 Software Dependencies  
#### 2.2.1 Required Software Version List  
| Software Name              | Version Requirement       | Role                                  | Installation Instructions                                                             |  
|----------------------------|---------------------------|---------------------------------------|-------------------------------------------------------------------------------|  
| OBS Studio                 | ≥27.0.0 (64-bit)          | Core video collection tool            | Download from official website: https://obsproject.com/                      |  
| Self-developed Input Collection Program | obs_tracker_V2.1 | Keyboard, mouse, and controller operation recording | Obtain from GitHub (provides standalone exe file, no installation required): https://github.com/Ayreh/ScreenRecorder|  

#### 2.2.2 Key Plugins and Built-in Components  
| Component Name              | Version Requirement       | Belonging Program         | Description                                  |  
|-----------------------------|---------------------------|---------------------------|----------------------------------------------|  
| obs-websocket               | ≥5.0.1                    | OBS Studio                | Manually enable (see 2.2.3), used for OBS and self-developed program status synchronization |  
| (Built-in) pynput           | 1.7.6                     | Self-developed exe program| Encapsulated in exe, used to capture mouse/keyboard events  |  
| (Built-in) pygame           | 2.1.0                     | Self-developed exe program| Encapsulated in exe, used to capture controller events        |  
| (Built-in) obsws-python     | 1.2.0                     | Self-developed exe program| Encapsulated in exe, used to parse OBS WebSocket protocol |  

#### 2.2.3 Configuration Verification  
- **OBS Configuration**:  
  Open OBS → Tools → WebSocket Server Settings → Check “Enable WebSocket server”, record port (default 4455) and password (if set), click “Apply” to save.  
- **Self-developed Program Verification**:  
  Download `obs_tracker_V2.1.exe` from GitHub → Double-click to run → The program automatically reads system device information, displaying “Initialization Complete” on the interface indicates normal startup (first run generates configuration file, path: `C:\Users\[Username]\AppData\Local\OBSTracker\config.ini`).  


### 2.3 Device Compatibility  
#### 2.3.1 Keyboard and Mouse  
- **Supported Types**:  
  - Keyboard: All USB/PS/2 wired keyboards, Bluetooth wireless keyboards (require Windows driver adaptation), including mechanical, membrane, and capacitive keyboards.  
  - Mouse: All USB/Bluetooth connected mice (support wheel, side buttons), including wired mice, 2.4G wireless mice (require matching receiver to work normally).  
- **Unsupported Cases**:  
  - Custom macro keyboards without installed drivers (may cause keycode recognition exceptions).  
  - Mouse DPI dynamic switching function (only records current DPI, does not track switching events).  

#### 2.3.2 Game Controller  
- **Supported Models**:  
  - Microsoft: Xbox Series X/S controller, Xbox One controller (wired/Bluetooth).  
  - Sony: PS5 DualSense controller, PS4 DualShock 4 controller (requires DS4Windows driver installation).  
  - Nintendo: Switch Pro controller (wired/Bluetooth).  
  - General: USB controllers compliant with DirectInput/XInput standards (such as Beitong, Razer series).  
- **Connection Methods**: Support USB wired connection, Bluetooth wireless connection (ensure Windows Bluetooth driver is normal).  
- **Limitations**:  
  - Only supports single controller recording (defaults to tracking the first controller recognized by the system).  
  - Does not support controller vibration feedback recording (only records input, not output).  

#### 2.3.3 Device Verification  
- Keyboard/Mouse: After connecting the device, confirm no yellow exclamation mark in “Device Manager” (driver normal), verify key response via `keyboardtester.com`.  
- Controller: After connecting, confirm the controller is recognized via “Control Panel → Devices and Printers”, run the self-developed program and check the interface “Device Status” column displays “Controller Connected” to indicate normal.


## 3. Collection Software Specifications  

### 3.1 Video Collection Software  
#### 3.1.1 Selection Standards  
- **Software Name**: OBS Studio (open source and free)  
- **Selection Basis**:  
  - Supports high-resolution, high-frame-rate video collection, compatible with mainstream game rendering modes (DirectX/OpenGL/Vulkan);  
  - Built-in WebSocket interface, can communicate in real-time with self-developed input collection program, ensuring recording status synchronization;  
  - Supports hardware encoding (NVENC/AMF/Quick Sync), balancing quality and performance consumption;  
  - Active community, timely version updates, compatible with Windows 10/11 systems.  
- **Version Requirement**: ≥27.0.0 (64-bit), recommended stable version 29.1.3 (verified by compatibility testing).  

#### 3.1.2 Core Configuration Requirements  
| Configuration Category       | Specific Requirements                                                                                                                                                                                                                                                                                                          | Configuration Path                                  |  
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|  
| WebSocket Settings           | - Enable WebSocket service: Check “Enable WebSocket server”<br>- Port: Default 4455 (if modified, must match self-developed program configuration)<br>- Authentication: Recommended to set password (≥8 characters, including numbers + letters), and synchronize in self-developed program                                    | OBS → Tools → WebSocket Server Settings             |  
| Recording Source Settings    | - Prioritize “Game Capture” source: Select “Mode → Capture specific window”, specify target game process (e.g., “GenshinImpact.exe”)<br>- Alternative: “Window Capture” (for non-fullscreen games) or “Display Capture” (not recommended, prone to redundant content)<br>- Disable “Preview Window”: Reduce GPU resource usage | OBS → Scene Collection → Add Source → Game Capture  |  
| Encoding Settings            | - Video Encoder: Select “Hardware Encoding” (e.g., NVIDIA NVENC H.264)<br>- Bitrate Control: CBR (Constant Bitrate)<br>- Bitrate: 1920×1080@60fps set to 15-20Mbps; 2560×1440@60fps set to 25-30Mbps                                                                                                                           | OBS → File → Settings → Output → Recording          |  
| Output Settings              | - Format: MP4 (compatible with mainstream players, supports repair after interruption)<br>- Filename Format: `[YYYY-MM-DD] [HH-MM-SS]` (e.g., “2024-09-25 14-30-00”)                                                                                                                                                           | OBS → File → Settings → Output → Recording          |  
| Performance Optimization     | - Disable “Vertical Sync”: Avoid screen delay<br>- Enable “Multi-threaded Encoding”: Improve encoding efficiency<br>- Frame Rate: Consistent with actual game frame rate (default 60fps)                                                                                                                                       | OBS → File → Settings → Video / Output              |  


### 3.2 Input Collection Software  
#### 3.2.1 Selection Standards  
- **Software Name**: Self-developed OBS Companion Program (obs_tracker_V2.1, exe format)  
- **Selection Basis**:  
  - Designed specifically for game screen recording scenarios, deeply adapted with OBS WebSocket, achieving millisecond-level status synchronization;  
  - Integrates full-type event collection for keyboard, mouse, and controller, data format strongly associated with video files (same name JSONL);  
  - Encapsulated as a single-file exe, no installation dependencies required, double-click to run, lowering usage threshold;  
  - Open source and traceable (GitHub repository: https://github.com/Ayreh/ScreenRecorder)

#### 3.2.2 Functional Requirements  
##### 3.2.2.1 Status Synchronization Function  
- **Synchronization Trigger Mechanism**:  
  - Automatically connect to OBS WebSocket after startup (requires correct address, port, password configuration);  
  - Real-time monitoring of OBS recording status: When OBS triggers “Start Recording”, automatically start keyboard, mouse, controller event collection; when OBS triggers “Stop Recording”, synchronously stop collection and generate integrity marker.  
- **Synchronization Accuracy**: Event timestamp deviation from OBS recording timestamp ≤1ms (real-time calibration via WebSocket protocol).  
- **Exception Synchronization Handling**:  
  - If OBS crashes, the program detects connection interruption and automatically stops collection and saves recorded data;  
  - If network fluctuation causes brief WebSocket disconnection (≤5s), automatically resume collection after reconnection (seamless timestamp connection).  

##### 3.2.2.2 Event Collection Scope  
| Device Type | Collection Object                  | Core Recorded Fields                                                                 | Collection Frequency/Trigger Condition                     |  
|-------------|------------------------------------|------------------------------------------------------------------------------|------------------------------------------------------------|  
| Mouse       | Displacement                       | X/Y axis raw physical displacement (hardware pulses, positive/negative indicating direction)                             | Real-time (triggered on mouse movement)                    |  
|             | Buttons                            | Button type (left/right/middle/side1/side2), state (press/release)             | Triggered on button actions                                |  
|             | Wheel                              | Scroll direction (positive +1/negative -1, based on hardware pulses)                                      | Triggered on wheel scroll                                  |  
| Keyboard    | Keys                               | Windows virtual key code (VK_CODE, e.g., A=0x41, Shift=0x10), state (press/release)      | Triggered on key actions (no character mapping, avoiding input method) |  
| Controller  | Action Buttons                     | Button name (a_button/b_button/x_button/y_button etc.), raw key code, state (press/release) | Triggered on button actions                                |  
|             | Shoulder/Special Keys              | Button name (lb_shoulder/rb_shoulder/back/start etc.), state (press/release)       | Triggered on button actions                                |  
|             | Sticks                             | Stick type (left_stick/right_stick), axis direction (x/y), raw value (-32768~32767), normalized value (-1.0~1.0) | Fixed 30Hz sampling (only record displacements >0.1 normalized value, filter jitter) |  
|             | Triggers                           | Trigger type (left_trigger/right_trigger), pressure value (0~1023, 0 for full release)         | Fixed 30Hz sampling (record on value change)               |  
|             | D-pad                              | Direction description (up/down/left/right/neutral etc.), raw X/Y coordinates (-1/0/1)               | Triggered on direction change                              |  

##### 3.2.2.3 Data Output Requirements  
- **File Format**: JSONL (one event per line, UTF-8 encoding), same name as corresponding video file (only suffix .jsonl);  
- **Metadata**: First line of file contains device information, recording start/end time, software version, etc. (see 4.2.2);  
- **Integrity Assurance**: Automatically append `"event_type": "SessionEnd"` marker after recording ends, used to verify file is not damaged.  

## 4. Delivery Content Standards  


### 4.1 Video Delivery Standards  
#### 4.1.1 Basic Parameter Specifications  
| Parameter Category       | Technical Requirements                                                                 | Description                                                                 |  
|--------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------|  
| Resolution               | Priority support: 1920×1080 (1080P)<br>Optional support: 2560×1440 (2K), 1280×720 (720P) | Must match actual game running resolution, prohibit stretching or scaling (avoid screen distortion); same batch recording must maintain uniform resolution |  
| Frame Rate               | Fixed 60fps (minimum not less than 30fps)                                      | Ensure smooth game operations, action games must meet 60fps; frame rate fluctuation ≤±1fps (monitor via OBS “Frame Rate Counter”) |  
| Encoding Format          | Video: H.264 (High Profile, Level 4.1)<br>Audio: AAC (LC Profile)              | Video bitrate control uses CBR (Constant Bitrate), audio sampling rate 48kHz, channels 2.0 (stereo)   |  
| Bitrate                  | 1080P@60fps: 15-20Mbps<br>2K@60fps: 25-30Mbps<br>720P@60fps: 8-12Mbps        | Balance quality and file size, avoid blurry screens due to low bitrate (especially in fast-moving scenes)   |  
| Color Space              | Rec.709 (standard high-definition color space)                                  | Ensure accurate color reproduction, consistent with original game screen                                 |  


#### 4.1.2 File Specifications  

- **Naming Rules**: `[YYYY-MM-DD] [HH-MM-SS].mp4`  
- **Example**:  
  - Recording started on September 25, 2024 at 14:30: `2024-09-25 14-30-00.mp4`
- **Constraints**:
  - Date and time accurate to seconds, consistent with OBS internal recording start time;


### 4.2 Operation Data Delivery Standards  
#### 4.2.1 Format Requirements  
- **File Format**: JSON Lines (JSONL), i.e., one independent JSON object per line, no nested arrays.  
- **Encoding Method**: UTF-8 (ensure normal display of Chinese device names, direction descriptions, etc.).  
- **File Size**: Split synchronously with video files (match corresponding video segment size), single JSONL file size usually 1%-5% of corresponding video file (depending on operation density).  
- **Naming Rules**: Correspond to the time of the corresponding video file, change suffix to `.jsonl` (example: `20240925_143000.jsonl`).  


#### 4.2.2 Core Field Specifications  
##### 4.2.2.1 Metadata (First Line of File)  
Metadata is in fixed format, containing basic information for traceability, example:  
```json
{
  "timestamp": 7.2e-05, 
  "absolute_time": 1758526531.944443, 
  "event_type": "SessionStart", 
  "details": 
  {
    "obs_sync": true,
    "start_time_unix": 1758526531.9443312, 
    "start_time_readable": "2025-09-22T15:35:31.944331", 
    "obs_connected": true, 
    "pynput_available": true,
    "gamepad_enabled": true, 
    "pygame_available": true,
    "gamepad_count": 0
  }
}
```

#### 4.2.2.2 Event Fields (Distinguished by Type)

All events must include `obs_timestamp` (aligned with OBS video frame timestamp) and `type` (event type), specific specifications as follows:

| Event Type   | Core Field Description                                                                 | Example (JSONL Format)                                                                 |
|--------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Mouse Displacement   | - `type`: `"mouse_move"` (fixed)<br>- `data.dx`: X-axis displacement pulse (integer, positive/negative indicating direction)<br>- `data.dy`: Y-axis displacement pulse (integer, positive/negative indicating direction) | ```json<br>{"obs_timestamp": 1727236201000, "type": "mouse_move", "data": {"dx": 15, "dy": -8}}<br>``` |
| Mouse Button   | - `type`: `"mouse_button"` (fixed)<br>- `data.button`: Button type (`left`/`right`/`middle`/`side1`/`side2`)<br>- `data.state`: State (`press`/`release`) | ```json<br>{"obs_timestamp": 1727236202000, "type": "mouse_button", "data": {"button": "left", "state": "press"}}<br>``` |
| Mouse Wheel   | - `type`: `"mouse_wheel"` (fixed)<br>- `data.delta`: Scroll pulse (`+1` forward, `-1` backward) | ```json<br>{"obs_timestamp": 1727236203000, "type": "mouse_wheel", "data": {"delta": 1}}<br>``` |
| Keyboard Event   | - `type`: `"keyboard"` (fixed)<br>- `data.vk_code`: Windows virtual key code (hexadecimal, e.g., `0x41`)<br>- `data.state`: State (`press`/`release`) | ```json<br>{"obs_timestamp": 1727236204000, "type": "keyboard", "data": {"vk_code": 0x41, "state": "press"}}<br>``` |
| Controller Button   | - `type`: `"gamepad_button"` (fixed)<br>- `data.button`: Button name (`a_button`/`b_button`/`x_button`/`y_button` etc.)<br>- `data.raw_code`: Hardware raw key code (integer)<br>- `data.state`: State (`press`/`release`) | ```json<br>{"obs_timestamp": 1727236205000, "type": "gamepad_button", "data": {"button": "a_button", "raw_code": 0, "state": "press"}}<br>``` |
| Controller Stick   | - `type`: `"gamepad_stick"` (fixed)<br>- `data.stick`: Stick type (`left_stick`/`right_stick`)<br>- `data.axis`: Axis direction (`x`/`y`)<br>- `data.value`: Raw value (`-32768`~`32767`)<br>- `data.normalized`: Normalized value (`-1.0`~`1.0`) | ```json<br>{"obs_timestamp": 1727236206000, "type": "gamepad_stick", "data": {"stick": "left_stick", "axis": "x", "value": 15600, "normalized": 0.48}}<br>``` |
| Controller Trigger   | - `type`: `"gamepad_trigger"` (fixed)<br>- `data.trigger`: Trigger type (`left_trigger`/`right_trigger`)<br>- `data.value`: Pressure value (`0`~`1023`) | ```json<br>{"obs_timestamp": 1727236207000, "type": "gamepad_trigger", "data": {"trigger": "right_trigger", "value": 780}}<br>``` |
| Controller D-pad | - `type`: `"gamepad_dpad"` (fixed)<br>- `data.direction`: Direction (`up`/`down`/`left`/`right`/`up_left` etc.)<br>- `data.raw_x`: X-axis raw value (`-1`/`0`/`1`)<br>- `data.raw_y`: Y-axis raw value (`-1`/`0`/`1`) | ```json<br>{"obs_timestamp": 1727236208000, "type": "gamepad_dpad", "data": {"direction": "up", "raw_x": 0, "raw_y": 1}}<br>``` |
| Recording End Marker | - `type`: `"recording_complete"` (fixed)<br>- `data.status`: State (fixed as `"success"`) | ```json<br>{"obs_timestamp": 1727239800000, "type": "recording_complete", "data": {"status": "success"}}<br>``` |

#### 4.2.2.3 End Fields
Metadata is in fixed format, containing basic information for traceability, example: 
```json
{
  "timestamp": 44.235763,
  "absolute_time": 1758526576.1776924,
  "event_type": "SessionEnd",
  "details": 
  {
    "total_events": 3064, 
    "mouse_events": 3008, 
    "keyboard_events": 56, 
    "gamepad_events": 0, 
    "duration_seconds": 44.235761099960655
  }
}
```

#### 4.2.2.4 Constraint Conditions

1. **Timestamp Rules**  
   - All `obs_timestamp` must be **millisecond-level Unix timestamps (integers)**, and must satisfy: `recording_start_obs_ts ≤ obs_timestamp ≤ recording_end_obs_ts` (error allowance ±10ms).

2. **Value Range Constraints**  
   - Controller Stick: `data.value` must be in `[-32768, 32767]` range; `data.normalized` must be in `[-1.0, 1.0]` range, and both satisfy `normalized = value / 32767` (round to 2 decimal places).  
   - Controller Trigger: `data.value` must be in `[0, 1023]` range (`0`=full release, `1023`=full press).  
   - Keyboard Virtual Key Code: `data.vk_code` must comply with Windows standard VK_CODE definition (range `0x00`~`0xFF`).

3. **Field Integrity Requirements**  
   - Each event must include `obs_timestamp` and `type` fields, no omissions.  
   - The `data` subfields of each type of event must fully include all items listed in the table (e.g., “Mouse Button” event must include both `button` and `state`).

4. **Naming Specifications**  
   - Event type `type` must strictly match the strings defined in the table (case-sensitive, e.g., `"mouse_move"` cannot be abbreviated as `"mousemove"`).  
   - Device component names (e.g., `data.button` as `a_button`, `data.stick` as `left_stick`) must be selected from preset enumeration lists, prohibit custom names.

## 5. Data Storage Specifications (AWS S3 Sydney Region)  
### 5.1 Storage Basic Configuration  
- **Storage Region**: Fixed as AWS Sydney Region (AP-Southeast-2, apse2), ensuring data compliance and controllable access latency.  
- **S3 Bucket Configuration**:  
  - Unified use of main bucket: `game-recording-main-apse2` (managed by us, no need for suppliers to create separately);  
  - Security Settings: Enable server-side encryption (SSE-S3), version control (prevent accidental deletion/overwrite), access permission control (only allow web upload side to write, prohibit public access).  

### 5.2 Simplified Directory Structure (Adapted for Web Upload)  
Only retain **“Supplier Code → Game Name”** two core directory levels, no redundant levels, files stored directly, structure as follows:  

    game-recording-main-apse2/  # Main bucket (fixed, cannot be modified)
    ├─ [Supplier Code]/  # First-level directory: Exclusive supplier code allocated by us (format requirement: 3-6 letters + numbers combination, example: SUP001, SUP002, SUP123A)
    │  ├─ [Game Name]/  # Second-level directory: Official standard game name (must be completely consistent with the “Game Name” field in “4. Delivery Standards”, example: “Genshin Impact” “Cyberpunk 2077” “League of Legends”)
    │  │  ├─ 2024-09-25 14-30-00.mp4  # Video file (naming must strictly follow “4.1.2 File Name Specifications”)
    │  │  ├─ 20240925_143000.jsonl  # Keyboard/mouse/controller data file (must match the corresponding video time, suffix changed to .jsonl, one-to-one correspondence)
    │  │  └─ [Optional] SUP001_20240925_config.ini  # Configuration snapshot file (upload as needed, not required; naming format: supplier code_date_config.ini)

- **Constraint Rules**:  
  1. Supplier Code: Allocated and filed in advance by us, cannot be customized (e.g., SUP001 exclusively allocated to Supplier A);  
  2. Game Name: Strictly use official standard name;  
  3. File Storage: Video and JSONL files directly stored in “Supplier Code-Game Name” directory, no need for further “Video/InputData” subfolders, simplifying operations.  

## 6. Data Upload Specifications (Based on R2bucketuploader Desktop Version) (In Progress)

### 6.1 Upload Tool Description (Desktop EXE Application)

#### 6.1.1 Tool Features and Distribution Method
* **Tool Form**: A desktop application (EXE format) packaged based on the core logic of r2-bucket-uploader, supporting Windows/macOS systems, with built-in Uppy upload engine and chunked upload capabilities, without relying on a browser.
* **Distribution and Updates**: Provided by our side as an encrypted compressed package (including checksum), suppliers download via a specified link and can use it immediately after decompression (portable version, no installation required).
* **Core Advantages**:
  * More stable for large file uploads (not limited by browser memory, supports chunked transmission for files over 100GB+);
  * Supports local file drag-and-drop (directly drag from folders into the application window);
  * Automatic retry after network disconnection (no manual intervention required, continues uploading after network recovery).

#### 6.1.2 Preliminary Preparation (Obtaining Upload Code)
Consistent with the web version, obtain the upload code through the Feishu multi-dimensional table:
1. Access our shared Feishu multi-dimensional table (link: [Our Provided Table Address]).
2. Fill in the form fields:
   * Supplier code (e.g., SUP001, must match the value assigned by our side);
   * Game name (dropdown selection, consistent with the "Game Name" in section 5.2 directory; new games can be manually entered);
   * Username (select your own Feishu address book account for tracking upload duration and settlement).
3. After submission, the table automatically generates an 8-16 digit upload code (alphanumeric), displays the validity period (default 72 hours) and status, and copies the code for later use.

### 6.2 Core Operation Process (Desktop Application)

#### 6.2.1 Application Startup and Configuration
1. Decompress the downloaded application package and double-click R2Uploader.exe to start (first startup will generate a local configuration folder for storing logs and cache).
2. Initial use requires completing basic configuration (only once):
   * Language selection (default Chinese);
   * Local cache path setting (recommended to select a non-system drive for temporary storage of chunked files, space required ≥ planned maximum upload file size).

#### 6.2.2 Upload Operation Steps
1. Input verification information: In the "Upload Configuration" area of the application main interface, fill in:
   * Supplier code (e.g., SUP001);
   * Game name (dropdown selection, must match the entry in the Feishu table);
   * Upload code (paste the code obtained from the Feishu table); Click "Verify Code", the application will validate the code's validity via built-in API (not expired, unused, matches supplier/game name), unlocking the file selection area upon success.
2. File Selection and Validation:
   * **Method 1**: Click the "Add Files" button to batch select corresponding batch .mp4 videos and .jsonl data files;
   * **Method 2**: Directly drag files from local folders to the application's "File List Area";
   * The application will automatically validate file name formats (files not compliant with 4.1.2/4.2.1 specifications will be marked red, with error reasons shown on hover, prohibiting upload).
3. Start Upload and Monitoring:
   * Click "Start Upload", the application automatically executes:
     * Chunking large files (files ≥100MB are automatically split into 50MB chunks for enhanced stability);
     * Generating R2 storage path: game-recording-main-apse2/[Supplier Code]/[Game Name]/[File Name];
     * Real-time display of overall progress (percentage), current uploading file, chunk progress, and remaining time;
   * During upload, the application can be minimized (continues transmission in the background), but cannot be closed (closing interrupts the upload; next startup requires re-verifying the code to resume).
4. Completion and Confirmation:
   * After all files are successfully uploaded and validated, the application displays an "Upload Complete" popup, including the number of files uploaded this time, total size, and duration;
   * Click "View Report" to generate a local validation report (txt format, containing file names, MD5 comparison results, upload code), recommended to save for records;
   * The corresponding upload code status in the Feishu table will automatically update to "Used", and sync the upload results.

### 6.3 Resumable Upload and Exception Handling

#### 6.3.1 Resumable Upload Mechanism
* Supports resumption in two scenarios:
  1. **Network Interruption**: The application automatically detects network status and resumes from the interrupted chunk without intervention after recovery;
  2. **Application Closure**: Restart the application, input the same supplier code + game name + upload code, the application reads the local cache's "Incomplete File Records" to automatically identify and continue uploading the required files.

#### 6.3.2 Exception Handling
* **File Validation Failure**: The application marks the failed file and displays a "Retry" button; clicking retries only that file (no need to re-upload all);
* **Upload Code Expiration**: If the code expires during upload (e.g., exceeding 24 hours), the application prompts "Code Expired", requiring a new code from the Feishu table; inputting it allows continuation (already uploaded chunks do not need retransmission);
* **Insufficient Disk Space**: When cache path space is insufficient, the application prompts "Clear Cache" or "Change Cache Path"; clearing does not affect uploaded chunks (already stored in the cloud).

### 6.4 Logs and Data Integration

#### 6.4.1 Local Logs and Cloud Synchronization
* **Local Logs**: The application automatically generates log files in the configuration folder (path: [Cache Path]/logs/[YYYYMMDD].log), recording:
  * Operation time, upload code, supplier code, game name;
  * Upload progress for each file, chunk success/failure records, MD5 values, duration;
* **Cloud Logs**: After upload completion, the application synchronizes core logs (via encrypted interface) to the R2 log directory: game-recording-main-apse2/UploadLogs/[Supplier Code]/[YYYYMMDD].log, consistent with web version log format.

#### 6.4.2 Integration with Feishu Table
* The desktop application integrates with the Feishu table via built-in API to achieve:
  * **Pre-Upload**: Pulls table data for comparison during code verification;
  * **During Upload**: Syncs "Current Upload Progress" to the table every 90 seconds (optional);
  * **Post-Upload**: Updates table status to "Used", supplementing "Total File Size, Validation Report Local Path, Upload Completion Time";
* For settlement, the table can directly aggregate upload data by "Username" (no reliance on application local files).

### 6.5 Security and Constraints
1. **Application Security**:
   * The EXE package provided by our side includes a SHA256 checksum; suppliers must verify the checksum before use (to prevent tampering);
   * The application communicates only via HTTPS with the backend; all sensitive information (e.g., upload code) is encrypted during transmission;
2. **Usage Constraints**:
   * Prohibited from modifying any files in the application directory (e.g., config.json, core.dll), otherwise leading to upload failure or marking as "Abnormal Operation";
   * The same upload code supports use on only one device (to prevent conflicts from multi-device simultaneous uploads);
   * For multi-device uploads, generate separate upload codes for each device (via multiple submissions in the Feishu table).

## 7. Verification and Acceptance Standards

### Core Principles
Acceptance must cover “Data Compliance, Integrity, Synchronization”, first completed by the supplier through self-inspection, then submitted to us for final acceptance. Data delivery is confirmed complete only after acceptance is passed.

### 7.1 Video Acceptance Indicators

#### 7.1.1 Quality and Audio Requirements (Quantitative Standards)

| Acceptance Dimension | Qualified Standards | Verification Tools/Methods |
|----------|----------|---------------|
| Frame Drop Situation | Single segment video frame drop rate ≤ 0.1% (i.e., 1-hour video frame drops ≤3.6 frames), no continuous frame drops (continuous frame drops ≤1 frame) | 1. Open video with **PotPlayer**, enable “Frame Counter” (shortcut Ctrl+J), check frame sequence continuity segment by segment; <br>2. Use **FFmpeg** command: `ffmpeg -i video_file.mp4 -vf "showinfo" -f null - 2> frame_info.log`, analyze “frame=xxx” continuity in log |
| Screen Clarity | 1. Game UI text (e.g., health, skill icons) no blur, no aliasing after 200% zoom; <br>2. Fast-moving scenes (e.g., character running, camera turning) no smearing, no mosaics | 1. Pause key frames (e.g., UI interface, fast-moving scenes) with video player, zoom to check details; <br>2. Compare original game resolution (e.g., 1080P) with video resolution, confirm no stretching/compression (use FFmpeg: `ffmpeg -i video_file.mp4`, check “Stream #0:0” resolution) |
| Audio Quality | 1. No noise, no popping, no breaks; <br>2. Game background sound, operation sound effects (e.g., key press, footsteps) uniform volume (-12dB~-6dB, no sudden changes); <br>3. Audio synchronized with screen (mouth/actions and sound effects delay ≤100ms) | 1. Open video audio track with **Audacity**, check waveform for no abnormal spikes (popping), no breaks (breaks); <br>2. When playing with player, focus on “operation trigger sound effects” (e.g., controller A key sound) alignment with screen actions |

#### 7.1.2 Format Compliance Validation
Must fully comply with 4.1 “Video Delivery Standards”, validation items as follows:

| Validation Item | Qualified Standards                                                                                                    | Verification Tools/Methods |
|--------|------------------------------------------------------------------------------------------------------------------------|---------------|
| Encoding Format | Video Encoding: H.264 (High Profile); Audio Encoding: AAC (LC Profile)                                                 | Use FFmpeg: `ffmpeg -i video_file.mp4`, check “Codec” fields (e.g., “Video: h264” “Audio: aac”) |
| Naming Specifications | Strictly conform to format: `[YYYY-MM-DD] [HH-MM-SS].mp4`, no typos, no special characters                             | Manually verify file names against 4.1.2 naming rules, focus on checking if “Game Name” matches S3 directory “Game Name” and if date/time is accurate |
| MD5 Consistency | Video file’s local MD5 and S3 cloud MD5 must be identical (refer to 6.2.1 validation report)                           | On the upload web end, check “View Validation Report” to confirm “Validation Status” is “Success”; or compare file “Metadata” MD5 value in S3 console with local |

### 7.2 Keyboard/Mouse/Controller Operation Data Acceptance Indicators

#### 7.2.1 Integrity Requirements (JSONL File)
Must fully cover 4.2 “Operation Data Delivery Standards”, no field omissions, no event missing:

| Acceptance Dimension | Qualified Standards | Verification Tools/Methods |
|----------|----------|---------------|
| Metadata Integrity | First line metadata includes all required fields (e.g., `meta_version`, `recording_start_obs_ts`, `mouse_info`, `output_video_file`), no null values, no field omissions | 1. Open JSONL file with Notepad/VS Code, check first line; <br>2. Use **jsonlint** tool to validate first line JSON format (command: `jsonlint -c first_line_content`), confirm no format errors |
| Event Integrity | 1. Includes all required event types (mouse displacement/button/wheel, keyboard, controller button/stick/trigger/D-pad), no complete absence of any event type; <br>2. Recording end marker exists (file ends with `"type": "recording_complete"` event) | 1. Use VS Code to search file content, confirm presence of all event `type` fields (e.g., search “mouse_move”, “keyboard”, “gamepad_stick”); <br>2. Locate file end, confirm presence of “recording_complete” event |
| Field Integrity | Each event’s `data` subfield has no omissions (e.g., mouse button event must include `button` and `state`, controller stick event must include `stick`/`axis`/`value`/`normalized`) | Randomly select 10 different types of events, use jsonlint to validate single-line JSON format, confirm no field omissions (e.g., check if a “gamepad_trigger” event includes `trigger` and `value`) |

#### 7.2.2 Synchronization Requirements (Timestamp Alignment)
Ensure operation data and video frames are precisely synchronized, no time deviation:

| Acceptance Dimension | Qualified Standards | Verification Tools/Methods |
|----------|----------|---------------|
| Timestamp Validity | 1. All event `obs_timestamp` within metadata `recording_start_obs_ts` and `recording_end_obs_ts` range (error ≤10ms); <br>2. Timestamps are integers (millisecond-level), no decimals, no negatives | 1. Use VS Code to extract “recording start/end time” from metadata, randomly select 20 event `obs_timestamp`, confirm within range; <br>2. Check `obs_timestamp` field values, confirm no non-integers (e.g., 1727236201000.5), no negatives |
| Video-Data Synchronization | Operation event and video frame time deviation ≤ 1ms (i.e., event `obs_timestamp` and corresponding video frame timestamp difference ≤1ms) | 1. Select one clear operation event (e.g., “press controller A key”, find the event’s `obs_timestamp` in JSONL, record as T1); <br>2. Open corresponding video with **PotPlayer**, locate video frame by T1 time (e.g., T1=1727236205000, corresponds to video time 00:00:05), confirm frame screen aligns perfectly with “press A key” action (e.g., character jump action synchronized with A key event) |

#### 7.2.3 Data Accuracy Requirements
Ensure collected values comply with specifications, no abnormal values:

| Acceptance Dimension | Qualified Standards | Verification Tools/Methods |
|----------|----------|---------------|
| Value Range Compliance | 1. Controller Stick: `data.value`: -32768~32767; `data.normalized`: -1.0~1.0; <br>2. Controller Trigger: `data.value`: 0~1023; <br>3. Keyboard VK_CODE: 0x00~0xFF | Randomly select 10 controller stick/trigger events, 10 keyboard events, check if corresponding values are within compliant ranges (use Excel to import JSONL data, filter value columns to check) |
| Naming Specification | Event `type` fields (e.g., “mouse_move”, “gamepad_button”) and device component names (e.g., `data.button` as “a_button”) strictly comply with 4.2.2.2 preset list, no custom names | Search JSONL file for `type` fields and `data.button`/`data.stick` fields, confirm no spelling errors (e.g., “mousemove”, “A_button”) |

### 7.3 Acceptance Result Determination
- **Pass**: All acceptance indicators meet qualified standards, no items fail;  
- **Pending Correction**: 1-2 non-critical failures (e.g., single event field omission, individual frame blur), supplier must correct and resubmit within 24 hours;  
- **Fail**: Critical failures exist (e.g., MD5 validation failure, significant frame drops, timestamp deviation >1ms), supplier must re-collect data and resubmit for acceptance.

## 8. Exception Handling Specifications  

### 8.1 Exception Levels  
Exceptions are classified into three levels based on their impact on data quality, integrity, and business processes, with specific standards as follows:  

| Exception Level | Definition Standard | Typical Scenarios |  
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|  
| Minor Exception | Does not affect core data validity, can be automatically recovered without human intervention, no significant impact on final analysis results; no need to re-verify entire data after fixing | 1. Single non-critical event field missing (e.g., occasional missing `raw_x` field for controller D-pad) <br>2. Transient network fluctuation causing 1-2 frames of slight blur (no continuous blur) <br>3. Single JSONL event timestamp deviation of 3-5ms (within ≤10ms synchronization threshold) |  
| Moderate Exception | Partial data damage but main body intact, requires human intervention to fix (no need for re-collection), slight impact on analysis accuracy; verify affected data after fixing | 1. Video frame drop rate 0.1%~0.5% (1-hour video drops 3.6~18 frames, no continuous drops exceeding 3 frames) <br>2. Up to 5 consecutive missing events of the same type (e.g., brief keyboard event interruption) <br>3. MD5 validation fails once but succeeds after one retry <br>4. Individual non-critical metadata fields missing in JSONL (e.g., `detected_dpi` in `mouse_info`) |  
| Severe Exception | Data integrity or usability compromised, unrecoverable by fixing, requires re-collection; or exception renders data unusable for analysis, necessitating termination of current collection process | 1. Recording interruption exceeding 30 seconds (e.g., OBS crash, device disconnection), causing video file corruption and unplayability <br>2. JSONL file missing over 20% (e.g., significant absence of critical controller stick events) or core metadata missing (e.g., `recording_start_obs_ts`) <br>3. Timestamp deviation >10ms persisting (over 10 consecutive events) <br>4. Upload failure ≥3 times with unidentified cause (e.g., S3 permission issues, web end failure) |  

### 8.2 Handling Procedures  

#### 8.2.1 Recording Interruption Handling Measures  
1. **Automatic Recovery Mechanism**:  
   - Recording tools (OBS + self-developed program) monitor recording status in real-time; upon detecting interruption (e.g., OBS disconnection, controller disconnection), immediately trigger automatic retry, retry interval 10 seconds, maximum 3 retries;  
   - If retry succeeds, automatically generate new segment file with incremented file name sequence (e.g., original file `Genshin_20240925_143000_01.mp4`, new file after interruption `Genshin_20240925_143000_02.mp4`), avoiding overwriting existing valid files;  
   - Automatically log interruption details (including interruption time, error code like `ERR_OBS_DISCONNECT`, retry result) to local `Log` directory.  

2. **Human Intervention Process**:  
   - If automatic retry fails, recording tool displays alert window showing interruption reason and troubleshooting suggestions (e.g., “Check OBS WebSocket connection”, “Replug controller”);  
   - Supplier must complete cause investigation within 1 hour (prioritize checking network, device drivers, OBS configuration), fix and re-record missing period;  
   - Re-recorded files must append `_retry` to file name (e.g., `Genshin_20240925_143000_03_retry.mp4`) and note “re-recorded file” during upload;  
   - Original interrupted corrupted files (e.g., unplayable `01.mp4`) must be stored separately in S3 directory `[Supplier Code]/[Game Name]/broken/` with `_broken` suffix, noting interruption reason (e.g., `Genshin_20240925_143000_01_broken.mp4`, remark “OBS crash caused interruption”).  

#### 8.2.2 Data Missing Handling Measures  
1. **Missing Detection**:  
   - Upload web end automatically validates matching degree of “video duration” and “JSONL event time span”, allowing error ≤5 seconds; if difference exceeds limit (e.g., 10-minute video, JSONL only records 8 minutes), immediately mark as “suspected missing” and prompt;  
   - Perform Schema validation on JSONL files (preset field rules); if required fields are missing (e.g., `obs_timestamp`, `type`), generate “Missing Report” specifying missing field names, line numbers, and missing quantity.  

2. **Repair Strategy**:  
   - Minor Missing (single/dispersed missing): Use “interpolation completion”, e.g., for missing controller stick data, fill with average of 3 preceding and following valid records; for missing keyboard events, if no logical conflict with preceding/following events, mark as “occasional missing” without need for completion;  
   - Moderate Missing (≤10% and concentrated in a section): Manually annotate missing time period (e.g., `1727236200000~1727236210000`), complete based on logic of adjacent valid data (e.g., character movement direction), document repair method in configuration file (e.g., `20240925_config.ini` notes “10:00-10:10 stick data interpolated”);  
   - Severe Missing (>10% or critical events missing): Trigger “re-collection” process, mark original missing file as `_invalid` and archive (e.g., `Genshin_20240925_143000_01_invalid.jsonl`), prohibit use for analysis.  

#### 8.2.3 Alert Mechanism Trigger Conditions  
| Exception Level | Trigger Threshold | Notification Method | Response Time Limit | Handling Requirements |  
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------------------|  
| Minor Exception | ≥5 same-type minor exceptions accumulated within 1 hour (e.g., repeated “single controller event missing”) | System log automatically recorded (local + S3 log directory), no real-time notification | - | Daily log summary, investigate potential issues (e.g., device connection issues) |  
| Moderate Exception | 1. ≥2 types of moderate exceptions in a single batch (e.g., simultaneous “video frame drop” + “JSONL metadata missing”) <br>2. Same moderate exception in 2 consecutive batches (e.g., “MD5 initial validation failure” in two batches) | 1. Upload web end pop-up notification <br>2. Email notification to supplier administrator (including exception report) | 24 hours | Supplier must fix exception within time limit, resubmit for acceptance; failure to handle within time upgrades to severe exception |  
| Severe Exception | 1. Any single severe exception detected (e.g., “recording interruption 30 seconds”, “JSONL missing 20%”) <br>2. Moderate exception not handled within 24 hours <br>3. Upload failure ≥3 times with unidentified cause | 1. Web end pop-up + email + SMS notification to supplier administrator <br>2. System ticket synchronized to our contact person | 2 hours | Supplier must immediately stop current collection, collaborate with our contact to investigate; submit “Exception Handling Report” after resolution, restart collection only after our confirmation |  

## 9. Terminology Definitions  

| Term | Definition | Technical Description                                                                                                                                                                                                                                                                                                                          |  
|------|--------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|  
| JSONL | JSON Lines, a lightweight structured data format where each line is an independent JSON object, no nested arrays | 1. Advantage: Supports streaming read/write (can process single events without loading entire file), suitable for large-scale event log storage; <br>2. Usage in this specification: Store keyboard/mouse/controller operation data, each line corresponds to one operation event (e.g., mouse movement, controller button), encoded in UTF-8. |  
| OBS WebSocket | Official remote control interface of OBS Studio, based on WebSocket protocol for bidirectional communication between “client (self-developed program) - OBS server” | 1. Core Functions: Transmit OBS recording status (start/stop), obtain video frame timestamps, synchronize recording parameters; <br>2. Configuration in this specification: Default port 4455, enable password authentication, ensure status synchronization delay between self-developed program and OBS ≤1ms.                                |  
| Normalized Value | Standardized result of scaling raw data to a uniform numerical range to eliminate hardware differences across devices | 1. Calculation Logic: In this specification, controller stick raw value range is -32768~32767, normalized value calculated via formula `normalized = value / 32767`, mapped to [-1.0, 1.0] range; <br>2. Purpose: Facilitate cross-device comparison (e.g., uniform sensitivity for Xbox and PS controllers).                                  |  
| S3 Object Key | Unique string identifying an “object (file)” in Amazon S3 bucket, essentially “file path + file name”, simulating directory structure (S3 is actually flat storage) | 1. Format Requirements: UTF-8 encoding, maximum length 1024 bytes, prohibit characters like `\`, `*`, `?`; <br>2. Format in this specification: `[Supplier Code]/[Game Name]/File Name` (e.g., `SUP001/Genshin Impact/Genshin_20240925_143000_01.mp4`).                                                                                        |  
| MD5 Validation | Calculates 128-bit hash value of a file using MD5 hash algorithm, verifies data integrity by comparing “local file MD5” with “cloud file MD5” | 1. Validation Process: Web end automatically calculates local file MD5 before upload, S3 recalculates cloud file MD5 after upload, consistency indicates “no transmission damage”; <br>2. Purpose: Prevent data tampering or loss due to network fluctuations during transmission.                                                             |  
| Frame Drop Rate | Proportion of “dropped frames” to “total frames” in video recording, reflecting screen completeness | 1. Calculation Formula: `Frame Drop Rate = (Total Frames - Valid Frames) / Total Frames × 100%`; <br>2. Standard in this specification: Acceptable frame drop rate ≤0.1% (i.e., 1-hour 60fps video, dropped frames ≤3.6), no continuous frame drops exceeding 3 frames.                                                                        |  
| Timestamp Synchronization | Ensures “keyboard/mouse/controller operation events” align with “corresponding video frames” timestamps to avoid operation-screen misalignment | 1. Synchronization Logic: Self-developed program obtains video frame `obs_timestamp` via OBS WebSocket, operation event `obs_timestamp` bound to this value; <br>2. Standard in this specification: Operation event and video frame timestamp deviation ≤1ms, exceeding affects “operation-screen” correlation analysis.                       |  
| Schema Validation | Automated checking mechanism to verify JSONL file structure against preset field rules | 1. Validation Content: Field integrity (presence of required fields), data type (e.g., `obs_timestamp` as integer), value range (e.g., controller trigger value 0~1023); <br>2. Tool: This specification recommends using `json-schema-validator`, generates detailed error report upon validation failure.                                    |  
| Supplier Code | Unique identifier allocated by us for each supplier, used for S3 directory differentiation, permission control, and data traceability | 1. Format: 3-6 letters + numbers combination (e.g., SUP001, SUP002), pre-filed and allocated by us, supplier cannot customize; <br>2. Purpose: First-level S3 directory, upload authentication, log traceability (distinguish data from different suppliers).                                                                                  |
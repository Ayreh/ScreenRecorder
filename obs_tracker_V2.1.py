"""
OBS Companion TRACKER - Improved UI Version
Based on working gamepad test with better styling
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import configparser
import os

# Import libraries
try:
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import obsws_python as obs
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class WorkingGamepadTracker:
    """基于成功测试程序的手柄追踪器"""
    
    def __init__(self, parent_tracker):
        self.parent = parent_tracker
        self.tracking = False
        self.gamepad_thread = None
        self.joystick = None
        
        # 按钮映射
        self.button_names = {
            0: 'a_button', 1: 'b_button', 2: 'x_button', 3: 'y_button',
            4: 'lb_shoulder', 5: 'rb_shoulder', 6: 'back_button', 7: 'start_button',
            8: 'left_stick_press', 9: 'right_stick_press'
        }
        
        # 轴名称
        self.axis_names = ["left_stick_x", "left_stick_y", "right_stick_x", "right_stick_y", "left_trigger", "right_trigger"]
        
        # 简单初始化
        if PYGAME_AVAILABLE:
            try:
                pygame.init()
                pygame.joystick.init()
                self.pygame_ready = True
                print("Gamepad system initialized successfully")
            except Exception as e:
                self.pygame_ready = False
                print(f"Gamepad init failed: {e}")
        else:
            self.pygame_ready = False
    
    def get_gamepad_count(self):
        """获取手柄数量"""
        if not self.pygame_ready:
            return 0
        try:
            return pygame.joystick.get_count()
        except:
            return 0
    
    def connect_gamepad(self):
        """连接手柄"""
        if not self.pygame_ready:
            return False
        
        try:
            count = pygame.joystick.get_count()
            if count == 0:
                print("No gamepads detected")
                return False
            
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            
            name = self.joystick.get_name()
            print(f"Connected gamepad: {name}")
            return True
            
        except Exception as e:
            print(f"Failed to connect gamepad: {e}")
            return False
    
    def log_gamepad_event(self, event_type, data):
        """记录手柄事件"""
        if self.parent and self.parent.recording:
            self.parent.log_event(f"gamepad_{event_type}", data)
    
    def gamepad_loop(self):
        """手柄监控循环"""
        print("Starting gamepad monitoring loop (using working test method)")
        
        while self.tracking and self.joystick:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break
                    elif event.type == pygame.JOYBUTTONDOWN:
                        button_name = self.button_names.get(event.button, f"button_{event.button}")
                        self.log_gamepad_event("button", {
                            "button": button_name,
                            "raw_code": event.button,
                            "state": "press"
                        })
                        print(f"Button press: {button_name} ({event.button})")
                        
                    elif event.type == pygame.JOYBUTTONUP:
                        button_name = self.button_names.get(event.button, f"button_{event.button}")
                        self.log_gamepad_event("button", {
                            "button": button_name,
                            "raw_code": event.button,
                            "state": "release"
                        })
                        
                    elif event.type == pygame.JOYAXISMOTION:
                        if abs(event.value) > 0.1:
                            if event.axis < 4:  # 摇杆
                                raw_value = int(event.value * 32767)
                                self.log_gamepad_event("stick", {
                                    "stick": "left_stick" if event.axis < 2 else "right_stick",
                                    "axis": "x" if event.axis % 2 == 0 else "y",
                                    "value": raw_value,
                                    "normalized": event.value
                                })
                            else:  # 扳机
                                trigger_value = max(0, int((event.value + 1.0) / 2.0 * 1023))
                                trigger_name = "left_trigger" if event.axis == 4 else "right_trigger"
                                self.log_gamepad_event("trigger", {
                                    "trigger": trigger_name,
                                    "value": trigger_value
                                })
                        
                    elif event.type == pygame.JOYHATMOTION:
                        directions = []
                        x, y = event.value
                        if y == 1: directions.append("up")
                        elif y == -1: directions.append("down")
                        if x == 1: directions.append("right")
                        elif x == -1: directions.append("left")
                        direction = "_".join(directions) if directions else "neutral"
                        
                        self.log_gamepad_event("dpad", {
                            "dpad": f"dpad_{event.hat}",
                            "direction": direction,
                            "raw_x": x,
                            "raw_y": y
                        })
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Gamepad loop error: {e}")
                time.sleep(0.1)
        
        print("Gamepad monitoring loop ended")
    
    def start_tracking(self):
        """开始追踪"""
        if not self.pygame_ready:
            return False
        
        if not self.connect_gamepad():
            return False
        
        self.tracking = True
        self.gamepad_thread = threading.Thread(target=self.gamepad_loop, daemon=True)
        self.gamepad_thread.start()
        
        print("Gamepad tracking started successfully")
        return True
    
    def stop_tracking(self):
        """停止追踪"""
        if not self.tracking:
            return
        
        self.tracking = False
        
        if self.gamepad_thread and self.gamepad_thread.is_alive():
            self.gamepad_thread.join(timeout=2)
        
        if self.joystick:
            try:
                self.joystick.quit()
            except:
                pass
            self.joystick = None

class OBSCompanionTracker:
    def __init__(self):
        self.recording = False
        self.start_time = None
        self.log_file = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_mouse_pos = None
        self.current_log_path = None
        
        # OBS connection
        self.obs_client = None
        self.obs_connected = False
        self.obs_monitor_thread = None
        self.should_monitor = True
        
        # Gamepad tracker
        self.gamepad_tracker = WorkingGamepadTracker(self)
        self.gamepad_enabled = True
        
        # Settings
        self.load_settings()
        
        # Event counters
        self.event_count = 0
        self.mouse_count = 0
        self.keyboard_count = 0
        self.gamepad_count = 0
        
    def load_settings(self):
        """Load settings"""
        self.config = configparser.ConfigParser()
        self.config_file = Path.home() / "AppData" / "Local" / "OBSTracker" / "config.ini"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self.config['OBS'] = {
                'host': 'localhost',
                'port': '4455',
                'password': ''
            }
            self.config['Recording'] = {
                'save_directory': str(Path.home() / "Videos" / "OBSInputLogs"),
                'include_mouse_position': 'True'
            }
            self.config['Gamepad'] = {
                'enabled': 'True'
            }
            self.save_settings()
        
        self.gamepad_enabled = self.config.getboolean('Gamepad', 'enabled', fallback=True)
        self.save_dir = Path(self.config.get('Recording', 'save_directory'))
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_settings(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def connect_obs(self):
        try:
            host = self.config.get('OBS', 'host', fallback='localhost')
            port = int(self.config.get('OBS', 'port', fallback='4455'))
            password = self.config.get('OBS', 'password', fallback='')
            
            self.obs_client = obs.ReqClient(
                host=host,
                port=port,
                password=password if password else None
            )
            
            version_info = self.obs_client.get_version()
            self.obs_connected = True
            print(f"Connected to OBS: {version_info.obs_version}")
            
            self.start_obs_monitoring()
            return True
            
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")
            self.obs_connected = False
            return False
    
    def disconnect_obs(self):
        self.should_monitor = False
        
        if self.obs_monitor_thread and self.obs_monitor_thread.is_alive():
            self.obs_monitor_thread.join(timeout=2)
        
        if self.obs_client:
            try:
                self.obs_client.disconnect()
            except:
                pass
            self.obs_client = None
        
        self.obs_connected = False
    
    def start_obs_monitoring(self):
        if self.obs_monitor_thread and self.obs_monitor_thread.is_alive():
            return
        
        self.should_monitor = True
        self.obs_monitor_thread = threading.Thread(target=self._obs_monitor_loop, daemon=True)
        self.obs_monitor_thread.start()
    
    def _obs_monitor_loop(self):
        last_recording_state = False
        
        while self.should_monitor and self.obs_connected:
            try:
                if self.obs_client:
                    status = self.obs_client.get_record_status()
                    is_recording = status.output_active
                    
                    if is_recording != last_recording_state:
                        if is_recording:
                            print("OBS recording started - Starting input tracking")
                            self.start_recording_sync()
                        else:
                            print("OBS recording stopped - Stopping input tracking")
                            self.stop_recording()
                        
                        last_recording_state = is_recording
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error monitoring OBS: {e}")
                time.sleep(2)
    
    def log_event(self, event_type, details):
        if self.log_file and self.start_time:
            elapsed = time.perf_counter() - self.start_time
            log_entry = {
                "timestamp": round(elapsed, 6),
                "absolute_time": time.time(),
                "event_type": event_type,
                "details": details
            }
            self.log_file.write(json.dumps(log_entry) + "\n")
            self.log_file.flush()
            
            self.event_count += 1
            if event_type.startswith("Mouse"):
                self.mouse_count += 1
            elif event_type.startswith("Key"):
                self.keyboard_count += 1
            elif event_type.startswith("gamepad"):
                self.gamepad_count += 1
    
    def on_mouse_move(self, x, y):
        if not self.recording:
            return
            
        if self.last_mouse_pos is not None:
            delta_x = x - self.last_mouse_pos[0]
            delta_y = y - self.last_mouse_pos[1]
            
            if abs(delta_x) > 0 or abs(delta_y) > 0:
                details = {"dx": delta_x, "dy": delta_y}
                
                if self.config.getboolean('Recording', 'include_mouse_position', fallback=True):
                    details.update({"x": x, "y": y})
                
                self.log_event("MouseDelta", details)
        
        self.last_mouse_pos = (x, y)
    
    def on_mouse_click(self, x, y, button, pressed):
        if not self.recording:
            return
            
        self.log_event("MouseClick", {
            "button": str(button).replace('Button.', ''),
            "action": "pressed" if pressed else "released",
            "x": x,
            "y": y
        })
    
    def on_key_press(self, key):
        if not self.recording:
            return
            
        try:
            if hasattr(key, 'char') and key.char:
                key_str = key.char
            else:
                key_str = str(key).replace('Key.', '')
            
            self.log_event("KeyDown", {"key": key_str})
            
        except AttributeError:
            self.log_event("KeyDown", {"key": str(key)})
    
    def on_key_release(self, key):
        if not self.recording:
            return
            
        try:
            if hasattr(key, 'char') and key.char:
                key_str = key.char
            else:
                key_str = str(key).replace('Key.', '')
            
            self.log_event("KeyUp", {"key": key_str})
            
        except AttributeError:
            self.log_event("KeyUp", {"key": str(key)})
    
    def start_recording_sync(self):
        if self.recording:
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"input_log_{timestamp}.jsonl"
            
            self.current_log_path = self.save_dir / log_filename
            self.log_file = open(self.current_log_path, "w", encoding="utf-8")
            
            self.start_time = time.perf_counter()
            start_absolute_time = time.time()
            
            session_info = {
                "obs_sync": True,
                "start_time_unix": start_absolute_time,
                "start_time_readable": datetime.fromtimestamp(start_absolute_time).isoformat(),
                "obs_connected": self.obs_connected,
                "pynput_available": PYNPUT_AVAILABLE,
                "gamepad_enabled": self.gamepad_enabled,
                "pygame_available": PYGAME_AVAILABLE
            }
            
            if self.gamepad_enabled and PYGAME_AVAILABLE:
                gamepad_count = self.gamepad_tracker.get_gamepad_count()
                session_info["gamepad_count"] = gamepad_count
            
            self.log_event("SessionStart", session_info)
            
            self.last_mouse_pos = None
            self.event_count = 0
            self.mouse_count = 0
            self.keyboard_count = 0
            self.gamepad_count = 0
            
            if PYNPUT_AVAILABLE:
                self.mouse_listener = mouse.Listener(
                    on_move=self.on_mouse_move,
                    on_click=self.on_mouse_click
                )
                
                self.keyboard_listener = keyboard.Listener(
                    on_press=self.on_key_press,
                    on_release=self.on_key_release
                )
                
                self.mouse_listener.start()
                self.keyboard_listener.start()
            
            if self.gamepad_enabled:
                self.gamepad_tracker.start_tracking()
            
            self.recording = True
            print(f"Input tracking started: {self.current_log_path}")
            return True
            
        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        if not self.recording:
            return
            
        self.recording = False
        
        try:
            if self.log_file:
                self.log_event("SessionEnd", {
                    "total_events": self.event_count,
                    "mouse_events": self.mouse_count,
                    "keyboard_events": self.keyboard_count,
                    "gamepad_events": self.gamepad_count,
                    "duration_seconds": time.perf_counter() - self.start_time if self.start_time else 0
                })
            
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            
            if self.gamepad_tracker:
                self.gamepad_tracker.stop_tracking()
            
            if self.log_file:
                self.log_file.close()
                self.log_file = None
            
            print(f"Input tracking stopped. Log saved: {self.current_log_path}")
            
        except Exception as e:
            print(f"Error stopping recording: {e}")

class ImprovedOBSTrackerGUI:
    def __init__(self):
        self.tracker = OBSCompanionTracker()
        self.root = tk.Tk()
        self.setup_gui()
        self.start_connection_check()
        
    def setup_gui(self):
        """Setup improved GUI with scrolling and better styling"""
        self.root.title("OBS TRACKER - Working Gamepad Version")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Colors
        bg_color = "#1a1a1a"
        accent_color = "#00d4ff"  # 更亮的蓝色
        text_color = "#ffffff"
        frame_bg = "#2a2a2a"     # 框架背景
        
        self.root.configure(bg=bg_color)
        
        # Create main canvas for scrolling
        main_frame = tk.Frame(self.root, bg=bg_color)
        main_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_frame, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.root.bind("<MouseWheel>", _on_mousewheel)
        
        # TRACKER ASCII Banner
        banner_frame = tk.Frame(scrollable_frame, bg=bg_color)
        banner_frame.pack(fill="x", pady=(0, 20))
        
        banner_text = """
 ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
 ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
    ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
    ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
    ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

                   OBS Companion - Gaming Input Tracker
              Perfect Sync with OBS Recording + Working Gamepad
        """
        
        banner_label = tk.Label(banner_frame, 
                               text=banner_text,
                               bg=bg_color,
                               fg=accent_color,
                               font=('Consolas', 8, 'bold'),
                               justify='center')
        banner_label.pack()
        
        subtitle_label = tk.Label(banner_frame,
                                 text="Based on Working Gamepad Test - Stable Connection",
                                 bg=bg_color,
                                 fg=accent_color,
                                 font=('Arial', 12, 'bold'))
        subtitle_label.pack(pady=(5, 0))
        
        # Connection Section
        self.create_connection_section(scrollable_frame, bg_color, frame_bg, text_color, accent_color)
        
        # Recording Section
        self.create_recording_section(scrollable_frame, bg_color, frame_bg, text_color, accent_color)
        
        # Settings Section
        self.create_settings_section(scrollable_frame, bg_color, frame_bg, text_color, accent_color)
        
        # Controls Section
        self.create_controls_section(scrollable_frame, bg_color, frame_bg, text_color, accent_color)
        
        canvas.focus_set()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_connection_section(self, parent, bg_color, frame_bg, text_color, accent_color):
        """Create OBS connection section"""
        frame = tk.LabelFrame(parent, text="OBS Connection", 
                             bg=frame_bg, fg=accent_color, 
                             font=('Arial', 10, 'bold'))
        frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Status
        status_frame = tk.Frame(frame, bg=frame_bg)
        status_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.obs_status_label = tk.Label(status_frame, 
                                        text="Disconnected", 
                                        bg=frame_bg, fg="red",
                                        font=('Arial', 11))
        self.obs_status_label.pack(side="left")
        
        self.connect_button = tk.Button(status_frame, text="Connect to OBS", 
                                       command=self.toggle_obs_connection,
                                       bg="#4CAF50", fg="white",
                                       font=('Arial', 10), relief="flat",
                                       padx=20, pady=5)
        self.connect_button.pack(side="right")
        
        # Settings
        settings_frame = tk.Frame(frame, bg=frame_bg)
        settings_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Host
        host_frame = tk.Frame(settings_frame, bg=frame_bg)
        host_frame.pack(side="left", padx=(0, 15))
        tk.Label(host_frame, text="Host:", bg=frame_bg, fg=text_color).pack(side="left")
        self.host_var = tk.StringVar(value=self.tracker.config.get('OBS', 'host'))
        tk.Entry(host_frame, textvariable=self.host_var, width=12, bg="#333", fg="white").pack(side="left", padx=(5, 0))
        
        # Port
        port_frame = tk.Frame(settings_frame, bg=frame_bg)
        port_frame.pack(side="left", padx=(0, 15))
        tk.Label(port_frame, text="Port:", bg=frame_bg, fg=text_color).pack(side="left")
        self.port_var = tk.StringVar(value=self.tracker.config.get('OBS', 'port'))
        tk.Entry(port_frame, textvariable=self.port_var, width=8, bg="#333", fg="white").pack(side="left", padx=(5, 0))
        
        # Password
        pass_frame = tk.Frame(settings_frame, bg=frame_bg)
        pass_frame.pack(side="left")
        tk.Label(pass_frame, text="Password:", bg=frame_bg, fg=text_color).pack(side="left")
        self.password_var = tk.StringVar(value=self.tracker.config.get('OBS', 'password'))
        tk.Entry(pass_frame, textvariable=self.password_var, show="*", width=12, bg="#333", fg="white").pack(side="left", padx=(5, 0))
    
    def create_recording_section(self, parent, bg_color, frame_bg, text_color, accent_color):
        """Create recording section"""
        frame = tk.LabelFrame(parent, text="Recording Status", 
                             bg=frame_bg, fg=accent_color,
                             font=('Arial', 10, 'bold'))
        frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Status
        self.recording_status_label = tk.Label(frame, 
                                              text="Waiting for OBS", 
                                              bg=frame_bg, fg="gray",
                                              font=('Arial', 12, 'bold'))
        self.recording_status_label.pack(pady=10)
        
        # Stats
        stats_frame = tk.Frame(frame, bg=frame_bg)
        stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.duration_label = tk.Label(stats_frame, text="Duration: 00:00:00", 
                                      bg=frame_bg, fg=text_color)
        self.duration_label.pack(side="left")
        
        self.events_label = tk.Label(stats_frame, text="Events: 0", 
                                    bg=frame_bg, fg=text_color)
        self.events_label.pack(side="left", padx=(20, 0))
        
        # Detailed stats
        detail_frame = tk.Frame(frame, bg=frame_bg)
        detail_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.mouse_label = tk.Label(detail_frame, text="Mouse: 0", 
                                   bg=frame_bg, fg=text_color)
        self.mouse_label.pack(side="left")
        
        self.keyboard_label = tk.Label(detail_frame, text="Keyboard: 0", 
                                      bg=frame_bg, fg=text_color)
        self.keyboard_label.pack(side="left", padx=(20, 0))
        
        self.gamepad_label = tk.Label(detail_frame, text="Gamepad: 0", 
                                     bg=frame_bg, fg=text_color)
        self.gamepad_label.pack(side="left", padx=(20, 0))
    
    def create_settings_section(self, parent, bg_color, frame_bg, text_color, accent_color):
        """Create settings section"""
        frame = tk.LabelFrame(parent, text="Settings", 
                             bg=frame_bg, fg=accent_color,
                             font=('Arial', 10, 'bold'))
        frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Directory
        dir_frame = tk.Frame(frame, bg=frame_bg)
        dir_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(dir_frame, text="Save Directory:", bg=frame_bg, fg=text_color).pack(anchor="w")
        
        path_frame = tk.Frame(dir_frame, bg=frame_bg)
        path_frame.pack(fill="x", pady=(5, 0))
        
        self.save_label = tk.Label(path_frame, 
                                  text=str(self.tracker.save_dir), 
                                  bg=frame_bg, fg="#ccc",
                                  font=('Arial', 9))
        self.save_label.pack(side="left", fill="x", expand=True)
        
        tk.Button(path_frame, text="Change", 
                 command=self.choose_directory,
                 bg="#2196F3", fg="white", relief="flat",
                 padx=15, pady=3).pack(side="right")
        
        # Mouse & Keyboard
        mk_frame = tk.LabelFrame(frame, text="Mouse & Keyboard",
                                bg=frame_bg, fg=accent_color,
                                font=('Arial', 9, 'bold'))
        mk_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.include_position_var = tk.BooleanVar(
            value=self.tracker.config.getboolean('Recording', 'include_mouse_position', fallback=True)
        )
        
        # Custom checkbox with better styling
        checkbox_frame = tk.Frame(mk_frame, bg=frame_bg)
        checkbox_frame.pack(fill="x", padx=5, pady=5)
        
        position_checkbox = tk.Checkbutton(checkbox_frame,
                                          text="Include mouse absolute position",
                                          variable=self.include_position_var,
                                          command=self.save_settings,
                                          bg=frame_bg, fg=text_color,
                                          selectcolor="#4CAF50",  # 绿色选中颜色
                                          activebackground=frame_bg,
                                          activeforeground=text_color,
                                          font=('Arial', 9))
        position_checkbox.pack(anchor="w")
        
        # Gamepad Settings
        gamepad_frame = tk.LabelFrame(frame, text="Working Gamepad Method",
                                     bg=frame_bg, fg=accent_color,
                                     font=('Arial', 9, 'bold'))
        gamepad_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.gamepad_enabled_var = tk.BooleanVar(value=self.tracker.gamepad_enabled)
        
        # Gamepad checkbox
        gamepad_checkbox_frame = tk.Frame(gamepad_frame, bg=frame_bg)
        gamepad_checkbox_frame.pack(fill="x", padx=5, pady=(5, 10))
        
        gamepad_checkbox = tk.Checkbutton(gamepad_checkbox_frame,
                                         text="Enable gamepad recording (using proven working method)",
                                         variable=self.gamepad_enabled_var,
                                         command=self.save_settings,
                                         bg=frame_bg, fg=text_color,
                                         selectcolor="#2196F3",  # 蓝色选中颜色
                                         activebackground=frame_bg,
                                         activeforeground=text_color,
                                         font=('Arial', 9))
        gamepad_checkbox.pack(anchor="w")
        
        # Gamepad status
        status_frame = tk.Frame(gamepad_frame, bg=frame_bg)
        status_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        self.gamepad_status_label = tk.Label(status_frame,
                                            text="Checking...",
                                            bg=frame_bg, fg="orange",
                                            font=('Arial', 9))
        self.gamepad_status_label.pack(side="left")
        
        tk.Button(status_frame, text="Refresh",
                 command=self.refresh_gamepad,
                 bg="#FF9800", fg="white", relief="flat",
                 padx=10, pady=2).pack(side="right")
    
    def create_controls_section(self, parent, bg_color, frame_bg, text_color, accent_color):
        """Create controls section"""
        frame = tk.LabelFrame(parent, text="Manual Controls",
                             bg=frame_bg, fg=accent_color,
                             font=('Arial', 10, 'bold'))
        frame.pack(fill="x", pady=(0, 15), padx=10)
        
        tk.Label(frame,
                text="Normal operation: Tracking starts/stops automatically with OBS recording",
                bg=frame_bg, fg=text_color,
                font=('Arial', 9)).pack(pady=(10, 15))
        
        button_frame = tk.Frame(frame, bg=frame_bg)
        button_frame.pack(pady=(0, 10))
        
        self.manual_start_button = tk.Button(button_frame, text="Manual Start",
                                            command=self.manual_start,
                                            bg="#4CAF50", fg="white",
                                            font=('Arial', 10, 'bold'),
                                            relief="flat", padx=25, pady=8)
        self.manual_start_button.pack(side="left", padx=(0, 15))
        
        self.manual_stop_button = tk.Button(button_frame, text="Manual Stop",
                                           command=self.manual_stop,
                                           bg="#f44336", fg="white",
                                           font=('Arial', 10, 'bold'),
                                           relief="flat", padx=25, pady=8)
        self.manual_stop_button.pack(side="right")
    
    def start_connection_check(self):
        """Start periodic checks"""
        self.check_connections()
        self.root.after(2000, self.start_connection_check)
    
    def check_connections(self):
        """Check connections"""
        # OBS status
        if self.tracker.obs_connected:
            self.obs_status_label.config(text="Connected to OBS", fg="#4CAF50")
            self.connect_button.config(text="Disconnect", bg="#f44336")
        else:
            self.obs_status_label.config(text="Disconnected", fg="#f44336")
            self.connect_button.config(text="Connect to OBS", bg="#4CAF50")
        
        # Recording status
        if self.tracker.recording:
            self.recording_status_label.config(text="Recording Active", fg="#f44336")
            self.update_stats()
        else:
            if self.tracker.obs_connected:
                self.recording_status_label.config(text="Connected - Waiting for OBS Recording", fg="#FF9800")
            else:
                self.recording_status_label.config(text="Waiting for OBS Connection", fg="gray")
        
        # Gamepad status
        self.update_gamepad_status()
    
    def update_stats(self):
        """Update recording stats"""
        if self.tracker.recording and self.tracker.start_time:
            elapsed = time.perf_counter() - self.tracker.start_time
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
            self.duration_label.config(text=f"Duration: {duration_str}")
            self.events_label.config(text=f"Events: {self.tracker.event_count}")
            self.mouse_label.config(text=f"Mouse: {self.tracker.mouse_count}")
            self.keyboard_label.config(text=f"Keyboard: {self.tracker.keyboard_count}")
            self.gamepad_label.config(text=f"Gamepad: {self.tracker.gamepad_count}")
    
    def update_gamepad_status(self):
        """Update gamepad status"""
        if not PYGAME_AVAILABLE:
            self.gamepad_status_label.config(text="pygame not available", fg="#f44336")
            return
        
        if not self.tracker.gamepad_enabled:
            self.gamepad_status_label.config(text="Gamepad disabled", fg="gray")
            return
        
        try:
            count = self.tracker.gamepad_tracker.get_gamepad_count()
            
            if count == 0:
                self.gamepad_status_label.config(text="No gamepads detected", fg="#FF9800")
            elif self.tracker.gamepad_tracker.tracking:
                if self.tracker.gamepad_tracker.joystick:
                    name = self.tracker.gamepad_tracker.joystick.get_name()
                    self.gamepad_status_label.config(text=f"WORKING: {name}", fg="#4CAF50")
                else:
                    self.gamepad_status_label.config(text="Gamepad tracking active", fg="#4CAF50")
            else:
                self.gamepad_status_label.config(text=f"{count} gamepad(s) available", fg="#FF9800")
                
        except Exception as e:
            self.gamepad_status_label.config(text=f"Error: {str(e)[:20]}...", fg="#f44336")
    
    def refresh_gamepad(self):
        """Refresh gamepad status"""
        self.update_gamepad_status()
    
    def toggle_obs_connection(self):
        """Toggle OBS connection"""
        if self.tracker.obs_connected:
            self.tracker.disconnect_obs()
        else:
            self.save_connection_settings()
            threading.Thread(target=self.tracker.connect_obs, daemon=True).start()
    
    def save_connection_settings(self):
        """Save connection settings"""
        self.tracker.config.set('OBS', 'host', self.host_var.get())
        self.tracker.config.set('OBS', 'port', self.port_var.get())
        self.tracker.config.set('OBS', 'password', self.password_var.get())
        self.tracker.save_settings()
    
    def save_settings(self):
        """Save settings"""
        self.tracker.config.set('Recording', 'include_mouse_position', 
                               str(self.include_position_var.get()))
        self.tracker.gamepad_enabled = self.gamepad_enabled_var.get()
        self.tracker.config.set('Gamepad', 'enabled', str(self.tracker.gamepad_enabled))
        self.tracker.save_settings()
    
    def choose_directory(self):
        """Choose save directory"""
        directory = filedialog.askdirectory(title="Choose Save Directory")
        if directory:
            self.tracker.save_dir = Path(directory)
            self.tracker.save_dir.mkdir(exist_ok=True)
            self.tracker.config.set('Recording', 'save_directory', str(directory))
            self.tracker.save_settings()
            self.save_label.config(text=str(self.tracker.save_dir))
    
    def manual_start(self):
        """Manual start recording"""
        self.tracker.start_recording_sync()
    
    def manual_stop(self):
        """Manual stop recording"""
        self.tracker.stop_recording()
    
    def on_closing(self):
        """Handle window closing"""
        if self.tracker.recording:
            if messagebox.askokcancel("Quit", "Recording is active. Stop and quit?"):
                self.tracker.stop_recording()
                self.tracker.disconnect_obs()
                self.root.destroy()
        else:
            self.tracker.disconnect_obs()
            self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("OBS TRACKER - Improved UI with Working Gamepad")
    print("=" * 50)
    
    print(f"pynput: {'Available' if PYNPUT_AVAILABLE else 'Missing'}")
    print(f"obsws-python: {'Available' if OBS_AVAILABLE else 'Missing'}")
    print(f"pygame: {'Available' if PYGAME_AVAILABLE else 'Missing'}")
    print()
    
    if PYGAME_AVAILABLE:
        print("Using the proven working gamepad method!")
    
    try:
        app = ImprovedOBSTrackerGUI()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to start: {e}")

if __name__ == "__main__":
    main()
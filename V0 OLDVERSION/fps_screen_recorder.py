import time
import threading
import subprocess
import os
import json
import sys
import shutil
from datetime import datetime
from pynput import mouse, keyboard
from tkinter import Tk, messagebox, filedialog, ttk
import tkinter as tk

class BundledFFmpegRecorder:
    def __init__(self):
        self.recording = False
        self.ffmpeg_process = None
        self.start_time = None
        self.log_file = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_mouse_pos = None
        self.video_path = None
        self.log_path = None
        self.ffmpeg_path = None
        
    def get_ffmpeg_path(self):
        """Get the path to bundled FFmpeg executable"""
        if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
            return self.ffmpeg_path
        
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as EXE
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Look for FFmpeg in different locations
        possible_paths = [
            os.path.join(base_path, 'ffmpeg', 'ffmpeg.exe'),  # Bundled in ffmpeg folder
            os.path.join(base_path, 'ffmpeg.exe'),            # Bundled in root
            os.path.join(os.getcwd(), 'ffmpeg', 'ffmpeg.exe'), # Current dir
            os.path.join(os.getcwd(), 'ffmpeg.exe'),           # Current dir root
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.ffmpeg_path = path
                return path
        
        # Try system PATH as fallback
        ffmpeg_system = shutil.which('ffmpeg')
        if ffmpeg_system:
            self.ffmpeg_path = ffmpeg_system
            return ffmpeg_system
        
        return None
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            return False, "FFmpeg not found"
        
        try:
            result = subprocess.run([ffmpeg_path, '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, f"FFmpeg found: {ffmpeg_path}"
            else:
                return False, f"FFmpeg error: {result.stderr}"
        except Exception as e:
            return False, f"FFmpeg check failed: {str(e)}"
    
    def get_screen_resolution(self):
        """Get screen resolution using tkinter (more reliable)"""
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return width, height
        except Exception as e:
            print(f"Error getting screen resolution: {e}")
            return 1920, 1080
    
    def log_event(self, event_type, details):
        """Log event to JSONL file"""
        if self.log_file and self.start_time:
            elapsed = time.perf_counter() - self.start_time
            log_entry = {
                "timestamp": round(elapsed, 3),
                "event_type": event_type,
                "details": details
            }
            self.log_file.write(json.dumps(log_entry) + "\n")
            self.log_file.flush()
    
    def on_mouse_move(self, x, y):
        """Handle mouse movement events"""
        if not self.recording:
            return
            
        if self.last_mouse_pos is not None:
            delta_x = x - self.last_mouse_pos[0]
            delta_y = y - self.last_mouse_pos[1]
            if abs(delta_x) > 0 or abs(delta_y) > 0:
                self.log_event("MouseDelta", {"dx": delta_x, "dy": delta_y})
        
        self.last_mouse_pos = (x, y)
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.recording:
            return
            
        action = "pressed" if pressed else "released"
        button_name = str(button).replace('Button.', '')
        self.log_event("MouseClick", {
            "button": button_name, 
            "action": action,
            "x": x,
            "y": y
        })
    
    def on_key_press(self, key):
        """Handle key press events"""
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
        """Handle key release events"""
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
        
        # Stop recording if F10 is pressed
        if key == keyboard.Key.f10:
            print("F10 pressed - stopping recording")
            self.stop_recording()
    
    def start_input_listeners(self):
        """Start mouse and keyboard listeners"""
        try:
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
            return True
        except Exception as e:
            print(f"Failed to start input listeners: {e}")
            return False
    
    def stop_input_listeners(self):
        """Stop input listeners"""
        try:
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
        except Exception as e:
            print(f"Error stopping listeners: {e}")
    
    def start_recording(self, save_dir, fps=30, quality="medium"):
        """Start FFmpeg-based screen recording"""
        if self.recording:
            return False
        
        try:
            # Get FFmpeg path
            ffmpeg_path = self.get_ffmpeg_path()
            if not ffmpeg_path:
                raise Exception("FFmpeg not found. Please ensure ffmpeg.exe is in the program directory.")
            
            # Create timestamped filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.video_path = os.path.join(save_dir, f"screen_recording_{timestamp}.mp4")
            self.log_path = os.path.join(save_dir, f"input_log_{timestamp}.jsonl")
            
            # Get screen resolution
            width, height = self.get_screen_resolution()
            print(f"Recording resolution: {width}x{height}")
            
            # Quality settings optimized for gaming
            quality_settings = {
                "low": {
                    "crf": "28", 
                    "preset": "ultrafast", 
                    "bufsize": "1000k",
                    "maxrate": "1500k"
                },
                "medium": {
                    "crf": "23", 
                    "preset": "fast", 
                    "bufsize": "2000k",
                    "maxrate": "3000k"
                },
                "high": {
                    "crf": "18", 
                    "preset": "medium", 
                    "bufsize": "4000k",
                    "maxrate": "6000k"
                }
            }
            
            settings = quality_settings.get(quality, quality_settings["medium"])
            
            # Build optimized FFmpeg command for Windows
            ffmpeg_cmd = [
                ffmpeg_path,
                # Input settings
                '-f', 'gdigrab',
                '-framerate', str(fps),
                '-show_region', '0',  # Don't show capture region
                '-i', 'desktop',
                
                # Video encoding settings
                '-c:v', 'libx264',
                '-preset', settings["preset"],
                '-crf', settings["crf"],
                '-maxrate', settings["maxrate"],
                '-bufsize', settings["bufsize"],
                
                # Format settings
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                
                # Performance settings
                '-threads', '4',  # Use 4 threads
                '-thread_type', 'slice',
                
                # Reduce CPU usage
                '-tune', 'zerolatency',
                
                # Output
                '-y',  # Overwrite output file
                self.video_path
            ]
            
            print(f"Starting recording with command:")
            print(' '.join(ffmpeg_cmd))
            
            # Start FFmpeg process with optimized settings
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = subprocess.SW_HIDE
            
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startup_info,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait a moment to check if FFmpeg started successfully
            time.sleep(0.5)
            if self.ffmpeg_process.poll() is not None:
                # FFmpeg exited immediately, check for errors
                stdout, stderr = self.ffmpeg_process.communicate()
                raise Exception(f"FFmpeg failed to start:\n{stderr}")
            
            # Initialize logging
            self.log_file = open(self.log_path, "w", buffering=1)
            self.start_time = time.perf_counter()
            self.last_mouse_pos = None
            
            # Start input listeners
            if not self.start_input_listeners():
                raise Exception("Failed to start input listeners")
            
            self.recording = True
            print(f"Recording started successfully!")
            print(f"Video: {self.video_path}")
            print(f"Log: {self.log_path}")
            return True
            
        except Exception as e:
            print(f"Failed to start recording: {e}")
            self.cleanup_recording()
            raise e
    
    def stop_recording(self):
        """Stop recording"""
        if not self.recording:
            return
        
        print("Stopping recording...")
        self.recording = False
        
        try:
            # Stop FFmpeg gracefully
            if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
                print("Sending quit signal to FFmpeg...")
                try:
                    self.ffmpeg_process.stdin.write(b'q\n')
                    self.ffmpeg_process.stdin.flush()
                    self.ffmpeg_process.stdin.close()
                except:
                    pass  # Ignore if pipe is already closed
                
                # Wait for FFmpeg to finish
                try:
                    stdout, stderr = self.ffmpeg_process.communicate(timeout=10)
                    print("FFmpeg stopped gracefully")
                    if stderr:
                        print(f"FFmpeg stderr: {stderr}")
                except subprocess.TimeoutExpired:
                    print("FFmpeg didn't stop gracefully, terminating...")
                    self.ffmpeg_process.terminate()
                    try:
                        self.ffmpeg_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.ffmpeg_process.kill()
            
        except Exception as e:
            print(f"Error stopping FFmpeg: {e}")
        finally:
            self.cleanup_recording()
    
    def cleanup_recording(self):
        """Clean up recording resources"""
        try:
            if self.ffmpeg_process:
                if self.ffmpeg_process.poll() is None:
                    self.ffmpeg_process.terminate()
                self.ffmpeg_process = None
            
            if self.log_file:
                self.log_file.close()
                self.log_file = None
            
            self.stop_input_listeners()
            
            print("Recording resources cleaned up")
            
        except Exception as e:
            print(f"Cleanup error: {e}")

# GUI Application
class RecorderGUI:
    def __init__(self):
        self.recorder = BundledFFmpegRecorder()
        self.save_dir = os.getcwd()
        self.setup_gui()
        self.update_timer = None
        
    def setup_gui(self):
        """Setup the GUI"""
        self.root = tk.Tk()
        self.root.title("Gaming Screen & Input Recorder")
        self.root.geometry("1000x1000")
        self.root.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Gaming Screen & Input Recorder", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))
        
        # FFmpeg status
        ffmpeg_available, ffmpeg_message = self.recorder.check_ffmpeg()
        if ffmpeg_available:
            status_text = "✅ Ready to record"
            status_color = "green"
        else:
            status_text = f"❌ {ffmpeg_message}"
            status_color = "red"
        
        self.ffmpeg_status_label = ttk.Label(main_frame, text=status_text, 
                                            font=("Arial", 10))
        self.ffmpeg_status_label.pack(pady=(0, 10))
        
        # Current status
        self.status_label = ttk.Label(main_frame, text="Ready", 
                                     font=("Arial", 14, "bold"))
        self.status_label.pack(pady=(0, 10))
        
        # Duration
        self.duration_label = ttk.Label(main_frame, text="Duration: 00:00:00", 
                                       font=("Arial", 12))
        self.duration_label.pack(pady=(0, 20))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Recording Settings", padding="15")
        settings_frame.pack(fill="x", pady=(0, 15))
        
        # Settings grid
        # FPS setting
        ttk.Label(settings_frame, text="Frame Rate (FPS):").grid(row=0, column=0, sticky="w", pady=5)
        self.fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(settings_frame, textvariable=self.fps_var, 
                                values=["15", "24", "30", "60"], width=15, state="readonly")
        fps_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Quality setting
        ttk.Label(settings_frame, text="Quality:").grid(row=1, column=0, sticky="w", pady=5)
        self.quality_var = tk.StringVar(value="medium")
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_var,
                                    values=["low", "medium", "high"], width=15, state="readonly")
        quality_combo.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Quality descriptions
        quality_desc = {
            "low": "Fast encoding, smaller file size",
            "medium": "Balanced quality and performance", 
            "high": "Best quality, larger file size"
        }
        
        def update_quality_desc(*args):
            desc = quality_desc.get(self.quality_var.get(), "")
            quality_desc_label.config(text=desc)
        
        self.quality_var.trace('w', update_quality_desc)
        
        quality_desc_label = ttk.Label(settings_frame, text=quality_desc["medium"], 
                                      font=("Arial", 8), foreground="gray")
        quality_desc_label.grid(row=1, column=2, sticky="w", padx=(10, 0), pady=5)
        
        # Save directory section
        save_frame = ttk.LabelFrame(main_frame, text="Save Location", padding="15")
        save_frame.pack(fill="x", pady=(0, 20))
        
        self.save_dir_label = ttk.Label(save_frame, text=f"📁 {self.save_dir}", 
                                       font=("Arial", 9))
        self.save_dir_label.pack(anchor="w", pady=(0, 10))
        
        choose_dir_button = ttk.Button(save_frame, text="Choose Directory", 
                                      command=self.choose_save_dir)
        choose_dir_button.pack()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="🔴 Start Recording", 
                                      command=self.start_recording, width=20)
        self.start_button.pack(side="left", padx=(0, 15))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop Recording", 
                                     command=self.stop_recording, width=20, state="disabled")
        self.stop_button.pack(side="right")
        
        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="15")
        info_frame.pack(fill="x")
        
        info_text = ("📺 Records full screen with high quality\n"
                     "🖱️  Captures all mouse movements and clicks (for FPS games)\n"
                     "⌨️  Captures all keyboard presses and releases\n"
                     "🛑 Press F10 during recording to stop\n"
                     "📁 Files are timestamped to prevent overwriting\n"
                     "⚡ Includes bundled FFmpeg - no external installation needed")
        
        info_label = ttk.Label(info_frame, text=info_text, font=("Arial", 9),
                              justify="left")
        info_label.pack(anchor="w")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Disable start button if FFmpeg not available
        if not ffmpeg_available:
            self.start_button.config(state="disabled")
    
    def update_duration(self):
        """Update duration display"""
        if self.recorder.recording and self.recorder.start_time:
            elapsed = time.perf_counter() - self.recorder.start_time
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.duration_label.config(text=f"🕐 Duration: {duration_str}")
            self.update_timer = self.root.after(1000, self.update_duration)
    
    def start_recording(self):
        """Start recording"""
        if self.recorder.recording:
            return
        
        try:
            fps = int(self.fps_var.get())
            quality = self.quality_var.get()
            
            self.recorder.start_recording(self.save_dir, fps=fps, quality=quality)
            
            self.status_label.config(text="🔴 RECORDING", foreground="red")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            self.update_duration()
            
        except Exception as e:
            print(f"Failed to start recording: {e}")
            messagebox.showerror("Recording Error", 
                f"Failed to start recording:\n\n{str(e)}\n\n"
                "Make sure ffmpeg.exe is in the program directory.")
            self.reset_gui_after_stop()
    
    def stop_recording(self):
        """Stop recording"""
        if not self.recorder.recording:
            return
        
        self.status_label.config(text="⏹️ Stopping...", foreground="orange")
        self.stop_button.config(state="disabled")
        
        # Stop in separate thread to prevent GUI freezing
        threading.Thread(target=self.recorder.stop_recording, daemon=True).start()
        self.root.after(3000, self.reset_gui_after_stop)
    
    def reset_gui_after_stop(self):
        """Reset GUI after recording stops"""
        self.status_label.config(text="Ready", foreground="black")
        self.duration_label.config(text="Duration: 00:00:00")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
        
        if os.path.exists(self.recorder.video_path or ""):
            file_size = os.path.getsize(self.recorder.video_path) / (1024*1024)  # MB
            messagebox.showinfo("Recording Complete", 
                f"✅ Recording saved successfully!\n\n"
                f"📁 Location: {self.save_dir}\n"
                f"🎬 Video: {os.path.basename(self.recorder.video_path)} ({file_size:.1f} MB)\n"
                f"📝 Input log: {os.path.basename(self.recorder.log_path)}")
        else:
            messagebox.showinfo("Recording Stopped", "Recording has been stopped.")
    
    def choose_save_dir(self):
        """Choose save directory"""
        new_dir = filedialog.askdirectory(title="Choose Save Directory")
        if new_dir:
            self.save_dir = new_dir
            self.save_dir_label.config(text=f"📁 {self.save_dir}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.recorder.recording:
            if messagebox.askokcancel("Quit", "Recording is in progress. Stop and quit?"):
                self.recorder.stop_recording()
                self.root.after(2000, self.root.destroy)
        else:
            self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        if sys.platform != "win32":
            messagebox.showerror("Platform Error", "This application is designed for Windows only.")
            return
        
        print("Gaming Screen Recorder initialized.")
        self.root.mainloop()

if __name__ == "__main__":
    app = RecorderGUI()
    app.run()

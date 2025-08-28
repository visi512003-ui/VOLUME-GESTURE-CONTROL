import os
import platform
import subprocess
import threading
import time

class VolumeController:
    def __init__(self):
        """Initialize volume controller for cross-platform support"""
        self.system = platform.system()
        self.current_volume = 50
        self.last_set_time = 0
        self.min_interval = 0.1  # Minimum time between volume changes (seconds)
        
        # Initialize system-specific volume control
        self._init_system_volume()
    
    def _init_system_volume(self):
        """Initialize system-specific volume control"""
        try:
            if self.system == "Windows":
                self._init_windows_volume()
            elif self.system == "Darwin":  # macOS
                self._init_macos_volume()
            elif self.system == "Linux":
                self._init_linux_volume()
            else:
                print(f"Warning: Volume control not fully supported on {self.system}")
        except Exception as e:
            print(f"Error initializing volume control: {e}")
    
    def _init_windows_volume(self):
        """Initialize Windows volume control using PowerShell"""
        self.volume_method = "windows_powershell"
    
    def _init_macos_volume(self):
        """Initialize macOS volume control using osascript"""
        self.volume_method = "macos_osascript"
    
    def _init_linux_volume(self):
        """Initialize Linux volume control using ALSA/PulseAudio"""
        # Check if PulseAudio is available
        try:
            subprocess.run(["pactl", "--version"], 
                         capture_output=True, check=True)
            self.volume_method = "linux_pulseaudio"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to ALSA
            try:
                subprocess.run(["amixer", "--version"], 
                             capture_output=True, check=True)
                self.volume_method = "linux_alsa"
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.volume_method = "unsupported"
                print("Warning: No supported audio system found (PulseAudio/ALSA)")
    
    def set_volume(self, volume_percent):
        """Set system volume (0-100)"""
        current_time = time.time()
        
        # Rate limiting to prevent too frequent volume changes
        if current_time - self.last_set_time < self.min_interval:
            return False
        
        volume_percent = max(0, min(100, int(volume_percent)))
        
        try:
            success = self._set_system_volume(volume_percent)
            if success:
                self.current_volume = volume_percent
                self.last_set_time = current_time
            return success
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False
    
    def _set_system_volume(self, volume_percent):
        """Set volume using system-specific method"""
        try:
            if self.volume_method == "windows_powershell":
                return self._set_windows_volume(volume_percent)
            elif self.volume_method == "macos_osascript":
                return self._set_macos_volume(volume_percent)
            elif self.volume_method == "linux_pulseaudio":
                return self._set_linux_pulseaudio_volume(volume_percent)
            elif self.volume_method == "linux_alsa":
                return self._set_linux_alsa_volume(volume_percent)
            else:
                print(f"Volume control not supported: {self.volume_method}")
                return False
        except Exception as e:
            print(f"Error in _set_system_volume: {e}")
            return False
    
    def _set_windows_volume(self, volume_percent):
        """Set Windows volume using PowerShell"""
        try:
            # PowerShell command to set volume
            ps_command = f"""
            Add-Type -TypeDefinition @"
            using System;
            using System.Runtime.InteropServices;
            public class Audio {{
                [DllImport("user32.dll")]
                public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
            }}
            "@
            
            $volume = {volume_percent}
            $currentVol = [Math]::Round([audio]::Volume * 100)
            
            if ($volume -gt $currentVol) {{
                for ($i = $currentVol; $i -lt $volume; $i += 2) {{
                    [Audio]::keybd_event(0xAF, 0, 0, 0)
                    [Audio]::keybd_event(0xAF, 0, 2, 0)
                    Start-Sleep -Milliseconds 10
                }}
            }} elseif ($volume -lt $currentVol) {{
                for ($i = $currentVol; $i -gt $volume; $i -= 2) {{
                    [Audio]::keybd_event(0xAE, 0, 0, 0)
                    [Audio]::keybd_event(0xAE, 0, 2, 0)
                    Start-Sleep -Milliseconds 10
                }}
            }}
            """
            
            subprocess.run(["powershell", "-Command", ps_command], 
                         capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"Windows volume control error: {e}")
            return False
    
    def _set_macos_volume(self, volume_percent):
        """Set macOS volume using osascript"""
        try:
            # Convert to macOS volume scale (0-7)
            macos_volume = int((volume_percent / 100) * 7)
            command = f"osascript -e 'set volume output volume {macos_volume}'"
            subprocess.run(command, shell=True, check=True)
            return True
        except Exception as e:
            print(f"macOS volume control error: {e}")
            return False
    
    def _set_linux_pulseaudio_volume(self, volume_percent):
        """Set Linux volume using PulseAudio"""
        try:
            command = ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume_percent}%"]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"PulseAudio volume control error: {e}")
            return False
    
    def _set_linux_alsa_volume(self, volume_percent):
        """Set Linux volume using ALSA"""
        try:
            command = ["amixer", "set", "Master", f"{volume_percent}%"]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"ALSA volume control error: {e}")
            return False
    
    def get_current_volume(self):
        """Get current system volume"""
        return self.current_volume
    
    def mute(self):
        """Mute system volume"""
        return self.set_volume(0)
    
    def unmute(self, volume=50):
        """Unmute system volume to specified level"""
        return self.set_volume(volume)
    
    def volume_up(self, step=5):
        """Increase volume by step amount"""
        new_volume = min(100, self.current_volume + step)
        return self.set_volume(new_volume)
    
    def volume_down(self, step=5):
        """Decrease volume by step amount"""
        new_volume = max(0, self.current_volume - step)
        return self.set_volume(new_volume)

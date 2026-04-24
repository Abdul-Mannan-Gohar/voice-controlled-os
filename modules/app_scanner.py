"""
App Scanner Module
Automatically scans Windows registry + common paths to find ALL installed apps.
No hardcoded paths needed — finds apps by itself.
"""

import os
import winreg
import subprocess
import logging
import json
import time

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "app_cache.json")

# Common executable locations to scan
SCAN_PATHS = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
    os.path.expandvars(r"%APPDATA%"),
    os.path.expandvars(r"%LOCALAPPDATA%"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft"),
]

# Registry keys where installed apps are listed
REGISTRY_KEYS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]

# Built-in Windows apps (always available)
BUILTIN_APPS = {
    "notepad":        "notepad.exe",
    "calculator":     "calc.exe",
    "paint":          "mspaint.exe",
    "task manager":   "taskmgr.exe",
    "file explorer":  "explorer.exe",
    "explorer":       "explorer.exe",
    "cmd":            "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell":     "powershell.exe",
    "snipping tool":  "SnippingTool.exe",
    "control panel":  "control.exe",
    "settings":       "ms-settings:",
    "wordpad":        "write.exe",
    "character map":  "charmap.exe",
    "magnifier":      "magnify.exe",
    "narrator":       "Narrator.exe",
    "on screen keyboard": "osk.exe",
    "registry editor": "regedit.exe",
    "disk cleanup":   "cleanmgr.exe",
    "device manager": "devmgmt.msc",
    "event viewer":   "eventvwr.msc",
    "services":       "services.msc",
    "task scheduler": "taskschd.msc",
}


class AppScanner:
    def __init__(self):
        self.apps = {}          # name -> path
        self.scan_time = None
        self._load_or_scan()

    def _load_or_scan(self):
        """Load from cache if fresh, else scan."""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                age = time.time() - data.get("timestamp", 0)
                if age < 3600:   # cache valid for 1 hour
                    self.apps = data.get("apps", {})
                    self.scan_time = data.get("timestamp")
                    logger.info(f"Loaded {len(self.apps)} apps from cache.")
                    return
            except Exception:
                pass
        self.scan()

    def scan(self, speak_fn=None):
        """Full system scan — registry + file system."""
        if speak_fn:
            speak_fn("Scanning your system for installed applications. Please wait a moment.")

        self.apps = dict(BUILTIN_APPS)

        # 1. Registry scan
        self._scan_registry()

        # 2. Common folder scan
        self._scan_folders()

        # 3. Start menu shortcuts
        self._scan_start_menu()

        self.scan_time = time.time()
        self._save_cache()

        count = len(self.apps)
        logger.info(f"Scan complete. Found {count} apps.")
        if speak_fn:
            speak_fn(f"Scan complete. I found {count} applications on your system.")

        return count

    def _scan_registry(self):
        for hive, key_path in REGISTRY_KEYS:
            try:
                key = winreg.OpenKey(hive, key_path)
                i = 0
                while True:
                    try:
                        sub_name = winreg.EnumKey(key, i)
                        sub_key  = winreg.OpenKey(key, sub_name)
                        try:
                            name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                            # Try InstallLocation or DisplayIcon for the path
                            exe_path = None
                            for val in ["InstallLocation", "DisplayIcon"]:
                                try:
                                    v, _ = winreg.QueryValueEx(sub_key, val)
                                    v = v.strip().strip('"').split(",")[0]
                                    if v.endswith(".exe") and os.path.exists(v):
                                        exe_path = v
                                        break
                                    elif os.path.isdir(v):
                                        # Search for exe in that folder
                                        for f in os.listdir(v):
                                            if f.endswith(".exe") and not f.startswith("unins"):
                                                exe_path = os.path.join(v, f)
                                                break
                                except Exception:
                                    pass
                            if name and exe_path:
                                clean = name.strip().lower()
                                self.apps[clean] = exe_path
                                # Also add short name
                                short = clean.split()[0]
                                if short not in self.apps:
                                    self.apps[short] = exe_path
                        except FileNotFoundError:
                            pass
                        finally:
                            winreg.CloseKey(sub_key)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except Exception as e:
                logger.debug(f"Registry scan error: {e}")

    def _scan_folders(self):
        for base in SCAN_PATHS:
            if not os.path.exists(base):
                continue
            try:
                for folder in os.listdir(base):
                    folder_path = os.path.join(base, folder)
                    if not os.path.isdir(folder_path):
                        continue
                    for f in os.listdir(folder_path):
                        if f.endswith(".exe") and not any(
                            x in f.lower() for x in ["unins", "update", "crash", "helper", "setup"]
                        ):
                            name = f[:-4].lower().replace("-", " ").replace("_", " ")
                            if name not in self.apps:
                                self.apps[name] = os.path.join(folder_path, f)
            except Exception:
                continue

    def _scan_start_menu(self):
        start_dirs = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        ]
        for start_dir in start_dirs:
            if not os.path.exists(start_dir):
                continue
            for root, dirs, files in os.walk(start_dir):
                for f in files:
                    if f.endswith(".lnk"):
                        name = f[:-4].lower()
                        lnk_path = os.path.join(root, f)
                        try:
                            # Resolve shortcut target
                            target = self._resolve_lnk(lnk_path)
                            if target and target.endswith(".exe") and os.path.exists(target):
                                self.apps[name] = target
                                short = name.split()[0]
                                if short not in self.apps:
                                    self.apps[short] = target
                        except Exception:
                            pass

    def _resolve_lnk(self, lnk_path: str) -> str | None:
        """Resolve a .lnk shortcut to its target exe path."""
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(lnk_path)
            return shortcut.Targetpath
        except Exception:
            # Fallback: read lnk binary
            try:
                with open(lnk_path, "rb") as f:
                    content = f.read()
                # .lnk files store target path starting at offset 0x4C
                idx = content.find(b"C:\\")
                if idx == -1:
                    idx = content.find(b"c:\\")
                if idx != -1:
                    end = content.find(b"\x00", idx)
                    path = content[idx:end].decode("latin-1", errors="ignore")
                    if path.endswith(".exe"):
                        return path
            except Exception:
                pass
        return None

    def _save_cache(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"timestamp": self.scan_time, "apps": self.apps}, f, indent=2)
        except Exception as e:
            logger.error(f"Cache save error: {e}")

    def find(self, name: str) -> tuple[str | None, str | None]:
        """
        Find app by name. Returns (path, matched_name) or (None, None).
        Does fuzzy matching.
        """
        name = name.strip().lower()

        # Exact match
        if name in self.apps:
            return self.apps[name], name

        # Starts-with match
        for key, path in self.apps.items():
            if key.startswith(name) or name.startswith(key):
                return path, key

        # Contains match
        for key, path in self.apps.items():
            if name in key or key in name:
                return path, key

        return None, None

    def list_apps(self) -> list[str]:
        return sorted(self.apps.keys())

    def get_count(self) -> int:
        return len(self.apps)

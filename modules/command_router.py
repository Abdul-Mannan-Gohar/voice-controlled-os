"""
Smart Command Router
- Auto-detects installed apps from system
- Continuous voice feedback for every action
- File management + Recycle Bin
- Internet speed + network name
- Hardware details with solutions
- Idle: asks "Mannan bhai kya karna chahte ho?"
- Error explanation + solution in voice
"""
from modules.ai_brain import AIBrain
import re
import os
import socket
import subprocess
import webbrowser
import urllib.parse
import psutil
import logging
import time
import threading

logger = logging.getLogger(__name__)


def _internet_ok() -> bool:
    try:
        socket.setdefaulttimeout(3)
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False


class CommandRouter:
    def __init__(self, speak_fn=None, hw_monitor=None, app_scanner=None):
        self.speak     = speak_fn or print
        self.hw        = hw_monitor
        self.scanner   = app_scanner
        self._idle_timer = None
        self._last_cmd_time = time.time()
        self._start_idle_checker()
        self.ai = AIBrain()

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN ROUTER
    # ═══════════════════════════════════════════════════════════════════════════

    def route(self, text: str) -> str | None:
        text = text.strip().lower()
        self._last_cmd_time = time.time()

        # Strip filler
        for f in ["please", "can you", "could you", "yara", "yra",
                  "bhai", "hey", "okay", "ok", "jarvis", "computer"]:
            text = text.replace(f, "").strip()

        logger.info(f"Routing: '{text}'")

        # ── App open ──────────────────────────────────────────────────────────
        m = re.search(r"(?:open|launch|start|chalo|kholo|chalao|shuru karo)\s+(.+)", text)
        if m:            return self._open_app(m.group(1).strip())

        # ── App close ─────────────────────────────────────────────────────────
        m = re.search(r"(?:close|band karo|band kro|kill|quit)\s+(.+)", text)
        if m:
            return self._close_app(m.group(1).strip())

        # ── App scan ──────────────────────────────────────────────────────────
        if re.search(r"scan|refresh apps|update apps|naye apps dhundo", text):
            return self._rescan_apps()

        if re.search(r"(?:list|show|kitne) apps|apps list", text):
            return self._list_apps()

        # ── Volume ────────────────────────────────────────────────────────────
        if re.search(r"volume up|awaaz barha|louder", text):
            return self._volume("up")
        if re.search(r"volume down|awaaz kam|quieter", text):
            return self._volume("down")
        if re.search(r"\bmute\b|khamosh|awaaz band", text):
            return self._mute()
        if re.search(r"\bunmute\b|awaaz wapis|sound on", text):
            return self._unmute()
        m = re.search(r"(?:set volume|volume set)\s+(?:to\s+)?(\d+)", text)
        if m:
            return self._set_volume(int(m.group(1)))

        # ── Hardware ──────────────────────────────────────────────────────────
        if re.search(r"\bcpu\b|processor|procesar", text):
            return self._cpu()
        if re.search(r"\bram\b|\bmemory\b|yadasht", text):
            return self._ram()
        if re.search(r"\bdisk\b|storage|hard drive|disk space", text):
            return self._disk()
        if re.search(r"battery|baitri|charge", text):
            return self._battery()
        if re.search(r"temperature|temp|garmi", text):
            return self._temperature()
        if re.search(r"system (?:status|report|info)|hardware report|pura report", text):
            return self._full_report()
        if re.search(r"running processes|kon chal raha|kaun chal raha", text):
            return self._top_processes()

        # ── Internet ──────────────────────────────────────────────────────────
        if re.search(r"internet|connected|online|network|connection|wifi|net hai", text):
            return self._internet_full()
        if re.search(r"(?:internet |net |network )?speed|kitni speed", text):
            return self._speed_test()
        if re.search(r"(?:my )?ip|ip address", text):
            return self._ip_address()
        if re.search(r"ping|latency", text):
            return self._ping()
        m = re.search(r"search\s+(?:for\s+)?(.+)", text)
        if m:
            return self._search(m.group(1).strip())
        m = re.search(r"open\s+([\w\-]+\.(?:com|net|org|io|gov|pk|edu)\S*)", text)
        if m:
            return self._open_website(m.group(1))

        # ── File Management ───────────────────────────────────────────────────
        if re.search(r"open (?:my )?(documents|downloads|desktop|pictures|music|videos)", text):
            m2 = re.search(r"(documents|downloads|desktop|pictures|music|videos)", text)
            return self._open_folder(m2.group(1) if m2 else "documents")
        m = re.search(r"create (?:a )?(?:new )?folder\s+(.+)", text)
        if m:
            return self._create_folder(m.group(1).strip())
        m = re.search(r"find (?:file\s+)?(.+)", text)
        if m:
            return self._find_file(m.group(1).strip())
        m = re.search(r"delete (?:file\s+)?(.+)", text)
        if m:
            return self._delete_file(m.group(1).strip())

        # ── Recycle Bin ───────────────────────────────────────────────────────
        if re.search(r"recycle bin|recycle|trash|deleted files|kachra", text):
            if re.search(r"show|open|dekho|kya hai|ander kya", text):
                return self._show_recycle_bin()
            if re.search(r"empty|clean|saf karo|delete", text):
                return self._ask_empty_recycle_bin()
            return self._show_recycle_bin()

        if re.search(r"han|haan|yes|ji|okay|theek hai|saf karo|karo", text):
            if hasattr(self, "_pending_recycle") and self._pending_recycle:
                self._pending_recycle = False
                return self._empty_recycle_bin()

        # ── System ────────────────────────────────────────────────────────────
        if re.search(r"screenshot|screen shot|capture", text):
            return self._screenshot()
        if re.search(r"lock (?:screen|pc|computer)|screen lock", text):
            return self._lock()
        if re.search(r"\bshutdown\b|band karo computer|system band karo", text):
            return self._shutdown()
        if re.search(r"restart|reboot|dobara shuru", text):
            return self._restart()
        if re.search(r"cancel shutdown|shutdown cancel", text):
            return self._cancel_shutdown()

        # ── Help ──────────────────────────────────────────────────────────────
        if re.search(r"\bhelp\b|madad|kya kar sakta|commands", text):
            return self._help()

        # AI fallback
        return self.ai.ask(text)

    # ═══════════════════════════════════════════════════════════════════════════
    # APP CONTROL — auto-detect from system
    # ═══════════════════════════════════════════════════════════════════════════

    def _open_app(self, app_name: str) -> str:
        name = app_name.strip().lower()

        # Search in auto-scanned apps
        path, matched = self.scanner.find(name) if self.scanner else (None, None)

        if not path:
            return (
                f"Mannan bhai, {app_name} aapke laptop mein nahi mila. "
                f"Main ne poore system ko check kiya lekin {app_name} install nahi hai. "
                "Pehle install karein, phir main khol deta hoon."
            )

        # Verify path still exists
        expanded = os.path.expandvars(path)
        if not path.startswith("ms-") and not os.path.exists(expanded):
            # Try shell fallback
            try:
                subprocess.Popen(path, shell=True)
                time.sleep(1.5)
                self._bring_to_front(name)
                return (
                    f"Mannan bhai, {matched} mil gaya. Main khol raha hoon. "
                    "App kul gayi hai. Aage batao kya karna hai."
                )
            except Exception:
                return (
                    f"Mannan bhai, {app_name} pehle install tha lekin ab file nahi mili. "
                    "Shayad uninstall ho gaya. Dobara install karein."
                )

        # Open it
        try:
            self.speak(f"Mannan bhai, {matched} mil gaya. Main khol raha hoon.")

            if expanded.startswith("ms-"):
                os.startfile(expanded)
            elif os.path.exists(expanded):
                subprocess.Popen([expanded])
            else:
                subprocess.Popen(path, shell=True)

            time.sleep(1.5)
            self._bring_to_front(matched or name)

            return (
                f"{matched or name} khul gayi hai Mannan bhai. "
                "Aage batao kya karna hai."
            )

        except PermissionError:
            return (
                f"Mannan bhai, {app_name} kholne ki permission nahi mili. "
                "Solution: is program ko administrator ki tarah chalayein. "
                "Right click karein aur Run as administrator select karein."
            )
        except Exception as e:
            return (
                f"Mannan bhai, {app_name} kholne mein masla aaya. "
                f"Error hai: {str(e)}. "
                "Solution: app dobara install karein ya administrator mode mein chalayein."
            )

    def _bring_to_front(self, app_name: str):
        try:
            import win32gui, win32con
            found = []
            def cb(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd).lower()
                    if app_name.split()[0] in t or app_name in t:
                        found.append(hwnd)
            win32gui.EnumWindows(cb, None)
            if found:
                win32gui.ShowWindow(found[0], win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(found[0])
        except Exception:
            pass

    def _close_app(self, app_name: str) -> str:
        name = app_name.strip().lower()
        killed = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if name in proc.info["name"].lower():
                    proc.kill()
                    killed.append(proc.info["name"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if killed:
            return (
                f"Mannan bhai, {', '.join(set(killed))} band kar di. "
                "Aage kya karna hai?"
            )
        return (
            f"Mannan bhai, {name} chal nahi raha tha. "
            "Shayad pehle se band tha."
        )

    def _rescan_apps(self) -> str:
        if self.scanner:
            count = self.scanner.scan(speak_fn=self.speak)
            return f"Mannan bhai, scan mukammal hua. {count} apps mile hain aapke system mein."
        return "App scanner available nahi hai."

    def _list_apps(self) -> str:
        if not self.scanner:
            return "App scanner available nahi hai."
        count = self.scanner.get_count()
        return (
            f"Mannan bhai, aapke system mein {count} apps hain. "
            "Koi bhi app ka naam lein, main dhundh ke khol deta hoon."
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # VOLUME
    # ═══════════════════════════════════════════════════════════════════════════

    def _volume(self, direction: str) -> str:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices   = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol       = cast(interface, POINTER(IAudioEndpointVolume))
            cur       = vol.GetMasterVolumeLevelScalar()
            new       = min(1.0, cur + 0.1) if direction == "up" else max(0.0, cur - 0.1)
            vol.SetMasterVolumeLevelScalar(new, None)
            pct = int(new * 100)
            return f"Mannan bhai, volume {pct} percent ho gaya."
        except Exception:
            keys = "[char]175" if direction == "up" else "[char]174"
            subprocess.run(
                f'powershell -c "$w=New-Object -com wscript.shell; for($i=0;$i -lt 5;$i++){{$w.SendKeys({keys})}}"',
                shell=True, capture_output=True
            )
            word = "barh" if direction == "up" else "kam"
            return f"Mannan bhai, volume {word} gaya."

    def _set_volume(self, level: int) -> str:
        level = max(0, min(100, level))
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices   = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol       = cast(interface, POINTER(IAudioEndpointVolume))
            vol.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Mannan bhai, volume {level} percent set ho gaya."
        except Exception:
            return f"Mannan bhai, volume precisely set nahi hua. Volume up ya down bolein."

    def _mute(self) -> str:
        subprocess.run('powershell -c "$w=New-Object -com wscript.shell;$w.SendKeys([char]173)"',
                       shell=True, capture_output=True)
        msg="Mannan bhai, system mute ho gaya."
        return msg

    def _unmute(self) -> str:
        subprocess.run('powershell -c "$w=New-Object -com wscript.shell;$w.SendKeys([char]173)"',
                       shell=True, capture_output=True)
        
        msg="Mannan bhai, system unmute ho gaya. Awaaz wapis aa gayi."
        return msg
        

    # ═══════════════════════════════════════════════════════════════════════════
    # HARDWARE — detailed with solutions
    # ═══════════════════════════════════════════════════════════════════════════

    def _cpu(self) -> str:
        usage = psutil.cpu_percent(interval=1)
        freq  = psutil.cpu_freq()
        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count(logical=True)
        freq_s = f"{freq.current:.0f} megahertz" if freq else "unknown"

        msg = (
            f"Mannan bhai, CPU ki details ye hain. "
            f"Abhi {usage:.0f} percent use ho raha hai. "
            f"Speed {freq_s} hai. "
            f"{cores} physical cores aur {threads} logical threads hain."
        )
        if usage > 90:
            msg += (
                " Khabardar! CPU bahut zyada load pe hai. "
                "Solution: Task Manager kholen aur dekhen kaunsa program zyada CPU le raha hai, usse band karein."
            )
        elif usage > 75:
            msg += " CPU usage thoda zyada hai. Kuch apps band karein toh behtar hoga."
        else:
            msg += " CPU normal chal raha hai. Sab theek hai."
        return msg

    def _ram(self) -> str:
        mem   = psutil.virtual_memory()
        total = mem.total / (1024**3)
        used  = mem.used  / (1024**3)
        avail = mem.available / (1024**3)

        msg = (
            f"Mannan bhai, RAM ki details: "
            f"Total {total:.1f} gigabyte hai. "
            f"Use ho raha hai {used:.1f} gigabyte. "
            f"Bacha hua hai {avail:.1f} gigabyte. "
            f"Overall {mem.percent:.0f} percent bhari hui hai RAM."
        )
        if mem.percent > 90:
            msg += (
                " Khabardar! RAM bilkul bhari hui hai. "
                "Solution: Kuch apps band karein ya browser tabs close karein. "
                "Zyada RAM chahiye toh RAM upgrade karna hoga."
            )
        elif mem.percent > 75:
            msg += " RAM thodi zyada use ho rahi hai. Kuch programs band karein."
        else:
            msg += " RAM theek chal rahi hai."
        return msg

    def _disk(self) -> str:
        msgs = []
        for p in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(p.mountpoint)
                drive = p.device.replace(":\\\\", "").replace(":", "")
                free_gb = u.free / (1024**3)
                total_gb = u.total / (1024**3)
                s = (
                    f"Drive {drive}: "
                    f"{u.percent:.0f} percent bhari hui hai. "
                    f"{free_gb:.0f} gigabyte free hai "
                    f"aur total {total_gb:.0f} gigabyte hai."
                )
                if u.percent > 95:
                    s += " Khabardar! Disk bilkul bhari hui hai. Fikori files delete karein."
                elif u.percent > 85:
                    s += " Disk zyada bhari hai. Kuch files delete karein ya external drive use karein."
                msgs.append(s)
            except PermissionError:
                continue
        if msgs:
            return "Mannan bhai, disk ki details: " + " | ".join(msgs)
        return "Mannan bhai, disk info nahi mili."

    def _battery(self) -> str:
        bat = psutil.sensors_battery()
        if not bat:
            return "Mannan bhai, battery nahi hai. Ye desktop computer lag raha hai."

        pct    = bat.percent
        status = "charge ho rahi hai" if bat.power_plugged else "battery pe chal raha hai"
        secs   = bat.secsleft

        if secs > 0 and not bat.power_plugged:
            h, m = divmod(secs // 60, 60)
            time_s = f"Takriban {h} ghante {m} minute bacha hai."
        elif bat.power_plugged:
            time_s = "Charger laga hua hai."
        else:
            time_s = ""

        msg = f"Mannan bhai, battery {pct:.0f} percent hai. {status}. {time_s}"

        if not bat.power_plugged and pct <= 10:
            msg += " Khabardar! Battery bahut kam hai. Abhi charger lagayen varna laptop band ho jayega."
        elif not bat.power_plugged and pct <= 25:
            msg += " Battery kam ho rahi hai. Charger lagayen."
        return msg

    def _temperature(self) -> str:
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                msgs = []
                for name, entries in temps.items():
                    for e in entries:
                        msgs.append(f"{name}: {e.current:.0f} degrees")
                return "Mannan bhai, temperatures: " + ", ".join(msgs)
        except Exception:
            pass
        return (
            "Mannan bhai, temperature sensor directly available nahi hai Windows pe. "
            "HWMonitor ya Core Temp app install karein temperature dekhne ke liye."
        )

    def _full_report(self) -> str:
        cpu  = psutil.cpu_percent(interval=0.5)
        mem  = psutil.virtual_memory()
        bat  = psutil.sensors_battery()
        bat_s = f"Battery {bat.percent:.0f} percent" if bat else "Desktop PC"
        return (
            f"Mannan bhai, poora system report: "
            f"CPU {cpu:.0f} percent use ho raha hai. "
            f"RAM {mem.percent:.0f} percent bhari hui hai. "
            f"{bat_s}. "
            "Sab normal lag raha hai. Aage kya karna hai?"
        )

    def _top_processes(self) -> str:
        procs = sorted(
            psutil.process_iter(["name", "cpu_percent", "memory_percent"]),
            key=lambda p: p.info["cpu_percent"] or 0,
            reverse=True
        )[:5]
        parts = []
        for p in procs:
            try:
                parts.append(
                    f"{p.info['name']} ({p.info['cpu_percent']:.0f}% CPU, "
                    f"{p.info['memory_percent']:.0f}% RAM)"
                )
            except Exception:
                pass
        if parts:
            return (
                "Mannan bhai, sabse zyada resources use karne wale programs: "
                + ", ".join(parts)
            )
        return "Mannan bhai, process list nahi mili."

    # ═══════════════════════════════════════════════════════════════════════════
    # INTERNET — full details
    # ═══════════════════════════════════════════════════════════════════════════

    def _internet_full(self) -> str:
        if not _internet_ok():
            return (
                "Mannan bhai, abhi internet nahi hai. "
                "WiFi ya data connection check karein. "
                "Router band hoga toh restart karein."
            )

        # Get network name
        network_name = self._get_wifi_name()

        # Get public IP
        try:
            import requests
            pub_ip = requests.get("https://api.ipify.org", timeout=3).text
        except Exception:
            pub_ip = "unknown"

        # Ping
        ping_ms = self._get_ping()

        msg = (
            f"Mannan bhai, internet connected hai. "
            f"Network ka naam hai: {network_name}. "
            f"Public IP address hai: {pub_ip}. "
            f"Ping {ping_ms} milliseconds hai. "
        )
        if ping_ms < 30:
            msg += "Connection bahut fast hai."
        elif ping_ms < 80:
            msg += "Connection theek hai."
        else:
            msg += "Connection thoda slow lag raha hai."

        return msg

    def _get_wifi_name(self) -> str:
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[-1].strip()
        except Exception:
            pass
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profile"],
                capture_output=True, text=True
            )
            # Ethernet fallback
            result2 = subprocess.run(
                ["ipconfig"], capture_output=True, text=True
            )
            if "Ethernet" in result2.stdout:
                return "Ethernet (cable connection)"
        except Exception:
            pass
        return "unknown network"

    def _get_ping(self) -> int:
        try:
            result = subprocess.run(
                ["ping", "-n", "3", "8.8.8.8"],
                capture_output=True, text=True, timeout=10
            )
            for line in reversed(result.stdout.splitlines()):
                if "Average" in line or "average" in line:
                    nums = re.findall(r"\d+", line)
                    if nums:
                        return int(nums[-1])
        except Exception:
            pass
        return 999

    def _speed_test(self) -> str:
        if not _internet_ok():
            return "Mannan bhai, internet nahi hai toh speed test nahi ho sakta."

        self.speak("Mannan bhai, speed test chal raha hai. Thodi der ruko.")
        try:
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            down = st.download() / 1_000_000
            up   = st.upload()   / 1_000_000
            return (
                f"Mannan bhai, speed test mukammal hua. "
                f"Download speed {down:.1f} megabits per second hai. "
                f"Upload speed {up:.1f} megabits per second hai. "
                + ("Bahut fast hai!" if down > 50 else
                   "Theek speed hai." if down > 10 else
                   "Speed thodi slow hai.")
            )
        except ImportError:
            return (
                "Mannan bhai, speed test ke liye speedtest-cli install karna hoga. "
                "Command chalao: pip install speedtest-cli"
            )
        except Exception as e:
            return f"Mannan bhai, speed test nahi hua. Error: {e}"

    def _ip_address(self) -> str:
        local = socket.gethostbyname(socket.gethostname())
        try:
            import requests
            pub = requests.get("https://api.ipify.org", timeout=3).text
            return f"Mannan bhai, local IP {local} hai aur public IP {pub} hai."
        except Exception:
            return f"Mannan bhai, local IP {local} hai. Public IP nahi mila."

    def _ping(self) -> str:
        ms = self._get_ping()
        quality = "excellent" if ms < 20 else "good" if ms < 60 else "average" if ms < 100 else "poor"
        return f"Mannan bhai, ping {ms} milliseconds hai. Connection {quality} hai."

    def _search(self, query: str) -> str:
        if not _internet_ok():
            return (
                "Mannan bhai, Google search ke liye internet chahiye. "
                "Abhi internet nahi hai."
            )
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))
        return f"Mannan bhai, Google pe '{query}' search kar raha hoon."

    def _open_website(self, url: str) -> str:
        if not _internet_ok():
            return f"Mannan bhai, {url} kholne ke liye internet chahiye. Abhi connected nahi hain."
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Mannan bhai, {url} browser mein khul raha hai."

    # ═══════════════════════════════════════════════════════════════════════════
    # FILE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    FOLDERS = {
        "documents": os.path.expanduser("~/Documents"),
        "downloads": os.path.expanduser("~/Downloads"),
        "desktop":   os.path.expanduser("~/Desktop"),
        "pictures":  os.path.expanduser("~/Pictures"),
        "music":     os.path.expanduser("~/Music"),
        "videos":    os.path.expanduser("~/Videos"),
    }

    def _open_folder(self, name: str) -> str:
        path = self.FOLDERS.get(name.lower())
        if path and os.path.exists(path):
            subprocess.Popen(f'explorer "{path}"')
            return f"Mannan bhai, {name} folder khul raha hai."
        return f"Mannan bhai, {name} folder nahi mila."

    def _create_folder(self, name: str) -> str:
        path = os.path.join(os.path.expanduser("~/Desktop"), name)
        try:
            os.makedirs(path, exist_ok=True)
            return f"Mannan bhai, Desktop pe '{name}' folder bana diya."
        except Exception as e:
            return f"Mannan bhai, folder nahi bana. Error: {e}"

    def _find_file(self, name: str) -> str:
        home  = os.path.expanduser("~")
        found = []
        for root, dirs, files in os.walk(home):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if name.lower() in f.lower():
                    found.append(os.path.join(root, f))
                    if len(found) >= 4:
                        break
            if len(found) >= 4:
                break

        if found:
            paths = ". ".join(found[:4])
            return (
                f"Mannan bhai, {len(found)} file mili '{name}' naam ki. "
                f"Yahan hain: {paths}"
            )
        return f"Mannan bhai, '{name}' naam ki koi file nahi mili aapke system mein."

    def _delete_file(self, name: str) -> str:
        import shutil
        for base in [os.path.expanduser("~/Desktop"),
                     os.path.expanduser("~/Documents"),
                     os.path.expanduser("~/Downloads")]:
            path = os.path.join(base, name)
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    return f"Mannan bhai, '{name}' delete ho gaya."
                except Exception as e:
                    return f"Mannan bhai, delete nahi hua. Error: {e}. Administrator mode mein chalayein."
        return f"Mannan bhai, '{name}' nahi mila delete karne ke liye."

    # ═══════════════════════════════════════════════════════════════════════════
    # RECYCLE BIN — with confirmation
    # ═══════════════════════════════════════════════════════════════════════════

    def _show_recycle_bin(self) -> str:
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "$shell = New-Object -ComObject Shell.Application; "
                 "$bin = $shell.Namespace(0xA); "
                 "$items = $bin.Items(); "
                 "Write-Output $items.Count"],
                capture_output=True, text=True
            )
            count = result.stdout.strip()
            if count == "0" or count == "":
                return "Mannan bhai, Recycle Bin khali hai. Koi file nahi hai iske ander."

            # Open recycle bin explorer
            subprocess.Popen("explorer shell:RecycleBinFolder")
            self._pending_recycle = True
            return (
                f"Mannan bhai, Recycle Bin mein {count} cheezein hain. "
                "Main ne explorer mein khol diya hai dekh lein. "
                "Saaf karna chahte ho? Han bolein toh main saaf kar deta hoon."
            )
        except Exception:
            subprocess.Popen("explorer shell:RecycleBinFolder")
            self._pending_recycle = True
            return (
                "Mannan bhai, Recycle Bin khul gayi hai. Dekh lein kya hai ander. "
                "Saaf karna chahte ho? Han bolein."
            )

    def _ask_empty_recycle_bin(self) -> str:
        self._pending_recycle = True
        return (
            "Mannan bhai, kya aap Recycle Bin saaf karna chahte ho? "
            "Han bolein toh main sab kuch delete kar deta hoon. "
            "Yaad rahe: baad mein wapis nahi aayega."
        )

    def _empty_recycle_bin(self) -> str:
        try:
            subprocess.run(
                ["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                capture_output=True
            )
            return (
                "Mannan bhai, Recycle Bin saaf ho gayi. "
                "Sab deleted files permanently hat gayi hain. "
                "Aage kya karna hai?"
            )
        except Exception as e:
            return f"Mannan bhai, Recycle Bin saaf nahi hui. Error: {e}"

    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════

    def _screenshot(self) -> str:
        import datetime
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.expanduser("~"), "Pictures", f"screenshot_{ts}.png")
        try:
            import pyautogui
            pyautogui.screenshot(path)
            return f"Mannan bhai, screenshot le li. Pictures folder mein save ho gayi screenshot_{ts} ke naam se."
        except ImportError:
            subprocess.Popen("SnippingTool.exe")
            return "Mannan bhai, Snipping Tool khul gaya. Screenshot lein."

    def _lock(self) -> str:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return "Mannan bhai, screen lock ho gayi."

    def _shutdown(self) -> str:
        subprocess.run(["shutdown", "/s", "/t", "30"])
        return (
            "Mannan bhai, computer 30 second mein band ho jayega. "
            "Cancel karna ho toh shutdown cancel bolein."
        )

    def _restart(self) -> str:
        subprocess.run(["shutdown", "/r", "/t", "30"])
        return "Mannan bhai, computer 30 second mein restart hoga."

    def _cancel_shutdown(self) -> str:
        subprocess.run(["shutdown", "/a"])
        return "Mannan bhai, shutdown cancel ho gaya. Computer band nahi hoga."

    # ═══════════════════════════════════════════════════════════════════════════
    # IDLE — asks Mannan bhai what to do
    # ═══════════════════════════════════════════════════════════════════════════

    def _start_idle_checker(self):
        def check():
            while True:
                time.sleep(30)
                idle = time.time() - self._last_cmd_time
                if idle > 45:
                    self._last_cmd_time = time.time()
                    self.speak(
                        "Mannan bhai, main yahan hoon. Kya karna chahte ho? "
                        "Koi app kholni ho, hardware check karna ho, ya kuch aur?"
                    )
        threading.Thread(target=check, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════════════════
    # HELP
    # ═══════════════════════════════════════════════════════════════════════════

    def _help(self) -> str:
        return (
            "Mannan bhai, ye commands use kar sakte ho. "
            "Apps ke liye: open chrome, open notepad, ya koi bhi app ka naam lein — "
            "main system mein dhundh ke khol deta hoon. "
            "Internet ke liye: internet check karo, speed test, ya search kuch bhi. "
            "Hardware ke liye: CPU, RAM, disk, battery, ya poora report bolein. "
            "Files ke liye: documents kholo, folder banao, file dhundo, ya file delete karo. "
            "Recycle Bin ke liye: recycle bin dekho ya saaf karo. "
            "System ke liye: screenshot, screen lock, shutdown, ya restart. "
            "Volume ke liye: volume up, volume down, ya mute. "
            "Aur han — Urdu mein bhi bol sakte ho."
        )

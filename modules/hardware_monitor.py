"""Hardware Monitor — background alerts"""
import psutil, time, logging
logger = logging.getLogger(__name__)

class HardwareMonitor:
    def __init__(self):
        self._alerts = {}

    def get_stats(self):
        bat = psutil.sensors_battery()
        try:
            disk = psutil.disk_usage("C:\\").percent
        except Exception:
            disk = 0
        return {
            "cpu":     psutil.cpu_percent(interval=None),
            "ram":     psutil.virtual_memory().percent,
            "disk":    disk,
            "battery": bat.percent if bat else None,
            "plugged": bat.power_plugged if bat else True,
        }

    def monitor_loop(self, speak_fn, interval=25):
        time.sleep(8)
        while True:
            try:
                s = self.get_stats()
                now = time.time()
                if s["cpu"] > 90 and self._ok("cpu", now, 90):
                    speak_fn(f"Mannan bhai, CPU {s['cpu']:.0f} percent pe hai. Koi bhari app band karein.")
                if s["ram"] > 85 and self._ok("ram", now, 90):
                    speak_fn(f"Mannan bhai, RAM bhari hui hai {s['ram']:.0f} percent. Kuch tabs ya apps band karein.")
                bat = s["battery"]
                if bat and not s["plugged"]:
                    if bat <= 10 and self._ok("bat_c", now, 60):
                        speak_fn(f"Khabardar Mannan bhai! Battery sirf {bat:.0f} percent reh gayi. Abhi charger lagayen!")
                    elif bat <= 20 and self._ok("bat_l", now, 120):
                        speak_fn(f"Mannan bhai, battery {bat:.0f} percent hai. Charger lagayen.")
            except Exception as e:
                logger.error(e)
            time.sleep(interval)

    def _ok(self, key, now, cooldown):
        if now - self._alerts.get(key, 0) >= cooldown:
            self._alerts[key] = now
            return True
        return False

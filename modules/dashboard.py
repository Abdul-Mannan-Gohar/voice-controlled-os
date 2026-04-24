"""
Dashboard GUI — Voice Controlled OS Interface
FYP — University of Kotli AJK
"""

import tkinter as tk
from tkinter import scrolledtext
import threading, time, psutil
from datetime import datetime

BG    = "#0d1117"; PANEL = "#161b22"; BORDER = "#21262d"
BLUE  = "#58a6ff"; GREEN = "#3fb950"; YELLOW = "#d29922"
RED   = "#f85149"; PURPLE= "#bc8cff"; TEXT   = "#e6edf3"; DIM = "#8b949e"
MONO  = ("Consolas", 10); SF = ("Segoe UI", 9)


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice-Controlled Intelligent OS Interface — FYP 2023-2027 | Abdul Mannan Gohar")
        self.geometry("1150x700")
        self.configure(bg=BG)
        self._engine = None
        self._hw_on  = True
        self._build()
        self._hw_loop()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def set_engine(self, e): self._engine = e

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        # Header
        h = tk.Frame(self, bg=BG, pady=10); h.pack(fill="x", padx=18)
        tk.Label(h, text="🎙  VOICE-CONTROLLED INTELLIGENT OS INTERFACE",
                 fg=BLUE, bg=BG, font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(h, text="Abdul Mannan Gohar  |  University of Kotli AJK  |  FYP 2023-2027",
                 fg=DIM, bg=BG, font=SF).pack(side="right")
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=10)
        body.columnconfigure(0, weight=1); body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        self._status_card(left)
        self._hw_card(left)
        self._btns_card(left)
        self._log_card(right)

    def _card(self, p, title, color=BLUE):
        f = tk.Frame(p, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", pady=(0,8))
        tk.Label(f, text=title, fg=color, bg=PANEL,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(8,4))
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=12)
        inn = tk.Frame(f, bg=PANEL); inn.pack(fill="both", padx=12, pady=8)
        return inn

    def _status_card(self, p):
        inn = self._card(p, "▸ STATUS")
        row = tk.Frame(inn, bg=PANEL); row.pack(fill="x")
        self._dot  = tk.Label(row, text="●", fg=RED, bg=PANEL, font=("Segoe UI",16))
        self._dot.pack(side="left")
        self._slbl = tk.Label(row, text="  STARTING…", fg=RED, bg=PANEL,
                              font=("Segoe UI",11,"bold"))
        self._slbl.pack(side="left")
        tk.Label(inn, text="English + Urdu  |  Mannan bhai mode ON",
                 fg=DIM, bg=PANEL, font=SF).pack(anchor="w", pady=(4,0))

    def _hw_card(self, p):
        inn = self._card(p, "▸ HARDWARE MONITOR", GREEN)
        self._hw = {}
        for label, key in [("CPU","cpu"),("RAM","ram"),("DISK","disk"),("BATTERY","bat")]:
            r = tk.Frame(inn, bg=PANEL); r.pack(fill="x", pady=2)
            tk.Label(r, text=f"{label:<8}", fg=DIM, bg=PANEL,
                     font=MONO, width=8, anchor="w").pack(side="left")
            bg2 = tk.Frame(r, bg=BORDER, height=10, width=130)
            bg2.pack(side="left", padx=(0,6)); bg2.pack_propagate(False)
            fill = tk.Frame(bg2, bg=GREEN, height=10)
            fill.place(x=0, y=0, relheight=1, width=0)
            val = tk.Label(r, text="—", fg=TEXT, bg=PANEL, font=MONO)
            val.pack(side="left")
            self._hw[key] = (fill, val)

    def _btns_card(self, p):
        inn = self._card(p, "▸ QUICK COMMANDS", PURPLE)
        cmds = [
            ("CPU Status", "cpu"),
            ("RAM Status", "ram"),
            ("Battery",    "battery"),
            ("Internet",   "internet"),
            ("Speed Test", "speed test"),
            ("Scan Apps",  "scan"),
            ("Recycle Bin","recycle bin"),
            ("Help",       "help"),
        ]
        g = tk.Frame(inn, bg=PANEL); g.pack(fill="x")
        for i, (label, cmd) in enumerate(cmds):
            tk.Button(g, text=label, command=lambda c=cmd: self._run(c),
                      bg=BORDER, fg=TEXT, relief="flat", font=SF,
                      cursor="hand2", padx=6, pady=4, width=14
                      ).grid(row=i//2, column=i%2, padx=3, pady=2, sticky="ew")
        g.columnconfigure(0, weight=1); g.columnconfigure(1, weight=1)

    def _log_card(self, p):
        f = tk.Frame(p, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="both", expand=True)
        h = tk.Frame(f, bg=PANEL); h.pack(fill="x", padx=12, pady=(8,4))
        tk.Label(h, text="▸ CONVERSATION LOG", fg=BLUE, bg=PANEL,
                 font=("Segoe UI",9,"bold")).pack(side="left")
        tk.Button(h, text="Clear", command=self._clear,
                  bg=BORDER, fg=DIM, relief="flat", font=SF, cursor="hand2").pack(side="right")
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=12)
        self._log = scrolledtext.ScrolledText(
            f, bg=BG, fg=TEXT, font=MONO, relief="flat", wrap="word", state="disabled")
        self._log.pack(fill="both", expand=True, padx=4, pady=4)
        self._log.tag_config("ts",       foreground=DIM)
        self._log.tag_config("heard",    foreground=TEXT)
        self._log.tag_config("response", foreground=GREEN)
        self._log.tag_config("system",   foreground=BLUE)
        self._log.tag_config("warning",  foreground=YELLOW)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_status(self, s):
        self.after(0, self._upd_status, s)

    def add_log(self, text, is_resp):
        tag = "response" if is_resp else "heard"
        pre = "SYSTEM" if is_resp else "HEARD"
        self.after(0, self._write, pre, text, tag)

    def add_response(self, text):
        self.after(0, self._write, "RESPONSE", text, "response")

    def run(self): self.mainloop()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _upd_status(self, s):
        c = {
            "idle":        (BLUE,   "IDLE — Listening"),
            "listening":   (GREEN,  "🎙  LISTENING…"),
            "processing":  (YELLOW, "⚙  PROCESSING…"),
            "executing":   (YELLOW, "▶  EXECUTING…"),
            "calibrating": (PURPLE, "CALIBRATING MIC…"),
            "offline":     (RED,    "OFFLINE"),
        }.get(s, (DIM, s.upper()))
        self._dot.config(fg=c[0])
        self._slbl.config(fg=c[0], text=f"  {c[1]}")

    def _write(self, prefix, text, tag):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log.config(state="normal")
        self._log.insert("end", f"[{ts}] ", "ts")
        self._log.insert("end", f"[{prefix}] ", tag)
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.config(state="disabled")

    def _clear(self):
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.config(state="disabled")

    def _run(self, cmd):
        if self._engine:
            self._write("BUTTON", cmd, "system")
            def go():
                r = self._engine.router.route(cmd)
                if r: self._engine.speak(r)
            threading.Thread(target=go, daemon=True).start()

    def _hw_loop(self):
        def loop():
            while self._hw_on:
                self.after(0, self._refresh_hw)
                time.sleep(2)
        threading.Thread(target=loop, daemon=True).start()

    def _refresh_hw(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            bat = psutil.sensors_battery()
            bat_pct = bat.percent if bat else 0
            try:    disk = psutil.disk_usage("C:\\").percent
            except: disk = 0
            for key, val in [("cpu",cpu),("ram",mem),("disk",disk),("bat",bat_pct)]:
                fill, lbl = self._hw[key]
                w = int(130 * val / 100)
                c = GREEN if val < 70 else (YELLOW if val < 85 else RED)
                fill.config(bg=c); fill.place(x=0, y=0, relheight=1, width=w)
                sfx = "%" + (" ⚡" if key=="bat" and bat and bat.power_plugged else "%")[1:]
                lbl.config(text=f"{val:.0f}%", fg=c)
        except Exception: pass

    def _close(self):
        self._hw_on = False
        if self._engine: self._engine.stop()
        self.destroy()

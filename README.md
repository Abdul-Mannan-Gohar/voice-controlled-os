# 🎙️ Voice-Controlled Intelligent Operating System Interface

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![FYP](https://img.shields.io/badge/FYP-2023--2027-purple?style=for-the-badge)

**Final Year Project — University of Kotli AJK**

Abdul Mannan Gohar | Rizwan Liaqat | Nadeem Naeem

**Supervisor:** Saima Jawad

</div>

---

## 📌 Project Overview

A real-time **Voice-Controlled Intelligent Operating System Interface** built in Python that allows users to control their Windows PC entirely through spoken commands in **English and Urdu**. The system automatically detects all installed applications, monitors hardware, manages files, and provides intelligent voice feedback for every single action.

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 🔍 **Auto App Detection** | Scans Windows Registry + Start Menu — no hardcoded paths needed |
| 🗣️ **Continuous Voice Feedback** | Speaks result of every command (success AND failure with reason) |
| 🧠 **Intelligent Decision Making** | Checks app exists before opening, checks internet before web commands |
| 🌐 **Internet Awareness** | Connection check, speed test, WiFi name, IP address |
| 💻 **Hardware Monitoring** | CPU, RAM, Disk, Battery with automatic verbal alerts |
| 📁 **File Management** | Open folders, create/find/delete files, manage Recycle Bin |
| ⚡ **Error Explanation** | When something fails — explains WHY and HOW to fix it by voice |
| 🔔 **Idle Prompting** | Asks what to do next after 40 seconds of inactivity |
| 🇵🇰 **Urdu Support** | Understands Roman Urdu commands alongside English |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   main.py (Launcher)                │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   Dashboard (GUI)   │  ← Tkinter dark theme UI
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   Voice Engine      │  ← Continuous mic listening
    │   (voice_engine.py) │  ← Google Speech Recognition
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   Command Router    │  ← Intelligent dispatcher (50+ patterns)
    │  (command_router.py)│  ← English + Urdu
    └────┬──────┬─────────┘
         │      │
   ┌─────▼──┐ ┌─▼──────────────────┐
   │  App   │ │     Modules        │
   │Scanner │ │  • hardware_monitor│
   │        │ │  • internet check  │
   └────────┘ │  • file manager    │
              │  • system control  │
              └────────────────────┘
```

---

## 📁 Project Structure

```
fyp_voice_os/
│
├── main.py                      ← Entry point — run this file
├── requirements.txt             ← All Python dependencies
├── README.md                    ← This file
├── app_cache.json               ← Auto-generated app database (created on first run)
├── fyp_voice_os.log             ← Runtime logs
│
└── modules/
    ├── __init__.py
    ├── app_scanner.py           ← Auto-detects ALL installed apps from Registry
    ├── command_router.py        ← Routes voice commands to actions (intelligent)
    ├── voice_engine.py          ← Microphone input + Text-to-Speech output
    ├── hardware_monitor.py      ← CPU/RAM/Battery monitoring + auto alerts
    └── dashboard.py             ← GUI (Tkinter dark theme)
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Windows 10 or Windows 11
- Python 3.11 or higher — [Download here](https://python.org)
- Working microphone
- Internet connection (for speech recognition)

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/fyp-voice-os.git
cd fyp-voice-os
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ If `pyaudio` fails on Windows:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### Step 3 — Run
```bash
python main.py
```

On first run the system will:
1. Scan all installed apps (~10 seconds)
2. Calibrate your microphone
3. Say **"Voice controlled OS interface is ready"**
4. Start listening continuously

---

## 🗣️ Voice Commands

### 📱 App Control
| Command | Action |
|---|---|
| `open chrome` | Scans system, finds Chrome, opens it |
| `open notepad` | Opens Notepad |
| `open discord` | Finds and opens Discord |
| `close notepad` | Closes the Notepad process |
| `kholo calculator` | Opens Calculator (Urdu) |
| `rescan apps` | Re-scans for newly installed apps |

> ✅ **App found:** *"Mannan bhai, Chrome mil gaya. Main open kar raha hoon."*
> ✅ **App opened:** *"Chrome khul gaya. Aage kya karna hai?"*
> ❌ **App not found:** *"Aapke laptop mein yeh nahi mila. Pehle install karein."*

---

### 🔊 Volume Control
| Command | Action |
|---|---|
| `volume up` | Increase volume |
| `volume down` | Decrease volume |
| `mute` | Mute system audio |
| `unmute` | Unmute system audio |
| `set volume 70` | Set volume to exact 70% |

---

### 💻 Hardware Monitoring
| Command | Example Response |
|---|---|
| `cpu` | *"CPU 23% use ho raha hai, 1800 MHz pe, 6 physical cores hain"* |
| `ram` | *"RAM 65% — 4.8 GB use mein, 2.6 GB free hai"* |
| `disk` | *"Drive C: 72% bhara hua, 45 GB free hai"* |
| `battery` | *"Battery 54% hai aur charging ho rahi hai"* |
| `temperature` | CPU temperature reading |
| `system report` | Full summary of all hardware |

> 🔔 **Automatic Alerts:** If CPU exceeds 90% or battery drops below 20%, system speaks an alert automatically!

---

### 🌐 Internet & Network
| Command | Example Response |
|---|---|
| `am i connected` | *"Ji, 'Jazz WiFi' se connected hain"* |
| `wifi name` | *"Aap 'HomeNetwork' se connected hain"* |
| `speed test` | *"Download 45 Mbps, Upload 12 Mbps, Ping 18ms"* |
| `my ip` | *"Local IP 192.168.1.5, Public IP 103.x.x.x"* |
| `search python tutorial` | Opens Google in browser |
| `open youtube.com` | Opens website directly |

---

### 📁 File Management
| Command | Action |
|---|---|
| `open documents` | Opens Documents folder in Explorer |
| `open downloads` | Opens Downloads folder |
| `create folder projects` | Creates folder on Desktop |
| `find file report` | Searches Desktop/Documents/Downloads |
| `delete file old.txt` | Deletes file with confirmation |
| `open recycle bin` | Opens Recycle Bin |
| `empty recycle bin` | Shows item count, asks confirmation, then clears |

---

### ⚙️ System Commands
| Command | Action |
|---|---|
| `screenshot` | Saves PNG to Pictures folder with timestamp |
| `lock screen` | Locks the workstation |
| `shutdown` | Shuts down in 30 seconds |
| `restart` | Restarts in 30 seconds |
| `cancel shutdown` | Cancels pending shutdown |
| `help` | Lists all available commands by voice |

---

## 🔧 How App Auto-Detection Works

On first launch, the system scans:

```
Windows Registry
    ├── HKEY_LOCAL_MACHINE\SOFTWARE\...\Uninstall   (64-bit apps)
    ├── HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\... (32-bit apps)
    └── HKEY_CURRENT_USER\SOFTWARE\...\Uninstall    (user-installed apps)

Start Menu Shortcuts
    ├── %APPDATA%\Microsoft\Windows\Start Menu\Programs
    └── C:\ProgramData\Microsoft\Windows\Start Menu\Programs

Known Locations (20+ paths)
    ├── Chrome, Firefox, Edge
    ├── Discord, Spotify, Telegram, WhatsApp
    ├── VS Code, Office Suite, VLC
    └── + more

Windows Built-ins
    ├── Notepad, Calculator, Paint, Explorer
    ├── CMD, PowerShell, Task Manager
    └── Settings, Control Panel, etc.

Result: app_cache.json with 500–1500 apps depending on system
```

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core language |
| SpeechRecognition | 3.10+ | Google Speech API |
| pyttsx3 | 2.90+ | Text-to-speech (offline) |
| PyAudio | 0.2.14+ | Microphone input |
| psutil | 5.9+ | Hardware stats |
| pywin32 | 306+ | Windows Registry + window control |
| Tkinter | built-in | GUI Dashboard |
| winreg | built-in | App scanning |

---

## 👥 Team

| Name | Role |
|---|---|
| **Abdul Mannan Gohar** | Lead Developer |
| **Rizwan Liaqat** | Co-Developer |
| **Nadeem Naeem** | Co-Developer |

**Supervisor:** Saima Jawad
**Institution:** University of Kotli AJK
**Session:** 2023–2027

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.

---

## 🙏 Acknowledgements

- University of Kotli AJK for FYP support
- Google Speech Recognition API
- Python open source community

"""
EXE Builder Script
Run this to create a standalone .exe file:
    python build_exe.py

Output will be in: dist/VoiceOS/VoiceOS.exe
"""

import subprocess
import sys
import os

print("=" * 55)
print("  FYP Voice OS — EXE Builder")
print("=" * 55)

# Step 1: Install PyInstaller
print("\n[1/3] Installing PyInstaller...")
subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

# Step 2: Build EXE
print("\n[2/3] Building EXE (this takes 2-5 minutes)...")
cmd = [
    "pyinstaller",
    "--noconfirm",
    "--onedir",              # folder with exe (faster startup than --onefile)
    "--windowed",            # no black console window
    "--name", "VoiceOS",
    "--add-data", "modules;modules",
    "--hidden-import", "speech_recognition",
    "--hidden-import", "pyttsx3",
    "--hidden-import", "pyttsx3.drivers",
    "--hidden-import", "pyttsx3.drivers.sapi5",
    "--hidden-import", "psutil",
    "--hidden-import", "pyaudio",
    "--hidden-import", "winreg",
    "--hidden-import", "win32gui",
    "--hidden-import", "win32con",
    "--hidden-import", "comtypes",
    "--hidden-import", "comtypes.client",
    "main.py"
]

result = subprocess.run(cmd)

if result.returncode == 0:
    exe_path = os.path.abspath(os.path.join("dist", "VoiceOS", "VoiceOS.exe"))
    print("\n[3/3] SUCCESS!")
    print(f"\n✅ EXE created at:\n   {exe_path}")
    print("\nShare the entire 'dist/VoiceOS/' folder — not just the .exe file.")
    print("Users just double-click VoiceOS.exe to run it.")
else:
    print("\n❌ Build failed. Try these fixes:")
    print("   pip install pyinstaller --upgrade")
    print("   Make sure all packages in requirements.txt are installed")

input("\nPress Enter to close...")

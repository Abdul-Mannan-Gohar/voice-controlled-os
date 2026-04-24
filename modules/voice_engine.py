"""
Voice Engine — Continuous listening, non-blocking TTS
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import logging
from modules.command_router  import CommandRouter
from modules.hardware_monitor import HardwareMonitor
from modules.app_scanner     import AppScanner

logger = logging.getLogger(__name__)


class VoiceEngine:
    def __init__(self, on_status=None, on_transcript=None, on_response=None):
        self.on_status    = on_status
        self.on_transcript = on_transcript
        self.on_response  = on_response
        self.running      = False

        # Recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold          = 0.7
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold         = 300
        self.mic = sr.Microphone()

        # TTS
        self._tts = pyttsx3.init()
        self._tts.setProperty("rate", 155)
        self._tts.setProperty("volume", 1.0)
        voices = self._tts.getProperty("voices")
        if voices:
            self._tts.setProperty("voice", voices[0].id)
        self._tts_lock = threading.Lock()

        # Subsystems
        self.hw_monitor  = HardwareMonitor()
        self.app_scanner = AppScanner()

        self.router = CommandRouter(
            speak_fn    = self.speak,
            hw_monitor  = self.hw_monitor,
            app_scanner = self.app_scanner,
        )

        self._calibrate()

    # ── TTS ───────────────────────────────────────────────────────────────────

    def speak(self, text: str):
        logger.info(f"Speaking: {text}")
        if self.on_response:
            self.on_response(text)
        def _run():
            with self._tts_lock:
                self._tts.say(text)
                self._tts.runAndWait()
        threading.Thread(target=_run, daemon=True).start()
        time.sleep(0.4)

    # ── Mic ───────────────────────────────────────────────────────────────────

    def _calibrate(self):
        self._set_status("calibrating")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info("Mic calibrated.")

    def _listen(self) -> str | None:
        with self.mic as source:
            self._set_status("listening")
            try:
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=12)
            except sr.WaitTimeoutError:
                self._set_status("idle")
                return None
        self._set_status("processing")
        try:
            text = self.recognizer.recognize_google(audio).lower()
            if self.on_transcript:
                self.on_transcript(text, False)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            self.speak("Internet nahi hai, speech recognition kaam nahi kar raha.")
            return None
        finally:
            self._set_status("idle")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        self.running = True
        self._set_status("idle")

        # Start hardware alert loop
        threading.Thread(
            target=self.hw_monitor.monitor_loop,
            args=(self.speak,),
            daemon=True
        ).start()

        self.speak(
            "Mannan bhai, Voice Controlled Intelligent Operating System ready hai. "
        )

        while self.running:
            text = self._listen()
            if not text:
                continue

            self._set_status("executing")
            try:
                response = self.router.route(text)
                if response:
                    if self.on_transcript:
                        self.on_transcript(response, True)
                    self.speak(response)
            except Exception as e:
                err = f"Mannan bhai, koi error aayi: {str(e)}"
                logger.error(err)
                self.speak(err)
            finally:
                self._set_status("idle")

    def stop(self):
        self.running = False
        self._set_status("offline")

    def _set_status(self, s):
        if self.on_status:
            self.on_status(s)

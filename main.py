"""
VOICE-CONTROLLED INTELLIGENT OPERATING SYSTEM INTERFACE
FYP — Abdul Mannan Gohar | University of Kotli AJK | 2023-2027

Run: python main.py
"""

import logging
import threading
from modules.voice_engine import VoiceEngine
from modules.dashboard    import Dashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("voice_os.log"),
        logging.StreamHandler()
    ]
)

def main():
    print("=" * 60)
    print("  VOICE-CONTROLLED INTELLIGENT OS INTERFACE")
    print("  Abdul Mannan Gohar | University of Kotli AJK")
    print("  FYP Session 2023-2027")
    print("=" * 60)

    dashboard = Dashboard()

    engine = VoiceEngine(
        on_status     = dashboard.set_status,
        on_transcript = dashboard.add_log,
        on_response   = dashboard.add_response,
    )

    dashboard.set_engine(engine)

    # Voice engine in background
    threading.Thread(target=engine.run, daemon=True).start()

    # GUI on main thread
    dashboard.run()

    engine.stop()
    print("System stopped. Goodbye Mannan bhai!")


if __name__ == "__main__":
    main()

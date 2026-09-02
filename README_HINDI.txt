MANJEET TTS - MP3 VERSION
==========================

FEATURES
- Hindi Female voice
- Hindi Male voice
- Normal / Heavy / Thin
- Tone control
- Speed control
- MP3 generation
- MP3 download
- Works in browser on computer
- Can be opened on iPhone/Android when the phone and computer are on the same Wi-Fi

IMPORTANT
This version uses the edge-tts Python package, which accesses Microsoft's online
Edge TTS service. Internet is required when generating audio. No API key is
needed by edge-tts, but service availability can change.

WINDOWS 7 SETUP
1. Install Python 3.8.10 (32-bit or 64-bit matching your Windows).
2. Put this whole folder somewhere easy, e.g. Desktop\Manjeet_TTS_MP3
3. Double-click install.bat.
4. When installation finishes, double-click start.bat.
5. On the computer open:
   http://127.0.0.1:5000

PHONE
1. Keep the Python server running on the computer.
2. Connect iPhone/Android and computer to the same Wi-Fi.
3. Find the computer's local IP:
   Start -> Run -> cmd -> ipconfig
4. Look for IPv4 Address, e.g. 192.168.1.5
5. On the phone open:
   http://192.168.1.5:5000

If Windows Firewall asks for permission for Python, allow it on the Private/Home
network. Do NOT expose this local server directly to the public internet.

VOICE SETTINGS
Female = hi-IN-SwaraNeural
Male   = hi-IN-MadhurNeural
Heavy lowers pitch.
Thin raises pitch.
Speed changes speaking rate.

LIMIT
The demo accepts up to 12,000 characters per generation. For very long scripts,
generate in smaller parts.

LICENSE / SERVICE NOTE
The app code in this package is your local project code. The TTS engine is the
third-party edge-tts package and Microsoft online TTS service; their respective
terms/licenses apply.

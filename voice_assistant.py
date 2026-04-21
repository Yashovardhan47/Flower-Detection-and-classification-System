import os
import threading

import requests
import speech_recognition as sr

from utils import get_info   # used by process_voice_flower

# ── Speech recogniser (stateless — safe to share) ────────────────────────────
recognizer = sr.Recognizer()
recognizer.energy_threshold         = 200   # pick up quiet speech
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold          = 0.9   # seconds of silence → end of phrase
recognizer.non_speaking_duration    = 0.5

# ── TTS singleton ─────────────────────────────────────────────────────────────
_engine      = None
_engine_lock = threading.Lock()
_tts_ok      = True   # permanently False after first init failure


def _get_engine():
    global _engine, _tts_ok
    if not _tts_ok:
        return None
    if _engine is None:
        try:
            import pyttsx3
            _engine = pyttsx3.init()
            _engine.setProperty("rate",   150)
            _engine.setProperty("volume", 1.0)
            # Prefer an English voice
            voices = _engine.getProperty("voices")
            if voices:
                for v in voices:
                    lang = (v.languages[0] if v.languages else "")
                    if "en" in str(lang).lower() or "english" in v.name.lower():
                        _engine.setProperty("voice", v.id)
                        break
            print("✅ pyttsx3 TTS initialised")
        except Exception as exc:
            print(f"⚠️  pyttsx3 unavailable ({exc}) — text-only mode")
            _tts_ok = False
            return None
    return _engine


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def speak(text: str) -> None:
    """
    Speak *text* aloud via pyttsx3. Thread-safe. Never raises. Always prints.
    Runs in the calling thread — wrap in a daemon thread for non-blocking use.
    """
    print(f"🔊 {text}")
    with _engine_lock:
        engine = _get_engine()
        if engine is None:
            return
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError as exc:
            global _engine
            print(f"⚠️  TTS RuntimeError ({exc}) — reinitialising")
            try:
                _engine = None
                e2 = _get_engine()
                if e2:
                    e2.say(text)
                    e2.runAndWait()
            except Exception as exc2:
                print(f"⚠️  TTS retry failed ({exc2})")
        except Exception as exc:
            print(f"⚠️  TTS non-fatal: {exc}")


def speak_async(text: str) -> None:
    """
    Fire-and-forget version of speak(). Runs in a daemon thread.
    Use this from FastAPI routes so the response is never delayed by TTS.
    """
    t = threading.Thread(target=speak, args=(text,), daemon=True)
    t.start()


def listen_command(timeout: int = 10, phrase_limit: int = 8) -> str:
    """
    Listen on the best available microphone and return recognised text (lower-case).

    Returns sentinel strings on failure:
        'timeout' – no speech detected
        'unknown' – heard audio but not understood
        'error'   – hardware or API problem
    """
    # Build mic candidate list: system default first, then all named devices
    mic_indices = [None]
    try:
        names = sr.Microphone.list_microphone_names()
        mic_indices += list(range(len(names)))
    except Exception:
        pass

    for idx in mic_indices:
        try:
            mic = sr.Microphone(device_index=idx) if idx is not None else sr.Microphone()
            label = f"device {idx}" if idx is not None else "default"

            with mic as source:
                print(f"🎤 Mic: {label} — adjusting for ambient noise…")
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                print("🎤 Ready — speak now")
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit,
                )

            text = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            print(f"🗣  Recognised: {text!r}")
            return text

        except sr.WaitTimeoutError:
            print("⏱  No speech within timeout")
            return "timeout"

        except sr.UnknownValueError:
            print("❓  Speech not understood")
            return "unknown"

        except sr.RequestError as exc:
            print(f"❌  Google Speech API error: {exc}")
            return "error"

        except OSError as exc:
            # PyAudio could not open this device — try next
            print(f"⚠️  Mic {label} failed ({exc}) — trying next device…")
            continue

        except Exception as exc:
            print(f"❌  listen_command unexpected: {exc}")
            return "error"

    print("❌  No working microphone found")
    return "error"


def get_flower_images(query: str, n: int = 3) -> list:
    """
    Return up to *n* Unsplash image URLs for *query*.
    Reads UNSPLASH_KEY from environment at call time.
    Falls back to placeholder URLs on any error.
    """
    key = os.getenv("UNSPLASH_KEY", "")
    if not key:
        print("⚠️  UNSPLASH_KEY missing — placeholders used")
        return [f"https://via.placeholder.com/400x300?text={query.replace(' ', '+')}"]

    # Use only the common name for a better search
    search_query = query.split("(")[0].strip()

    try:
        res = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query":       search_query,
                "per_page":    n,
                "orientation": "landscape",
            },
            headers={
                "Authorization":  f"Client-ID {key}",
                "Accept-Version": "v1",
            },
            timeout=8,
        )
        if res.status_code == 200:
            results = res.json().get("results", [])
            urls    = [img["urls"]["regular"] for img in results if img.get("urls")]
            if urls:
                return urls
        print(f"⚠️  Unsplash {res.status_code}")
    except Exception as exc:
        print(f"❌ get_flower_images: {exc}")

    return [f"https://via.placeholder.com/400x300?text={search_query.replace(' ', '+')}"]


def process_voice_flower() -> dict:
    """
    Full pipeline: listen → info + images → speak summary.
    Returns {name, info, images}.
    """
    command = listen_command()

    _errors = {
        "timeout": "I didn't hear anything. Please try again.",
        "unknown": "I couldn't understand that. Please speak clearly.",
        "error":   "Microphone error. Please check your mic and try again.",
    }
    if command in _errors:
        msg = _errors[command]
        speak(msg)
        return {
            "name":   "None",
            "info":   msg,
            "images": ["https://via.placeholder.com/400x300?text=No+Input"],
        }

    flower_name = command.strip()
    info        = get_info(flower_name)
    images      = get_flower_images(flower_name)

    if info == "No info found":
        speak(f"Sorry, I couldn't find information about {flower_name}.")
    else:
        first = info.split(".")[0].strip()
        speak(f"{flower_name}. {first}.")

    return {"name": flower_name, "info": info, "images": images}

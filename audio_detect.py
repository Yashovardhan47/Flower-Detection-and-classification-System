# """
# audio_detect.py
# ---------------
# Microphone-based flower detection pipeline consumed by backend.py (/voice-detect).

# Fix: /voice-detect now accepts an optional `flower_name` query param.
# When the browser Web Speech API has already recognised the flower name,
# it passes it directly — we skip the server-side mic listen entirely.
# When no name is provided we fall back to listening on the server mic.
# """

# from voice_assistant import listen_command, get_flower_images, speak
# from utils import get_info


# def process_audio_flower(flower_name: str = "") -> dict:
#     """
#     1. If `flower_name` is provided (from browser speech recognition), use it.
#        Otherwise listen on the server microphone.
#     2. Fetch Wikipedia info + Unsplash images for that name.
#     3. Speak a brief summary aloud.
#     4. Return {'name', 'info', 'images'}.
#     """

   
#     if flower_name:
#         # Name came from the browser — use it directly
#         print(f"🎤 Browser-supplied flower name: {flower_name!r}")
#         text = flower_name.lower().strip()
#     else:
#         # Fall back to server-side mic listen
#         text = listen_command(timeout=10, phrase_limit=8)

  
#     _errors = {
#         "timeout": "I didn't hear anything. Please try again.",
#         "unknown": "I couldn't understand that. Please speak clearly.",
#         "error":   "There was a microphone error. Please check your mic.",
#     }
#     if text in _errors:
#         msg = _errors[text]
#         speak(msg)
#         return {
#             "name":   "None",
#             "info":   msg,
#             "images": ["https://via.placeholder.com/400x300?text=No+Audio"],
#         }

#     name   = text.strip()
#     info   = get_info(name)
#     images = get_flower_images(name, n=3)

#     if info == "No info found":
#         speak(f"Sorry, I couldn't find information about {name}.")
#     else:
#         first_sentence = info.split(".")[0].strip()
#         speak(f"{name}. {first_sentence}.")

#     return {
#         "name":   name,
#         "info":   info,
#         "images": images,
#     }


# audio_detect.py
# ---------------
# Microphone-based flower detection pipeline consumed by backend.py (/voice-detect).

# When `flower_name` is provided (from browser Web Speech API), server-side
# mic listening is skipped and we go directly to info + image lookup.
# When `flower_name` is empty, the server listens on its own microphone.

# """
# audio_detect.py
# ---------------
# Microphone-based flower detection pipeline consumed by backend.py (/voice-detect).

# Fix: /voice-detect now accepts an optional `flower_name` query param.
# When the browser Web Speech API has already recognised the flower name,
# it passes it directly — we skip the server-side mic listen entirely.
# When no name is provided we fall back to listening on the server mic.
# """

# from voice_assistant import listen_command, get_flower_images, speak
# from utils import get_info


# def process_audio_flower(flower_name: str = "") -> dict:
#     """
#     1. If `flower_name` is provided (from browser speech recognition), use it.
#        Otherwise listen on the server microphone.
#     2. Fetch Wikipedia info + Unsplash images for that name.
#     3. Speak a brief summary aloud.
#     4. Return {'name', 'info', 'images'}.
#     """

   
#     if flower_name:
#         # Name came from the browser — use it directly
#         print(f"🎤 Browser-supplied flower name: {flower_name!r}")
#         text = flower_name.lower().strip()
#     else:
#         # Fall back to server-side mic listen
#         text = listen_command(timeout=10, phrase_limit=8)

  
#     _errors = {
#         "timeout": "I didn't hear anything. Please try again.",
#         "unknown": "I couldn't understand that. Please speak clearly.",
#         "error":   "There was a microphone error. Please check your mic.",
#     }
#     if text in _errors:
#         msg = _errors[text]
#         speak(msg)
#         return {
#             "name":   "None",
#             "info":   msg,
#             "images": ["https://via.placeholder.com/400x300?text=No+Audio"],
#         }

#     name   = text.strip()
#     info   = get_info(name)
#     images = get_flower_images(name, n=3)

#     if info == "No info found":
#         speak(f"Sorry, I couldn't find information about {name}.")
#     else:
#         first_sentence = info.split(".")[0].strip()
#         speak(f"{name}. {first_sentence}.")

#     return {
#         "name":   name,
#         "info":   info,
#         "images": images,
#     }


# audio_detect.py
# ---------------
# Microphone-based flower detection pipeline consumed by backend.py (/voice-detect).

# When `flower_name` is provided (from browser Web Speech API), server-side
# mic listening is skipped and we go directly to info + image lookup.
# When `flower_name` is empty, the server listens on its own microphone.


from voice_assistant import listen_command, get_flower_images, speak, speak_async
from utils import get_info


def process_audio_flower(flower_name: str = "") -> dict:
    """
    1. Use provided flower_name (from browser speech) OR listen on server mic.
    2. Fetch Wikipedia info + Unsplash images.
    3. Speak a brief summary (async — non-blocking).
    4. Return {name, info, images}.
    """

    # ── Step 1: resolve the flower name ──────────────────────────────────────
    if flower_name:
        print(f"🎤 Browser-supplied name: {flower_name!r}")
        text = flower_name.lower().strip()
    else:
        text = listen_command(timeout=10, phrase_limit=8)

    # ── Handle mic failures ───────────────────────────────────────────────────
    _errors = {
        "timeout": "I didn't hear anything. Please try again.",
        "unknown": "I couldn't understand that. Please speak clearly.",
        "error":   "Microphone error — please check your mic and try again.",
    }
    if text in _errors:
        msg = _errors[text]
        speak_async(msg)
        return {
            "name":   "None",
            "info":   msg,
            "images": ["https://via.placeholder.com/400x300?text=No+Audio"],
        }

    # ── Happy path ───────────────────────────────────────────────────────────
    name   = text.strip()
    info   = get_info(name)
    images = get_flower_images(name, n=3)

    if info == "No info found":
        speak_async(f"Sorry, I couldn't find information about {name}.")
    else:
        first = info.split(".")[0].strip()
        speak_async(f"{name}. {first}.")

    return {"name": name, "info": info, "images": images}
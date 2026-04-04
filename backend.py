"""
backend.py
----------
FastAPI backend — Flower Classification System v4.

Start:  uvicorn backend:app --host 0.0.0.0 --port 8000 --reload

What's fixed:
  - /detect returns structured flower info (not raw Wikipedia dump)
  - Builds a rich `info` string with botanical facts clearly labelled
  - `info_structured` dict also returned for frontend to use by section
  - Irrelevant Wikipedia content filtered via updated utils.get_info()
"""

import asyncio
import hashlib
import os
import re
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import cv2
import numpy as np
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

UNSPLASH_KEY = os.getenv("UNSPLASH_KEY", "")

# ── YOLO ──────────────────────────────────────────────────────────────────────
try:
    from ultralytics import YOLO
    _model = YOLO("yolov8n.pt")
    print("✅ YOLO model loaded")
except Exception as _exc:
    print(f"⚠️  YOLO not loaded: {_exc}")
    _model = None

from audio_detect import process_audio_flower          # noqa: E402
from utils import get_info, identify_plant             # noqa: E402
from voice_assistant import speak_async, get_flower_images  # noqa: E402

_pool = ThreadPoolExecutor(max_workers=6)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Flower Classification System", version="4.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ────────────────────────────────────────────────────────────────────
API_DELAY   = 2
MAX_HISTORY = 25

# ── State ─────────────────────────────────────────────────────────────────────
_last_result   = {"name": "Waiting", "confidence": 0, "info": "No detection yet.", "images": []}
_last_api_call = 0.0
_last_img_hash = ""
recognized_history   = []
unrecognized_history = []


# ── Helpers ───────────────────────────────────────────────────────────────────
def _placeholder(label="flower"):
    return [f"https://via.placeholder.com/400x300?text={label.replace(' ', '+')}"]


def _fetch_images(query, n=3):
    if not UNSPLASH_KEY:
        return _placeholder(query)
    search = query.split("(")[0].strip()
    try:
        res = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": search + " flower", "per_page": n, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}", "Accept-Version": "v1"},
            timeout=8,
        )
        if res.status_code == 200:
            urls = [img["urls"]["regular"] for img in res.json().get("results", []) if img.get("urls")]
            if urls:
                return urls
    except Exception as exc:
        print(f"⚠️  Unsplash: {exc}")
    return _placeholder(search)


def _push(lst, item):
    lst.insert(0, item)
    if len(lst) > MAX_HISTORY:
        lst.pop()


def _build_flower_info(name: str, raw_info: str, confidence: float) -> dict:
    """
    Build a structured info dict from the raw Wikipedia extract.
    Returns:
        info        – clean paragraph for display (botanical facts only)
        info_sections – dict with labelled sections for rich display
    """
    common = name.split("(")[0].strip() if "(" in name else name
    sci    = re.search(r"\(([^)]+)\)", name)
    sci    = sci.group(1) if sci else ""

    if not raw_info or raw_info == "No info found":
        return {
            "info": f"{common} is a flowering plant detected by the AI system. Wikipedia information is not available for this species.",
            "info_sections": {
                "Overview": f"Detected flower: {common}" + (f" ({sci})" if sci else ""),
                "Note": "Detailed botanical information not available. Try searching Wikipedia directly.",
            }
        }

    # ── Split info into sentences and group by topic ──────────────────────────
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_info) if s.strip()]

    # First 2 sentences → Overview
    overview  = " ".join(sentences[:2]) if sentences else ""
    # Middle sentences → Details
    details   = " ".join(sentences[2:6]) if len(sentences) > 2 else ""
    # Remaining → Additional facts
    extra     = " ".join(sentences[6:]) if len(sentences) > 6 else ""

    sections = {}
    if overview:
        sections["Overview"] = overview
    if details:
        sections["Botanical Details"] = details
    if extra:
        sections["Additional Facts"] = extra

    # Add confidence note
    if confidence > 0:
        sections["AI Detection"] = (
            f"Identified as {common}" +
            (f" ({sci})" if sci else "") +
            f" with {confidence:.1f}% confidence by PlantNet AI."
        )

    # Clean full info string — this is what gets displayed in the details box
    clean_info = raw_info  # already filtered by utils.get_info()

    return {
        "info": clean_info,
        "info_sections": sections,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "🌸 Flower Classification System", "version": "4.0.0"}


@app.get("/status")
def status():
    return {
        "status":           "running",
        "yolo_loaded":      _model is not None,
        "plantnet_key_set": bool(os.getenv("PLANTNET_API_KEY")),
        "unsplash_key_set": bool(UNSPLASH_KEY),
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    global _last_api_call, _last_result, _last_img_hash

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")

        # Decode image
        np_arr = np.frombuffer(contents, np.uint8)
        frame  = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return {
                "name": "Invalid image", "confidence": 0,
                "info": "Could not decode the image. Please upload a clear JPEG or PNG photo.",
                "info_sections": {},
                "images": _placeholder("invalid"),
            }

        loop = asyncio.get_event_loop()

        # YOLO annotation (visual only — not used as gate)
        if _model is not None:
            try:
                await loop.run_in_executor(_pool, lambda: _model(frame, verbose=False))
            except Exception as e:
                print(f"⚠️  YOLO skipped: {e}")

        # Rate-limit + deduplicate by image hash
        img_hash = hashlib.md5(contents[:4096]).hexdigest()
        now      = time.time()
        same     = (img_hash == _last_img_hash) and (now - _last_api_call < API_DELAY)

        if not same:
            _last_api_call = now
            _last_img_hash = img_hash

            print(f"🌿 Sending to PlantNet ({len(contents)//1024} KB)…")
            name, confidence = await loop.run_in_executor(_pool, identify_plant, contents)
            print(f"🌿 PlantNet: {name!r} {confidence:.2%}")

            if name != "Unknown":
                # Fetch Wikipedia info and Unsplash images concurrently
                raw_info, images = await asyncio.gather(
                    loop.run_in_executor(_pool, get_info, name),
                    loop.run_in_executor(_pool, _fetch_images, name),
                )

                structured = _build_flower_info(name, raw_info, confidence * 100)

                _last_result = {
                    "name":          name,
                    "confidence":    round(confidence * 100, 2),
                    "info":          structured["info"],
                    "info_sections": structured["info_sections"],
                    "images":        images,
                }
                _push(recognized_history, _last_result)

                # Speak only the clean first sentence
                common = name.split("(")[0].strip()
                first  = structured["info"].split(".")[0].strip()
                speak_async(f"{common}. {first}." if first else f"Detected: {common}.")

            else:
                _last_result = {
                    "name":       "Unknown",
                    "confidence": 0,
                    "info":       (
                        "Could not identify this flower. "
                        "For best results: use a clear, well-lit close-up photo "
                        "with the flower centred and in sharp focus. "
                        "Avoid blurry or dark images."
                    ),
                    "info_sections": {
                        "Tips for better detection": (
                            "• Hold camera 20-30 cm from the flower\n"
                            "• Use good natural lighting\n"
                            "• Focus on the flower head directly\n"
                            "• Avoid busy backgrounds"
                        )
                    },
                    "images": _placeholder("unknown+flower"),
                }
                _push(unrecognized_history, _last_result)
        else:
            print("ℹ️  Same image — returning cached result")

        return _last_result

    except HTTPException:
        raise
    except Exception as exc:
        print(f"❌ /detect error: {exc}")
        traceback.print_exc()
        return {
            "name": "Error", "confidence": 0,
            "info": f"Processing error: {str(exc)[:120]}. Please try again.",
            "info_sections": {},
            "images": _placeholder("error"),
        }


@app.get("/voice-detect")
async def voice_detect(flower_name: Optional[str] = Query(default=None)):
    """
    Listen on server mic (or use provided flower_name from browser speech)
    and return structured flower info.
    """
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            _pool, lambda: process_audio_flower(flower_name or "")
        )
        # Build structured info for voice results too
        name     = result.get("name", "Unknown")
        raw_info = result.get("info", "")
        if name not in ("Unknown", "None", "Error") and raw_info not in ("No info found", ""):
            structured = _build_flower_info(name, raw_info, 0)
            result["info"]          = structured["info"]
            result["info_sections"] = structured["info_sections"]
        else:
            result["info_sections"] = {}

        return {
            "name":          result.get("name", "Unknown"),
            "info":          result.get("info", "No information available."),
            "info_sections": result.get("info_sections", {}),
            "images":        result.get("images", _placeholder("voice")),
            "confidence":    0,
        }
    except Exception as exc:
        print(f"❌ /voice-detect: {exc}")
        return {
            "name":          "Error",
            "info":          "Voice processing failed. Please try again.",
            "info_sections": {},
            "images":        _placeholder("error"),
            "confidence":    0,
        }


@app.get("/history")
def get_history():
    return {"recognized": recognized_history, "unrecognized": unrecognized_history}


@app.delete("/clear-history")
def clear_history():
    recognized_history.clear()
    unrecognized_history.clear()
    return {"message": "History cleared."}
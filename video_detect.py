# """
# video_detect.py
# ---------------
# Standalone real-time flower detection using your webcam.

# Run:    python video_detect.py
# Quit:   press Q or ESC

# What it does
# ------------
#   • Reads frames from the default camera (index 0).
#   • Runs YOLOv8n on every frame for bounding-box annotation (COCO classes).
#   • Calls PlantNet every API_DELAY seconds for flower identification.
#     (PlantNet works on the raw frame — not filtered by YOLO class.)
#   • Displays a live info panel with the flower name + Wikipedia excerpt.
# """

# import sys
# import time

# import cv2
# import numpy as np

# from utils import get_info, identify_plant

# try:
#     from ultralytics import YOLO
#     model = YOLO("yolov8n.pt")
#     print("✅ YOLO model loaded")
# except Exception as exc:
#     print(f"❌ YOLO load failed: {exc}")
#     sys.exit(1)


# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("❌ Could not open camera (index 0).")
#     sys.exit(1)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# print("✅ Flower Classification System — LIVE")
# print("   Press  Q  or  ESC  to quit\n")


# API_DELAY   = 5         
# PANEL_W     = 430        
# FONT        = cv2.FONT_HERSHEY_SIMPLEX
# CLR_TITLE   = (0, 255, 220)
# CLR_NAME    = (0, 230, 100)
# CLR_META    = (160, 160, 160)
# CLR_TEXT    = (220, 220, 220)
# CLR_FOOTER  = (100, 100, 220)
# CLR_DIVIDER = (60, 60, 60)


# last_name     = "Detecting…"
# last_info     = "Waiting for first identification."
# last_conf     = 0.0
# last_api_call = 0.0

# def wrap_text(text: str, max_chars: int = 50) -> list:
#     """Word-wrap *text* into lines of ≤ *max_chars* characters."""
#     words = text.split()
#     lines, cur = [], ""
#     for word in words:
#         candidate = (cur + " " + word).lstrip()
#         if len(candidate) <= max_chars:
#             cur = candidate
#         else:
#             if cur:
#                 lines.append(cur)
#             cur = word
#     if cur:
#         lines.append(cur)
#     return lines


# def draw_panel(canvas: np.ndarray, cam_w: int, cam_h: int) -> None:
#     """Render the right-hand information panel onto *canvas* in-place."""
#     x0 = cam_w

   
#     cv2.rectangle(canvas, (x0, 0), (x0 + PANEL_W, cam_h), (25, 25, 30), -1)

#     cv2.putText(canvas, "Flower Classification System",
#                 (x0 + 12, 30), FONT, 0.55, CLR_TITLE, 1, cv2.LINE_AA)
#     cv2.putText(canvas, "YOLO + PlantNet AI",
#                 (x0 + 12, 50), FONT, 0.40, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 60), (x0 + PANEL_W - 10, 60), CLR_DIVIDER, 1)

   
#     display_name = last_name if len(last_name) <= 38 else last_name[:36] + "…"
#     cv2.putText(canvas, display_name,
#                 (x0 + 12, 90), FONT, 0.60, CLR_NAME, 2, cv2.LINE_AA)

   
#     conf_str = f"Confidence: {last_conf * 100:.1f}%" if last_conf > 0 else ""
#     cv2.putText(canvas, conf_str,
#                 (x0 + 12, 112), FONT, 0.38, CLR_META, 1, cv2.LINE_AA)

#     cv2.putText(canvas, f"Updates every {API_DELAY}s",
#                 (x0 + 12, 130), FONT, 0.36, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 140), (x0 + PANEL_W - 10, 140), CLR_DIVIDER, 1)

#     lines = wrap_text(last_info, max_chars=50)
#     y = 158
#     for line in lines:
#         if y > cam_h - 30:
#             break
#         cv2.putText(canvas, line,
#                     (x0 + 12, y), FONT, 0.37, CLR_TEXT, 1, cv2.LINE_AA)
#         y += 18

#     cv2.putText(canvas, "Q / ESC  to exit",
#                 (x0 + 12, cam_h - 10), FONT, 0.40, CLR_FOOTER, 1, cv2.LINE_AA)



# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("❌ Camera read failed — exiting")
#         break

#     now = time.time()

 
#     if now - last_api_call >= API_DELAY:
#         last_api_call = now
#         ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
#         if ok:
#             name, conf = identify_plant(buf.tobytes())
#             if name != "Unknown":
#                 last_name = name
#                 last_conf = conf
#                 last_info = get_info(name)
#             else:
#                 last_name = "Unknown — point at a flower"
#                 last_conf = 0.0
#                 last_info = ("Could not identify the plant. "
#                              "Ensure good lighting and point the camera "
#                              "directly at the flower.")

#     results   = model(frame, verbose=False)
#     annotated = results[0].plot()

#     h, w = annotated.shape[:2]
#     canvas = np.zeros((h, w + PANEL_W, 3), dtype=np.uint8)
#     canvas[:, :w] = annotated
#     draw_panel(canvas, w, h)

#     cv2.imshow("Flower Classification System", canvas)

#     key = cv2.waitKey(1) & 0xFF
#     if key in (ord("q"), ord("Q"), 27):  
#         print("🛑 Stopped by user")
#         break

# cap.release()
# cv2.destroyAllWindows()



# video_detect.py
# ---------------
# Standalone real-time flower detection via webcam.

# Run:   python video_detect.py
# Quit:  press  Q  or  ESC

# Pipeline per frame:
#   • YOLOv8n  — bounding-box annotation (COCO classes, visual only)
#   • PlantNet — botanical identification every API_DELAY seconds
#   • Wikipedia — rich info fetched once per new identification

# """
# video_detect.py
# ---------------
# Standalone real-time flower detection using your webcam.

# Run:    python video_detect.py
# Quit:   press Q or ESC

# What it does
# ------------
#   • Reads frames from the default camera (index 0).
#   • Runs YOLOv8n on every frame for bounding-box annotation (COCO classes).
#   • Calls PlantNet every API_DELAY seconds for flower identification.
#     (PlantNet works on the raw frame — not filtered by YOLO class.)
#   • Displays a live info panel with the flower name + Wikipedia excerpt.
# """

# import sys
# import time

# import cv2
# import numpy as np

# from utils import get_info, identify_plant

# try:
#     from ultralytics import YOLO
#     model = YOLO("yolov8n.pt")
#     print("✅ YOLO model loaded")
# except Exception as exc:
#     print(f"❌ YOLO load failed: {exc}")
#     sys.exit(1)


# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("❌ Could not open camera (index 0).")
#     sys.exit(1)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# print("✅ Flower Classification System — LIVE")
# print("   Press  Q  or  ESC  to quit\n")


# API_DELAY   = 5         
# PANEL_W     = 430        
# FONT        = cv2.FONT_HERSHEY_SIMPLEX
# CLR_TITLE   = (0, 255, 220)
# CLR_NAME    = (0, 230, 100)
# CLR_META    = (160, 160, 160)
# CLR_TEXT    = (220, 220, 220)
# CLR_FOOTER  = (100, 100, 220)
# CLR_DIVIDER = (60, 60, 60)


# last_name     = "Detecting…"
# last_info     = "Waiting for first identification."
# last_conf     = 0.0
# last_api_call = 0.0

# def wrap_text(text: str, max_chars: int = 50) -> list:
#     """Word-wrap *text* into lines of ≤ *max_chars* characters."""
#     words = text.split()
#     lines, cur = [], ""
#     for word in words:
#         candidate = (cur + " " + word).lstrip()
#         if len(candidate) <= max_chars:
#             cur = candidate
#         else:
#             if cur:
#                 lines.append(cur)
#             cur = word
#     if cur:
#         lines.append(cur)
#     return lines


# def draw_panel(canvas: np.ndarray, cam_w: int, cam_h: int) -> None:
#     """Render the right-hand information panel onto *canvas* in-place."""
#     x0 = cam_w

   
#     cv2.rectangle(canvas, (x0, 0), (x0 + PANEL_W, cam_h), (25, 25, 30), -1)

#     cv2.putText(canvas, "Flower Classification System",
#                 (x0 + 12, 30), FONT, 0.55, CLR_TITLE, 1, cv2.LINE_AA)
#     cv2.putText(canvas, "YOLO + PlantNet AI",
#                 (x0 + 12, 50), FONT, 0.40, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 60), (x0 + PANEL_W - 10, 60), CLR_DIVIDER, 1)

   
#     display_name = last_name if len(last_name) <= 38 else last_name[:36] + "…"
#     cv2.putText(canvas, display_name,
#                 (x0 + 12, 90), FONT, 0.60, CLR_NAME, 2, cv2.LINE_AA)

   
#     conf_str = f"Confidence: {last_conf * 100:.1f}%" if last_conf > 0 else ""
#     cv2.putText(canvas, conf_str,
#                 (x0 + 12, 112), FONT, 0.38, CLR_META, 1, cv2.LINE_AA)

#     cv2.putText(canvas, f"Updates every {API_DELAY}s",
#                 (x0 + 12, 130), FONT, 0.36, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 140), (x0 + PANEL_W - 10, 140), CLR_DIVIDER, 1)

#     lines = wrap_text(last_info, max_chars=50)
#     y = 158
#     for line in lines:
#         if y > cam_h - 30:
#             break
#         cv2.putText(canvas, line,
#                     (x0 + 12, y), FONT, 0.37, CLR_TEXT, 1, cv2.LINE_AA)
#         y += 18

#     cv2.putText(canvas, "Q / ESC  to exit",
#                 (x0 + 12, cam_h - 10), FONT, 0.40, CLR_FOOTER, 1, cv2.LINE_AA)



# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("❌ Camera read failed — exiting")
#         break

#     now = time.time()

 
#     if now - last_api_call >= API_DELAY:
#         last_api_call = now
#         ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
#         if ok:
#             name, conf = identify_plant(buf.tobytes())
#             if name != "Unknown":
#                 last_name = name
#                 last_conf = conf
#                 last_info = get_info(name)
#             else:
#                 last_name = "Unknown — point at a flower"
#                 last_conf = 0.0
#                 last_info = ("Could not identify the plant. "
#                              "Ensure good lighting and point the camera "
#                              "directly at the flower.")

#     results   = model(frame, verbose=False)
#     annotated = results[0].plot()

#     h, w = annotated.shape[:2]
#     canvas = np.zeros((h, w + PANEL_W, 3), dtype=np.uint8)
#     canvas[:, :w] = annotated
#     draw_panel(canvas, w, h)

#     cv2.imshow("Flower Classification System", canvas)

#     key = cv2.waitKey(1) & 0xFF
#     if key in (ord("q"), ord("Q"), 27):  
#         print("🛑 Stopped by user")
#         break

# cap.release()
# cv2.destroyAllWindows()



# video_detect.py
# ---------------
# Standalone real-time flower detection via webcam.

# Run:   python video_detect.py
# Quit:  press  Q  or  ESC

# Pipeline per frame:
#   • YOLOv8n  — bounding-box annotation (COCO classes, visual only)
#   • PlantNet — botanical identification every API_DELAY seconds
#   • Wikipedia — rich info fetched once per new identification


# """
# video_detect.py
# ---------------
# Standalone real-time flower detection using your webcam.

# Run:    python video_detect.py
# Quit:   press Q or ESC

# What it does
# ------------
#   • Reads frames from the default camera (index 0).
#   • Runs YOLOv8n on every frame for bounding-box annotation (COCO classes).
#   • Calls PlantNet every API_DELAY seconds for flower identification.
#     (PlantNet works on the raw frame — not filtered by YOLO class.)
#   • Displays a live info panel with the flower name + Wikipedia excerpt.
# """

# import sys
# import time

# import cv2
# import numpy as np

# from utils import get_info, identify_plant

# try:
#     from ultralytics import YOLO
#     model = YOLO("yolov8n.pt")
#     print("✅ YOLO model loaded")
# except Exception as exc:
#     print(f"❌ YOLO load failed: {exc}")
#     sys.exit(1)


# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("❌ Could not open camera (index 0).")
#     sys.exit(1)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# print("✅ Flower Classification System — LIVE")
# print("   Press  Q  or  ESC  to quit\n")


# API_DELAY   = 5         
# PANEL_W     = 430        
# FONT        = cv2.FONT_HERSHEY_SIMPLEX
# CLR_TITLE   = (0, 255, 220)
# CLR_NAME    = (0, 230, 100)
# CLR_META    = (160, 160, 160)
# CLR_TEXT    = (220, 220, 220)
# CLR_FOOTER  = (100, 100, 220)
# CLR_DIVIDER = (60, 60, 60)


# last_name     = "Detecting…"
# last_info     = "Waiting for first identification."
# last_conf     = 0.0
# last_api_call = 0.0

# def wrap_text(text: str, max_chars: int = 50) -> list:
#     """Word-wrap *text* into lines of ≤ *max_chars* characters."""
#     words = text.split()
#     lines, cur = [], ""
#     for word in words:
#         candidate = (cur + " " + word).lstrip()
#         if len(candidate) <= max_chars:
#             cur = candidate
#         else:
#             if cur:
#                 lines.append(cur)
#             cur = word
#     if cur:
#         lines.append(cur)
#     return lines


# def draw_panel(canvas: np.ndarray, cam_w: int, cam_h: int) -> None:
#     """Render the right-hand information panel onto *canvas* in-place."""
#     x0 = cam_w

   
#     cv2.rectangle(canvas, (x0, 0), (x0 + PANEL_W, cam_h), (25, 25, 30), -1)

#     cv2.putText(canvas, "Flower Classification System",
#                 (x0 + 12, 30), FONT, 0.55, CLR_TITLE, 1, cv2.LINE_AA)
#     cv2.putText(canvas, "YOLO + PlantNet AI",
#                 (x0 + 12, 50), FONT, 0.40, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 60), (x0 + PANEL_W - 10, 60), CLR_DIVIDER, 1)

   
#     display_name = last_name if len(last_name) <= 38 else last_name[:36] + "…"
#     cv2.putText(canvas, display_name,
#                 (x0 + 12, 90), FONT, 0.60, CLR_NAME, 2, cv2.LINE_AA)

   
#     conf_str = f"Confidence: {last_conf * 100:.1f}%" if last_conf > 0 else ""
#     cv2.putText(canvas, conf_str,
#                 (x0 + 12, 112), FONT, 0.38, CLR_META, 1, cv2.LINE_AA)

#     cv2.putText(canvas, f"Updates every {API_DELAY}s",
#                 (x0 + 12, 130), FONT, 0.36, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 140), (x0 + PANEL_W - 10, 140), CLR_DIVIDER, 1)

#     lines = wrap_text(last_info, max_chars=50)
#     y = 158
#     for line in lines:
#         if y > cam_h - 30:
#             break
#         cv2.putText(canvas, line,
#                     (x0 + 12, y), FONT, 0.37, CLR_TEXT, 1, cv2.LINE_AA)
#         y += 18

#     cv2.putText(canvas, "Q / ESC  to exit",
#                 (x0 + 12, cam_h - 10), FONT, 0.40, CLR_FOOTER, 1, cv2.LINE_AA)



# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("❌ Camera read failed — exiting")
#         break

#     now = time.time()

 
#     if now - last_api_call >= API_DELAY:
#         last_api_call = now
#         ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
#         if ok:
#             name, conf = identify_plant(buf.tobytes())
#             if name != "Unknown":
#                 last_name = name
#                 last_conf = conf
#                 last_info = get_info(name)
#             else:
#                 last_name = "Unknown — point at a flower"
#                 last_conf = 0.0
#                 last_info = ("Could not identify the plant. "
#                              "Ensure good lighting and point the camera "
#                              "directly at the flower.")

#     results   = model(frame, verbose=False)
#     annotated = results[0].plot()

#     h, w = annotated.shape[:2]
#     canvas = np.zeros((h, w + PANEL_W, 3), dtype=np.uint8)
#     canvas[:, :w] = annotated
#     draw_panel(canvas, w, h)

#     cv2.imshow("Flower Classification System", canvas)

#     key = cv2.waitKey(1) & 0xFF
#     if key in (ord("q"), ord("Q"), 27):  
#         print("🛑 Stopped by user")
#         break

# cap.release()
# cv2.destroyAllWindows()



# video_detect.py
# ---------------
# Standalone real-time flower detection via webcam.

# Run:   python video_detect.py
# Quit:  press  Q  or  ESC

# Pipeline per frame:
#   • YOLOv8n  — bounding-box annotation (COCO classes, visual only)
#   • PlantNet — botanical identification every API_DELAY seconds
#   • Wikipedia — rich info fetched once per new identification

# """
# video_detect.py
# ---------------
# Standalone real-time flower detection using your webcam.

# Run:    python video_detect.py
# Quit:   press Q or ESC

# What it does
# ------------
#   • Reads frames from the default camera (index 0).
#   • Runs YOLOv8n on every frame for bounding-box annotation (COCO classes).
#   • Calls PlantNet every API_DELAY seconds for flower identification.
#     (PlantNet works on the raw frame — not filtered by YOLO class.)
#   • Displays a live info panel with the flower name + Wikipedia excerpt.
# """

# import sys
# import time

# import cv2
# import numpy as np

# from utils import get_info, identify_plant

# try:
#     from ultralytics import YOLO
#     model = YOLO("yolov8n.pt")
#     print("✅ YOLO model loaded")
# except Exception as exc:
#     print(f"❌ YOLO load failed: {exc}")
#     sys.exit(1)


# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("❌ Could not open camera (index 0).")
#     sys.exit(1)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# print("✅ Flower Classification System — LIVE")
# print("   Press  Q  or  ESC  to quit\n")


# API_DELAY   = 5         
# PANEL_W     = 430        
# FONT        = cv2.FONT_HERSHEY_SIMPLEX
# CLR_TITLE   = (0, 255, 220)
# CLR_NAME    = (0, 230, 100)
# CLR_META    = (160, 160, 160)
# CLR_TEXT    = (220, 220, 220)
# CLR_FOOTER  = (100, 100, 220)
# CLR_DIVIDER = (60, 60, 60)


# last_name     = "Detecting…"
# last_info     = "Waiting for first identification."
# last_conf     = 0.0
# last_api_call = 0.0

# def wrap_text(text: str, max_chars: int = 50) -> list:
#     """Word-wrap *text* into lines of ≤ *max_chars* characters."""
#     words = text.split()
#     lines, cur = [], ""
#     for word in words:
#         candidate = (cur + " " + word).lstrip()
#         if len(candidate) <= max_chars:
#             cur = candidate
#         else:
#             if cur:
#                 lines.append(cur)
#             cur = word
#     if cur:
#         lines.append(cur)
#     return lines


# def draw_panel(canvas: np.ndarray, cam_w: int, cam_h: int) -> None:
#     """Render the right-hand information panel onto *canvas* in-place."""
#     x0 = cam_w

   
#     cv2.rectangle(canvas, (x0, 0), (x0 + PANEL_W, cam_h), (25, 25, 30), -1)

#     cv2.putText(canvas, "Flower Classification System",
#                 (x0 + 12, 30), FONT, 0.55, CLR_TITLE, 1, cv2.LINE_AA)
#     cv2.putText(canvas, "YOLO + PlantNet AI",
#                 (x0 + 12, 50), FONT, 0.40, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 60), (x0 + PANEL_W - 10, 60), CLR_DIVIDER, 1)

   
#     display_name = last_name if len(last_name) <= 38 else last_name[:36] + "…"
#     cv2.putText(canvas, display_name,
#                 (x0 + 12, 90), FONT, 0.60, CLR_NAME, 2, cv2.LINE_AA)

   
#     conf_str = f"Confidence: {last_conf * 100:.1f}%" if last_conf > 0 else ""
#     cv2.putText(canvas, conf_str,
#                 (x0 + 12, 112), FONT, 0.38, CLR_META, 1, cv2.LINE_AA)

#     cv2.putText(canvas, f"Updates every {API_DELAY}s",
#                 (x0 + 12, 130), FONT, 0.36, CLR_META, 1, cv2.LINE_AA)
#     cv2.line(canvas, (x0 + 10, 140), (x0 + PANEL_W - 10, 140), CLR_DIVIDER, 1)

#     lines = wrap_text(last_info, max_chars=50)
#     y = 158
#     for line in lines:
#         if y > cam_h - 30:
#             break
#         cv2.putText(canvas, line,
#                     (x0 + 12, y), FONT, 0.37, CLR_TEXT, 1, cv2.LINE_AA)
#         y += 18

#     cv2.putText(canvas, "Q / ESC  to exit",
#                 (x0 + 12, cam_h - 10), FONT, 0.40, CLR_FOOTER, 1, cv2.LINE_AA)



# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("❌ Camera read failed — exiting")
#         break

#     now = time.time()

 
#     if now - last_api_call >= API_DELAY:
#         last_api_call = now
#         ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
#         if ok:
#             name, conf = identify_plant(buf.tobytes())
#             if name != "Unknown":
#                 last_name = name
#                 last_conf = conf
#                 last_info = get_info(name)
#             else:
#                 last_name = "Unknown — point at a flower"
#                 last_conf = 0.0
#                 last_info = ("Could not identify the plant. "
#                              "Ensure good lighting and point the camera "
#                              "directly at the flower.")

#     results   = model(frame, verbose=False)
#     annotated = results[0].plot()

#     h, w = annotated.shape[:2]
#     canvas = np.zeros((h, w + PANEL_W, 3), dtype=np.uint8)
#     canvas[:, :w] = annotated
#     draw_panel(canvas, w, h)

#     cv2.imshow("Flower Classification System", canvas)

#     key = cv2.waitKey(1) & 0xFF
#     if key in (ord("q"), ord("Q"), 27):  
#         print("🛑 Stopped by user")
#         break

# cap.release()
# cv2.destroyAllWindows()



# video_detect.py
# ---------------
# Standalone real-time flower detection via webcam.

# Run:   python video_detect.py
# Quit:  press  Q  or  ESC

# Pipeline per frame:
#   • YOLOv8n  — bounding-box annotation (COCO classes, visual only)
#   • PlantNet — botanical identification every API_DELAY seconds
#   • Wikipedia — rich info fetched once per new identification


import sys
import time

import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()   # MUST be before utils imports so PLANTNET_API_KEY is available

from utils import get_info, identify_plant   # noqa: E402

# ── YOLO ──────────────────────────────────────────────────────────────────────
try:
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt")
    print("✅ YOLO model loaded")
except Exception as exc:
    print(f"⚠️  YOLO load failed ({exc}) — running without bounding-box annotation")
    model = None   # graceful fallback — PlantNet still works

# ── Camera — try indices 0,1,2 until one opens ───────────────────────────────
cap = None
for _cam_idx in range(3):
    _c = cv2.VideoCapture(_cam_idx)
    if _c.isOpened():
        cap = _c
        print(f"✅ Camera opened at index {_cam_idx}")
        break
    _c.release()

if cap is None:
    print("❌ No camera found on indices 0-2.")
    print("   • Make sure a webcam is connected and not used by another app.")
    print("   • On Windows try: Device Manager → Cameras → check it's enabled.")
    sys.exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("✅ Flower Classification System — LIVE")
print("   Press  Q  or  ESC  to quit\n")

# ── Config ────────────────────────────────────────────────────────────────────
API_DELAY   = 5          # seconds between PlantNet calls
PANEL_W     = 440        # info panel width in pixels
FONT        = cv2.FONT_HERSHEY_SIMPLEX

# Colour palette (BGR)
CLR_BG      = (20, 22, 28)
CLR_TITLE   = (220, 255, 0)
CLR_NAME    = (80, 230, 80)
CLR_META    = (160, 160, 160)
CLR_TEXT    = (210, 210, 210)
CLR_FOOTER  = (200, 100, 100)
CLR_DIVIDER = (55, 55, 65)
CLR_CONF    = (0, 220, 180)

# ── State ─────────────────────────────────────────────────────────────────────
last_name      = "Detecting…"
last_info      = "Waiting for first identification."
last_conf      = 0.0
last_api_call  = 0.0
frame_count    = 0


# ── Helpers ───────────────────────────────────────────────────────────────────

def wrap_text(text: str, max_chars: int = 52) -> list:
    words  = text.split()
    lines, cur = [], ""
    for word in words:
        candidate = (cur + " " + word).lstrip()
        if len(candidate) <= max_chars:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_panel(canvas: np.ndarray, cam_w: int, cam_h: int) -> None:
    x0 = cam_w

    # Background
    cv2.rectangle(canvas, (x0, 0), (x0 + PANEL_W, cam_h), CLR_BG, -1)

    # Subtle gradient strip at left edge of panel
    cv2.rectangle(canvas, (x0, 0), (x0 + 3, cam_h), CLR_CONF, -1)

    # ── Title block ──────────────────────────────────────────────────────────
    cv2.putText(canvas, "FLOWER CLASSIFICATION",
                (x0 + 14, 28), FONT, 0.52, CLR_TITLE, 1, cv2.LINE_AA)
    cv2.putText(canvas, "YOLO  +  PlantNet  +  Wikipedia",
                (x0 + 14, 48), FONT, 0.36, CLR_META, 1, cv2.LINE_AA)
    cv2.line(canvas, (x0 + 12, 58), (x0 + PANEL_W - 12, 58), CLR_DIVIDER, 1)

    # ── Flower name ──────────────────────────────────────────────────────────
    display = last_name if len(last_name) <= 40 else last_name[:38] + "…"
    cv2.putText(canvas, display,
                (x0 + 14, 88), FONT, 0.62, CLR_NAME, 2, cv2.LINE_AA)

    # Confidence + update cadence
    if last_conf > 0:
        conf_str = f"Confidence: {last_conf * 100:.1f}%"
        cv2.putText(canvas, conf_str,
                    (x0 + 14, 110), FONT, 0.38, CLR_CONF, 1, cv2.LINE_AA)

    cv2.putText(canvas, f"Updates every {API_DELAY}s   |   Frame #{frame_count}",
                (x0 + 14, 128), FONT, 0.34, CLR_META, 1, cv2.LINE_AA)
    cv2.line(canvas, (x0 + 12, 138), (x0 + PANEL_W - 12, 138), CLR_DIVIDER, 1)

    # ── Info text ────────────────────────────────────────────────────────────
    lines = wrap_text(last_info, max_chars=52)
    y = 156
    for line in lines:
        if y > cam_h - 40:
            cv2.putText(canvas, "… (more on Wikipedia)",
                        (x0 + 14, y), FONT, 0.32, CLR_META, 1, cv2.LINE_AA)
            break
        cv2.putText(canvas, line,
                    (x0 + 14, y), FONT, 0.36, CLR_TEXT, 1, cv2.LINE_AA)
        y += 19

    # ── Footer ───────────────────────────────────────────────────────────────
    cv2.line(canvas, (x0 + 12, cam_h - 26), (x0 + PANEL_W - 12, cam_h - 26), CLR_DIVIDER, 1)
    cv2.putText(canvas, "Press Q or ESC to quit",
                (x0 + 14, cam_h - 10), FONT, 0.38, CLR_FOOTER, 1, cv2.LINE_AA)


# ── Main loop ─────────────────────────────────────────────────────────────────
_fps_time = time.time()
_fps_val  = 0.0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera read failed — check camera connection")
        break

    frame_count += 1
    now = time.time()

    # FPS calculation
    if frame_count % 30 == 0:
        _fps_val  = 30 / max(now - _fps_time, 0.001)
        _fps_time = now

    # PlantNet call (rate-limited to every API_DELAY seconds)
    if now - last_api_call >= API_DELAY:
        last_api_call = now
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 88])
        if ok:
            name, conf = identify_plant(buf.tobytes())
            if name != "Unknown":
                last_name = name
                last_conf = conf
                last_info = get_info(name)
                if last_info == "No info found":
                    last_info = f"{name} — Wikipedia information not available."
            else:
                last_name = "Unknown — point camera at a flower"
                last_conf = 0.0
                last_info = (
                    "Could not identify the plant. "
                    "Ensure good lighting, get close to the flower, "
                    "and make sure it fills most of the frame."
                )

    # YOLO annotation (only if model loaded)
    if model is not None:
        try:
            results   = model(frame, verbose=False)
            annotated = results[0].plot()
        except Exception:
            annotated = frame
    else:
        annotated = frame

    # Composite canvas with info panel
    h, w   = annotated.shape[:2]
    canvas = np.full((h, w + PANEL_W, 3), CLR_BG, dtype=np.uint8)
    canvas[:, :w] = annotated
    draw_panel(canvas, w, h)

    # FPS overlay (bottom-left of camera feed)
    cv2.putText(canvas, f"FPS: {_fps_val:.1f}",
                (8, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (80, 80, 80), 1, cv2.LINE_AA)

    cv2.imshow("Flower Classification System", canvas)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), ord("Q"), 27):
        print("🛑 Stopped by user")
        break

# ── Cleanup ───────────────────────────────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()
print("✅ Closed cleanly.")
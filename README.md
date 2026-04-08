# About the Project
The **Flower Classification System** is a Final Year AI project that combines computer vision, botanical APIs, and natural language processing to identify
flowers in real time. Users can detect flowers through their **webcam**,**upload a photo**, or use **voice commands** — and the system responds with
the flower's name, scientific classification, confidence score, Wikipedia information, and reference images.
The system is built on a **FastAPI** backend and a pure **HTML/CSS/JavaScript** frontend, communicating over a REST API. It features a fully integrated
**voice assistant** that speaks detection results aloud using browser-native Text-to-Speech (TTS).

# 🌸 Flower Detection and Classification System
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-00FFCD?style=flat&logo=yolo&logoColor=black)
![PlantNet](https://img.shields.io/badge/PlantNet_API-4CAF50?style=flat&logo=leaf&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
> An AI-powered real-time flower identification system using YOLOv8 object detection,
> PlantNet botanical API, Wikipedia, and a built-in voice assistant — all accessible through a modern browser-based interface.

# ✨ Features
# 🔍 Detection Modes
- 📷 Camera Mode** — Live webcam feed with real-time flower detection
<img width="1907" height="1080" alt="Screenshot 2026-04-04 231905" src="https://github.com/user-attachments/assets/f4a709b5-28d5-4197-8c61-1bd01a001271" />
  
- 📂 Upload Mode** — Upload any JPEG/PNG flower photo for identification
  <img width="1912" height="1081" alt="Screenshot 2026-04-04 231413" src="https://github.com/user-attachments/assets/2f73166e-d41a-457b-842e-1c56b2c47bac" />

- 🎤 Voice Mode** — Say a flower name, system looks it up and speaks the result
   <img width="1903" height="1071" alt="Screenshot 2026-04-04 231600" src="https://github.com/user-attachments/assets/debce968-82d8-4c0e-a74b-ecbb690df5d5" />

# 🧠 AI Pipeline
- **YOLOv8n** — Object detection and bounding-box annotation (visual layer)
- **PlantNet v2 API** — Botanical species identification with confidence scoring
- **Wikipedia REST API** — Rich multi-sentence plant information
- **Unsplash API** — High-quality reference flower photographs
# 🔊 Voice Assistant
- Browser-native Text-to-Speech speaks every detection result aloud
- Supports Indian English (en-IN) and all major languages
- Mute/unmute toggle button
- Server-side TTS via pyttsx3 as backup
# 🌐 Translation
- Translate detection results into 18 languages instantly
- Supports Hindi, Telugu, Tamil, French, German, Spanish, and more
- Powered by Google Translate API
# 📚 History & UI
- Detection history (recognised and unrecognised) with thumbnails
- Quick Facts panel — extracts family, genus, native region, colour
- Confidence progress bar
- Image lightbox viewer
- Animated pipeline background
- Fully responsive dark-themed UI
- 
# 🎯 Conclusion
The Flower Classification System successfully demonstrates the integration of multiple AI technologies — object detection, botanical identification, natural
language processing, and speech synthesis — into a single, cohesive application.The system provides accurate flower identification through three input modes,
delivers rich botanical information, and communicates results through both visual and audio channels, making it accessible and intuitive for all users.

# 🔮 Future Enhancements

-  Mobile app version (Android/iOS)
-  Support for identifying multiple flowers in a single image
-  User accounts with personalised detection history
-  Expand database to cover rare and endangered species
-  AR (Augmented Reality) overlay for real-time field use
-  Disease detection — identify plant diseases alongside species
-  Export detection report as PDF
-  Multi-language voice input support
  

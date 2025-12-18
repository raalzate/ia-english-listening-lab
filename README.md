# 🎤 English Listening Lab 

Este es un laboratorio de aprendizaje de inglés basado en Inteligencia Artificial. La aplicación permite transformar cualquier video de YouTube en una experiencia de estudio interactiva, con transcripción palabra por palabra sincronizada en tiempo real.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Faster-Whisper](https://img.shields.io/badge/Faster--Whisper-IA-blue?style=for-the-badge)

## ✨ Características

- **Descarga Inteligente:** Obtiene el audio directamente de YouTube usando `yt-dlp`.
- **Transcripción de Alta Precisión:** Utiliza el modelo `faster-whisper` (implementación optimizada de OpenAI Whisper) para obtener *timestamps* exactos de cada palabra.
- **Reproductor Interactivo:**
    - Resaltado dinámico de palabras mientras suena el audio.
    - **Navegación por clic:** Haz clic en cualquier palabra para saltar el audio a ese momento exacto (ideal para practicar pronunciación).
    - Ajuste de velocidad (0.5x a 1.0x) para facilitar el *Shadowing*.
- **Interfaz Moderna:** Construida íntegramente en Streamlit con componentes personalizados de HTML5/JavaScript.

## 🚀 Instalación y Uso

### 1. Requisitos Previos
Asegúrate de tener instalado [FFmpeg](https://ffmpeg.org/) en tu sistema, ya que es necesario para procesar el audio.


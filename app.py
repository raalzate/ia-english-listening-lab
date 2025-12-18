import streamlit as st
import yt_dlp
import os
import json
import time
import torch
from faster_whisper import WhisperModel

class KaraokeFasterWhisper:
    def __init__(self, model_size="base"):
        # Detección automática de dispositivo
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        self.model = WhisperModel(
            model_size, 
            device=self.device, 
            compute_type=self.compute_type
        )

    def descargar_audio(self, url, velocidad=0.85):
        output_name = f"audio_{int(time.time())}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            # Forzamos la extracción a un formato específico para permitir el filtrado
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # Eliminamos la opción de copia y forzamos el re-encodificado con filtros
            'postprocessor_args': [
                '-af', f'atempo={velocidad}'
            ],
            'outtmpl': f'{output_name}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        print(f"--- Descargando y re-codificando audio a velocidad {velocidad} ---")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return f"{output_name}.mp3"

    def transcribir_palabras(self, audio_path, idioma='en'):
        segments, _ = self.model.transcribe(
            audio_path, 
            language=idioma, 
            word_timestamps=True
        )
        word_data = []
        for segment in segments:
            for word in segment.words:
                word_data.append({
                    'w': word.word.strip(),
                    's': round(word.start, 3),
                    'e': round(word.end, 3)
                })
        return word_data

    def generar_componente_karaoke(self, audio_file, word_data):
        """Genera el HTML dinámico para Streamlit."""
        import base64
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        
        words_json = json.dumps(word_data)
        
        html_code = f"""
        <div id="karaoke-container" style="background:#1a1a1a; color:white; padding:20px; border-radius:15px; font-family:sans-serif;">
            <audio id="v-player" controls style="width:100%; margin-bottom:15px;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <div id="lyrics-box" style="height:250px; overflow-y:auto; line-height:1.8; font-size:1.4em; padding:15px; background:#000; border-radius:10px;">
                <div id="text-wrapper"></div>
            </div>
        </div>
        <style>
            .word {{ color: #555; margin-right: 7px; display: inline-block; transition: 0.2s; cursor:pointer; }}
            .active {{ color: #4CAF50; font-weight: bold; transform: scale(1.1); text-shadow: 0 0 8px #4CAF50; }}
            .read {{ color: #ccc; }}
        </style>
        <script>
            const words = {words_json};
            const wrapper = document.getElementById('text-wrapper');
            const player = document.getElementById('v-player');
            
            const spans = words.map((wd, i) => {{
                const s = document.createElement('span');
                s.className = 'word';
                s.innerText = wd.w;
                s.onclick = () => player.currentTime = wd.s;
                wrapper.appendChild(s);
                return {{ el: s, s: wd.s, e: wd.e }};
            }});

            player.ontimeupdate = () => {{
                const t = player.currentTime;
                spans.forEach((item, i) => {{
                    if(t >= item.s && t <= item.e) {{
                        item.el.className = 'word active';
                        if(i % 5 === 0) item.el.scrollIntoView({{behavior:'smooth', block:'center'}});
                    }} else if (t > item.e) {{
                        item.el.className = 'word read';
                    }} else {{
                        item.el.className = 'word';
                    }}
                }});
            }};
        </script>
        """
        return html_code

# --- APP STREAMLIT ---
st.set_page_config(page_title="IA English Lab", layout="wide")
st.title("🎧 Listening Lab con Resaltado IA")

col1, col2 = st.columns([1, 2])

with col1:
    url = st.text_input("YouTube URL", "https://www.youtube.com/watch?v=w4rG5GY9IlA")
    vel = st.slider("Velocidad", 0.5, 1.0, 0.82)
    btn = st.button("Generar Lab")

if btn:
    app = KaraokeFasterWhisper()
    with st.spinner("Descargando y Transcribiendo..."):
        # Descarga
        audio_path = app.descargar_audio(url, vel)
        # Transcripción
        data = app.transcribir_palabras(audio_path)
        # Visualización
        html_karaoke = app.generar_componente_karaoke(audio_path, data)
        st.components.v1.html(html_karaoke, height=500)
        
        # Limpieza opcional
        if os.path.exists(audio_path):
            os.remove(audio_path)
import streamlit as st
import yt_dlp
import os
import json
import time
import base64
import re
from faster_whisper import WhisperModel

# Configuración de página
st.set_page_config(page_title="English Learning Hub", page_icon="🇺🇸", layout="wide")

class EnglishLearningApp:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        if 'whisper_model' not in st.session_state:
            with st.spinner("Cargando modelo de IA Whisper..."):
                st.session_state.whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.model = st.session_state.whisper_model

    def descargar_audio(self, url, velocidad=0.85):
        output_name = f"audio_{int(time.time())}"
        
        # Intentamos usar proxies de Invidious si es URL de YouTube
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        url_final = f"https://yewtu.be/watch?v={video_id_match.group(1)}" if video_id_match else url

        ydl_opts = {
            'format': 'bestaudio/best',
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'postprocessor_args': ['-af', f'atempo={velocidad}'],
            'outtmpl': f'{output_name}.%(ext)s',
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_final])
        
        filename = f"{output_name}.mp3"
        if not os.path.exists(filename):
            raise Exception("YouTube bloqueó la descarga.")
        return filename

    def transcribir(self, audio_path):
        segments, _ = self.model.transcribe(audio_path, language="en", word_timestamps=True)
        word_data = []
        for segment in segments:
            for word in segment.words:
                word_data.append({'w': word.word.strip(), 's': round(word.start, 3), 'e': round(word.end, 3)})
        return word_data

    def render_ui(self, audio_file, word_data):
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        
        audio_html = f"data:audio/mp3;base64,{audio_base64}"
        words_json = json.dumps(word_data)

        st.components.v1.html(f"""
            <div style="background:#1e1e1e; padding:20px; border-radius:15px; font-family:sans-serif; color:white;">
                <audio id="p" controls src="{audio_html}" style="width:100%"></audio>
                <div id="t" style="height:300px; overflow-y:auto; margin-top:20px; font-size:1.5rem; line-height:2; color:#555;"></div>
            </div>
            <script>
                const data = {words_json};
                const t = document.getElementById('t');
                const p = document.getElementById('p');
                const spans = data.map(d => {{
                    const s = document.createElement('span');
                    s.innerText = d.w + ' ';
                    s.style.cursor = 'pointer';
                    s.style.transition = '0.2s';
                    s.onclick = () => p.currentTime = d.s;
                    t.appendChild(s);
                    return {{ el: s, s: d.s, e: d.e }};
                }});
                p.ontimeupdate = () => {{
                    const now = p.currentTime;
                    spans.forEach(item => {{
                        if(now >= item.s && now <= item.e) {{
                            item.el.style.color = '#00f2fe';
                            item.el.style.fontWeight = 'bold';
                        }} else if (now > item.e) item.el.style.color = '#fff';
                        else item.el.style.color = '#444';
                    }});
                }};
            </script>
        """, height=500)

# --- APP ---
st.title("🇺🇸 English Learning Hub")
col1, col2 = st.columns([1, 2])

with col1:
    url = st.text_input("YouTube URL:")
    archivo_local = st.file_uploader("O sube tu MP3 (si YouTube falla)", type=["mp3"])
    speed = st.slider("Velocidad", 0.5, 1.0, 0.85)

if st.button("Iniciar Lección 🚀"):
    app = EnglishLearningApp()
    audio_path = None
    
    try:
        with st.status("Procesando...", expanded=True) as status:
            if archivo_local:
                audio_path = "temp_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(archivo_local.getbuffer())
            else:
                st.write("📥 Descargando de YouTube...")
                audio_path = app.descargar_audio(url, speed)
            
            st.write("🧠 Transcribiendo con IA...")
            datos = app.transcribir(audio_path)
            status.update(label="¡Listo!", state="complete")
        
        app.render_ui(audio_path, datos)
        if os.path.exists(audio_path): os.remove(audio_path)
    except Exception as e:
        st.error(f"Error: {e}. Intenta subir el archivo MP3 directamente.")
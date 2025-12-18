import streamlit as st
import yt_dlp
import os
import json
import time
import base64
from faster_whisper import WhisperModel

# Configuración de página
st.set_page_config(page_title="English Learning Hub", page_icon="🇺🇸", layout="wide")

class EnglishLearningApp:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        if 'whisper_model' not in st.session_state:
            with st.spinner("Preparando laboratorio de idiomas..."):
                st.session_state.whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.model = st.session_state.whisper_model

    def descargar_audio(self, url, velocidad=0.85):
        output_name = f"audio_{int(time.time())}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'postprocessor_args': ['-af', f'atempo={velocidad}'],
            'outtmpl': f'{output_name}.%(ext)s',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"{output_name}.mp3"

    def transcribir_aprendizaje(self, audio_path):
        # Transcribimos y traducimos internamente si es necesario
        segments, _ = self.model.transcribe(audio_path, language="en", word_timestamps=True)
        
        full_data = []
        full_text = ""
        
        for segment in segments:
            full_text += segment.text + " "
            for word in segment.words:
                full_data.append({
                    'w': word.word.strip(),
                    's': round(word.start, 3),
                    'e': round(word.end, 3)
                })
        return full_data, full_text.strip()

    def render_learning_ui(self, audio_file, word_data):
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        
        audio_html = f"data:audio/mp3;base64,{audio_base64}"
        words_json = json.dumps(word_data)

        html_code = f"""
        <div style="background: #1e1e1e; padding: 25px; border-radius: 20px; border: 1px solid #383838; font-family: 'Inter', sans-serif;">
            <audio id="player" controls src="{audio_html}" style="width: 100%; margin-bottom: 25px;"></audio>
            
            <div id="transcript-box" style="background: #000; padding: 30px; border-radius: 15px; height: 350px; overflow-y: auto; line-height: 2; font-size: 1.5rem; color: #888; border: 1px solid #333;">
                <div id="content"></div>
            </div>
            
            <p style="color: #666; font-size: 0.9rem; margin-top: 15px;">💡 Tip: Haz clic en cualquier palabra para repetir la pronunciación.</p>
        </div>

        <script>
            const data = {words_json};
            const content = document.getElementById('content');
            const player = document.getElementById('player');

            const spans = data.map((d) => {{
                const s = document.createElement('span');
                s.style.display = 'inline-block';
                s.style.marginRight = '10px';
                s.style.cursor = 'pointer';
                s.style.transition = 'all 0.2s';
                s.innerText = d.w;
                s.onclick = () => player.currentTime = d.s;
                content.appendChild(s);
                return {{ el: s, s: d.s, e: d.e }};
            }});

            player.ontimeupdate = () => {{
                const now = player.currentTime;
                spans.forEach((item) => {{
                    if (now >= item.s && now <= item.e) {{
                        item.el.style.color = '#00f2fe';
                        item.el.style.transform = 'scale(1.2)';
                        item.el.style.textShadow = '0 0 10px #00f2fe66';
                        item.el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }} else if (now > item.e) {{
                        item.el.style.color = '#fff';
                        item.el.style.transform = 'scale(1)';
                        item.el.style.textShadow = 'none';
                    }} else {{
                        item.el.style.color = '#444';
                        item.el.style.transform = 'scale(1)';
                    }}
                }});
            }};
        </script>
        """
        st.components.v1.html(html_code, height=550)

# --- INTERFAZ ---
st.title("🇺🇸 English Listening Lab")
st.subheader("Mejora tu comprensión auditiva con IA")

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### ⚙️ Ajustes")
    url = st.text_input("Video de YouTube (English):")
    speed = st.select_slider("Velocidad de estudio:", options=[0.5, 0.75, 0.85, 1.0], value=0.85)
    st.info("Recomendamos 0.85 para captar mejor los fonemas.")

with col2:
    if st.button("Comenzar Lección 🚀", use_container_width=True):
        if url:
            app = EnglishLearningApp()
            
            with st.status("Preparando material didáctico...", expanded=True) as s:
                st.write("📥 Descargando audio original...")
                audio = app.descargar_audio(url, speed)
                st.write("✍️ Generando transcripción fonética...")
                data, raw_text = app.transcribir_aprendizaje(audio)
                s.update(label="¡Clase lista!", state="complete")
            
            # Layout de estudio
            tab1, tab2 = st.tabs(["🎧 Reproductor Interactivo", "📖 Vocabulario Completo"])
            
            with tab1:
                app.render_learning_ui(audio, data)
            
            with tab2:
                st.markdown("### Texto completo para estudio")
                st.write(raw_text)
                st.download_button("Descargar Transcripción", raw_text, file_name="lesson.txt")
        else:
            st.warning("Introduce una URL para empezar.")


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
            with st.spinner("Preparando laboratorio de idiomas (IA Whisper)..."):
                # Optimizamos para CPU de Streamlit Cloud
                st.session_state.whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.model = st.session_state.whisper_model

    def corregir_url(self, url):
        """Convierte URLs de YouTube a instancias de Invidious para saltar bloqueos."""
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        if video_id_match:
            video_id = video_id_match.group(1)
            # Usamos yewtu.be como proxy para evitar el error 403 Forbidden
            return f"https://yewtu.be/watch?v={video_id}"
        return url

    def descargar_audio(self, url, velocidad=0.85):
        url_final = self.corregir_url(url)
        output_name = f"audio_{int(time.time())}"
        
        ydl_opts = {
            # 'ba' busca el mejor audio disponible que no requiera descifrado complejo
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
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_final])
        
        # Verificamos si el archivo se creó realmente
        filename = f"{output_name}.mp3"
        if not os.path.exists(filename):
            raise Exception("No se pudo descargar el audio. YouTube bloqueó la petición incluso vía proxy.")
            
        return filename

    def transcribir_aprendizaje(self, audio_path):
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
        <div style="background: #1e1e1e; padding: 25px; border-radius: 20px; border: 1px solid #383838; font-family: sans-serif; color: white;">
            <audio id="player" controls src="{audio_html}" style="width: 100%; margin-bottom: 25px;"></audio>
            <div id="transcript-box" style="background: #000; padding: 30px; border-radius: 15px; height: 350px; overflow-y: auto; line-height: 2; font-size: 1.5rem; color: #666; border: 1px solid #333; scroll-behavior: smooth;">
                <div id="content"></div>
            </div>
            <p style="color: #666; font-size: 0.9rem; margin-top: 15px;">💡 Haz clic en una palabra para saltar a ese momento.</p>
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
                        item.el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }} else if (now > item.e) {{
                        item.el.style.color = '#fff';
                        item.el.style.transform = 'scale(1)';
                    }} else {{
                        item.el.style.color = '#444';
                    }}
                }});
            }};
        </script>
        """
        st.components.v1.html(html_code, height=550)

# --- INTERFAZ ---
st.title("🇺🇸 English Listening Lab")
st.subheader("Practica tu oido con transcripción sincronizada")

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### ⚙️ Configuración")
    url = st.text_input("YouTube URL:")
    speed = st.select_slider("Velocidad:", options=[0.5, 0.75, 0.85, 1.0], value=0.85)
    st.info("Nota: Se usará un proxy automático para evitar bloqueos de YouTube.")

with col2:
    if st.button("Comenzar Lección 🚀", use_container_width=True):
        if url:
            app = EnglishLearningApp()
            try:
                with st.status("Procesando material...", expanded=True) as s:
                    st.write("📥 Descargando audio (vía Proxy)...")
                    audio_file = app.descargar_audio(url, speed)
                    
                    st.write("🧠 Transcribiendo con IA...")
                    word_data, raw_text = app.transcribir_aprendizaje(audio_file)
                    
                    s.update(label="¡Listo!", state="complete")
                
                tab1, tab2 = st.tabs(["🎧 Estudio Interactivo", "📖 Texto Plano"])
                
                with tab1:
                    app.render_learning_ui(audio_file, word_data)
                
                with tab2:
                    st.write(raw_text)
                
                # Borramos archivo temporal para no llenar el servidor
                if os.path.exists(audio_file):
                    os.remove(audio_file)

            except Exception as e:
                st.error(f"Error crítico: {e}")
        else:
            st.warning("Por favor, introduce una URL.")
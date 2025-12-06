import webview
import os
import json
import threading
import time
import base64
import tempfile
import mss
import mss.tools
import speech_recognition as sr
import pyaudio
import wave
from PIL import Image
from io import BytesIO
import google.generativeai as genai

# arquivo global de configurações
SETTINGS_FILE = 'settings.json'

class Api:
    def __init__(self):
        self.api_key = None
        self.recording = False
        self.audio_frames = []
        self._load_settings()

    def _load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    self.api_key = data.get('api_key')
                    if self.api_key:
                        genai.configure(api_key=self.api_key)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self, key):
        self.api_key = key
        genai.configure(api_key=key)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({'api_key': key}, f)
        return True

    def load_settings(self):
        return self.api_key

    def close_app(self):
        webview.windows[0].destroy()

    def send_message(self, text, image_b64=None):
        if not self.api_key:
            return "por favor, configure sua chave de api primeiro."

        try:
            # usa o modelo gemini-2.0-flash que deve estar liberado
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            content = []
            
            # adiciona uma instrução básica
            system_instruction = "você é um assistente de desktop. aja naturalmente, como um amigo. responda sempre em português do brasil. use sempre letras minúsculas (lowercase) em tudo. se tiver imagem, analise e descreva ou responda sobre ela."
            
            # se tiver texto, combina. se não, vai só a instrução.
            if text:
                final_prompt = f"{system_instruction}\n\npergunta do usuário: {text}"
            else:
                final_prompt = system_instruction
                
            content.append(final_prompt)
                
            if image_b64:
                # converte base64 de volta pra imagem pil
                image_data = base64.b64decode(image_b64)
                image = Image.open(BytesIO(image_data))
                content.append(image)

            # gera o conteúdo
            response = model.generate_content(content)
            return response.text.lower() # força minúsculas na saída por garantia
        except Exception as e:
            return f"erro no gemini: {str(e)}"

    def analyze_screen(self, prompt="o que tem na minha tela?"):
        if not self.api_key:
            return "por favor, configure sua chave de api primeiro."

        window = webview.windows[0]
        window.hide()
        time.sleep(0.5) 

        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                img.thumbnail((1024, 1024))
                
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            window.show()
            return f"falha ao capturar tela: {str(e)}"

        window.show()
        return self.send_message(prompt, img_str)

    def toggle_recording(self, start):
        if start:
            if not self.recording:
                self.start_listening()
            return "gravando..."

        else:
            if self.recording:
                return self.stop_listening()
            return None

    def start_listening(self):
        self.recording = True
        self.audio_frames = []
        
        def record_thread():
            try:
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
                while self.recording:
                    # Non-blocking read?
                    # na real bloqueia, mas tá suave pra essa thread
                    if stream.is_active():
                        data = stream.read(1024, exception_on_overflow=False)
                        self.audio_frames.append(data)
                stream.stop_stream()
                stream.close()
                p.terminate()
            except Exception as e:
                print(f"Audio thread error: {e}")

        self.thread = threading.Thread(target=record_thread)
        self.thread.start()

    def stop_listening(self):
        self.recording = False
        try:
            self.thread.join(timeout=2.0)
        except:
            pass
        
        if not self.audio_frames:
            return None
            
        # salva num wav temporário
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            wf = wave.open(temp_wav.name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
            filename = temp_wav.name
            
        r = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio_data = r.record(source)
            
        try:
            # usa o google web speech api (gratuito)
            text = r.recognize_google(audio_data, language="pt-BR") 
            os.unlink(filename)
            return text
        except sr.UnknownValueError:
            try: os.unlink(filename)
            except: pass
            return None
        except sr.RequestError as e:
            try: os.unlink(filename)
            except: pass
            return f"erro no serviço de voz: {e}"

if __name__ == '__main__':
    api = Api()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(current_dir, 'web')
    index_path = os.path.join(web_dir, 'index.html')

    window = webview.create_window(
        'Assistente de IA', 
        url=f'file:///{index_path}',
        width=400,
        height=600,
        frameless=True,
        easy_drag=False,
        on_top=True,
        transparent=True,
        js_api=api
    )
    

    def on_loaded():
        # espera um pouco mais pra garantir
        time.sleep(1.0)
        # força um resize pra obrigar a repintar e arrumar a transparência
        window.resize(401, 601) 
        time.sleep(0.1)
        window.resize(400, 600)
        
        # pisca a janela (hide/show) como garantia final
        window.hide()
        time.sleep(0.2)
        window.show()

    webview.start(debug=True, func=on_loaded)


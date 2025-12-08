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
from io import BytesIO
from PIL import Image

# Managers
from llm_manager import LLMManager
from rag_manager import RAGManager
from web_search_manager import WebSearchManager
from mcp_manager import MCPManager

SETTINGS_FILE = 'settings.json'

class Api:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        
        # Initialize Managers
        self.llm = LLMManager(SETTINGS_FILE)
        self.rag = RAGManager()
        self.web = WebSearchManager()
        self.mcp = MCPManager()

        # State
        self.rag_enabled = False

        self.current_provider = 'gemini'

    def close_app(self):
        webview.windows[0].destroy()

    def get_settings(self):
        return {
            "api_keys": self.llm.api_keys,
            "models": self.llm.models,
            "rag_enabled": self.rag_enabled,

            "current_provider": self.current_provider
        }

    def save_settings(self, settings):
        # Update internal state
        self.current_provider = settings.get('provider', 'gemini')
        self.rag_enabled = settings.get('rag_enabled', False)


        # Update Keys/Models in LLM Manager
        if 'api_keys' in settings:
            self.llm.api_keys.update(settings['api_keys'])
        if 'models' in settings:
            self.llm.models.update(settings['models'])
        
        # Save to file
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({
                'keys': self.llm.api_keys,
                'gemini_model': self.llm.models.get('gemini'),
                'openrouter_model': self.llm.models.get('openrouter'),
                'last_provider': self.current_provider,
                'rag_enabled': self.rag_enabled,

            }, f, indent=4)
        
        # Reload LLM manager to apply keys
        self.llm._load_settings()
        return True

    def send_message(self, text, image_b64=None):
        context_parts = []

        # 1. MCP Context (Always active for personalization)
        mcp_context = self.mcp.get_context_string()
        
        # 2. RAG Retrieval
        if self.rag_enabled and text:
            rag_results = self.rag.query_context(text)
            if rag_results:
                context_parts.append(f"=== CONTEXTO RECUPERADO (RAG) ===\n{rag_results}")



        # Assemble Final System Instruction
        system_instruction = (
            "Você é um assistente de desktop avançado. aja naturalmente, como um parceiro de trabalho.\n"
            "responda sempre em português do brasil. use letras minúsculas.\n"
            "se tiver imagem, analise e descreva.\n"
            "use as informações de contexto abaixo para enriquecer sua resposta, se relevante.\n\n"
            f"{mcp_context}\n" +
            "\n".join(context_parts)
        )

        # Call LLM
        response = self.llm.generate_response(
            text, 
            image_b64=image_b64, 
            provider=self.current_provider,
            system_instruction=system_instruction
        )

        # Update MCP with interaction
        self.mcp.add_task(f"User query: {text[:50]}...")
        
        # Save to RAG
        if self.rag_enabled and text and len(text) > 20:
            self.rag.add_document(text, source="user_chat")

        return response

    def analyze_screen(self, prompt="o que tem na minha tela?"):
        window = webview.windows[0]
        window.hide()
        time.sleep(0.5) 

        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                # Resize for performance
                img.thumbnail((1024, 1024))
                
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=80)
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            window.show()
            return f"falha ao capturar tela: {str(e)}"

        window.show()
        return self.send_message(prompt, img_str)

    # Audio methods
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
            print("DEBUG: Audio thread started")
            p = None
            stream = None
            try:
                p = pyaudio.PyAudio()
                # 16000Hz standard for SR
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
                print("DEBUG: Stream opened successfully")
                
                while self.recording:
                    if stream.is_active():
                        data = stream.read(1024, exception_on_overflow=False)
                        self.audio_frames.append(data)
                        
            except Exception as e:
                print(f"DEBUG: Audio thread fatal error: {e}")
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
                if p:
                    p.terminate()
                print(f"DEBUG: Audio thread finished. Frames captured: {len(self.audio_frames)}")

        self.thread = threading.Thread(target=record_thread)
        self.thread.start()

    def stop_listening(self):
        self.recording = False
        try:
            self.thread.join(timeout=2.0)
        except:
            pass
        
        if not self.audio_frames:
            print("DEBUG: No audio frames captured!")
            return None
            
        print(f"DEBUG: Processing {len(self.audio_frames)} frames...")
        
        filename = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                wf = wave.open(temp_wav.name, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(2) 
                wf.setframerate(16000) 
                wf.writeframes(b''.join(self.audio_frames))
                wf.close()
                filename = temp_wav.name
            
            r = sr.Recognizer()
            with sr.AudioFile(filename) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="pt-BR")
                print(f"DEBUG: Recognized text: {text}")
                
                # Robust deletion with retry
                for _ in range(5):
                    try:
                        os.unlink(filename)
                        break
                    except Exception as del_err:
                        print(f"DEBUG: Retrying file deletion ({del_err})...")
                        time.sleep(0.5)
                
                return text

        except Exception as e:
            print(f"DEBUG: Audio Recognition Error: {e}")
            
            if filename:
                for _ in range(5):
                    try:
                        os.unlink(filename)
                        break
                    except:
                        time.sleep(0.5)

            if isinstance(e, sr.RequestError):
                return f"Erro de conexão com serviço de voz: {e}"
            elif isinstance(e, sr.UnknownValueError):
                return None 
            
            return f"Erro de áudio: {str(e)[:50]}"

if __name__ == '__main__':
    api = Api()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(current_dir, 'web')
    index_path = os.path.join(web_dir, 'index.html')

    window = webview.create_window(
        'Assistente IA', 
        url=f'file:///{index_path}',
        width=450,
        height=700,
        frameless=True,
        easy_drag=False,
        on_top=True,
        transparent=True,
        js_api=api
    )

    def on_loaded():
        time.sleep(1.0)
        window.resize(451, 701) 
        time.sleep(0.1)
        window.resize(450, 700)
        
    webview.start(debug=False, func=on_loaded)

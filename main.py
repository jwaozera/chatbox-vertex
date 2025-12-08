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

# gerenciadores
# gerenciadores
from llm_manager import LLMManager
from rag_manager import RAGManager
# from web_search_manager import WebSearchManager # removido porque pediram
from mcp_manager import MCPManager
from prompt_manager import PromptManager

SETTINGS_FILE = 'settings.json'

class Api:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        
        # iniciando os gerenciadores
        self.llm = LLMManager(SETTINGS_FILE)
        self.rag = RAGManager()
        # self.web = WebSearchManager() # tiraram esse
        self.mcp = MCPManager()
        self.prompts = PromptManager()

        # estado atual
        self.rag_enabled = False
        # self.web_enabled = False # removido
        self.current_provider = 'gemini'

    def close_app(self):
        webview.windows[0].destroy()

    def get_settings(self):
        return {
            "api_keys": self.llm.api_keys,
            "models": self.llm.models,
            "rag_enabled": self.rag_enabled,
            "web_enabled": False, # forçando false na marra
            "current_provider": self.current_provider
        }

    def save_settings(self, settings):
        # atualiza o estado interno
        self.current_provider = settings.get('provider', 'gemini')
        self.rag_enabled = settings.get('rag_enabled', False)
        # self.web_enabled = settings.get('web_enabled', False)

        # atualiza chaves e modelos no gerenciador llm
        if 'api_keys' in settings:
            self.llm.api_keys.update(settings['api_keys'])
        if 'models' in settings:
            self.llm.models.update(settings['models'])
        
        # salva tudo no arquivo
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({
                'keys': self.llm.api_keys,
                'gemini_model': self.llm.models.get('gemini'),
                'openrouter_model': self.llm.models.get('openrouter'),
                'last_provider': self.current_provider,
                'rag_enabled': self.rag_enabled,
                'web_enabled': False
            }, f, indent=4)
        
        # recarrega o llm manager pra aplicar as chaves novas
        self.llm._load_settings()
        return True

    # --- funções da biblioteca de prompts ---
    def get_prompts(self):
        return self.prompts.get_all_prompts()

    def save_prompt(self, prompt_data):
        return self.prompts.save_prompt(prompt_data)

    def delete_prompt(self, prompt_id):
        return self.prompts.delete_prompt(prompt_id)
    # ------------------------------

    def send_message(self, text, image_b64=None, active_prompt=None):
        context_parts = []

        # 1. contexto mcp (sempre ligado pra personalizar)
        mcp_context = self.mcp.get_context_string()
        
        # 2. recuperação rag (puxando da memória)
        if self.rag_enabled and text:
            rag_results = self.rag.query_context(text)
            if rag_results:
                context_parts.append(f"=== CONTEXTO RECUPERADO (RAG) ===\n{rag_results}")

        # 3. busca web (foi de base)
        # if self.web_enabled and text: ...

        # definindo o prompt de sistema
        if active_prompt:
            # monta o prompt usando o template customizado
            system_instruction = (
                f"Persona: {active_prompt.get('persona', '')}\n"
                f"Task: {active_prompt.get('task', '')}\n"
                f"Instructions: {active_prompt.get('instructions', '')}\n"
                f"Output Format: {active_prompt.get('output_format', '')}\n\n"
                "Additional Context:\n"
                f"{mcp_context}\n" +
                "\n".join(context_parts)
            )
        else:
            # modo padrão
            system_instruction = (
                "você é um assistente de desktop avançado. aja naturalmente, como um parceiro de trabalho.\n"
                "responda sempre em português do brasil. use letras minúsculas.\n"
                "se tiver imagem, analise e descreva.\n"
                "use as informações de contexto abaixo para enriquecer sua resposta, se relevante.\n\n"
                f"{mcp_context}\n" +
                "\n".join(context_parts)
            )

        # chamando o llm
        response = self.llm.generate_response(
            text, 
            image_b64=image_b64, 
            provider=self.current_provider,
            system_instruction=system_instruction
        )

        # atualiza o mcp com essa interação
        self.mcp.add_task(f"User query: {text[:50]}...")
        
        # salva na memória rag
        if self.rag_enabled and text and len(text) > 20:
            self.rag.add_document(text, source="user_chat")

        return response

    def analyze_screen(self, prompt="o que tem na minha tela?", active_prompt=None):
        window = webview.windows[0]
        window.hide()
        time.sleep(0.5) 

        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                # diminui o tamanho pra não travar tudo
                img.thumbnail((1024, 1024))
                
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=80)
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            window.show()
            return f"falha ao capturar tela: {str(e)}"

        window.show()
        # manda o prompt ativo junto pro send_message
        return self.send_message(prompt, img_str, active_prompt=active_prompt)

    # parte de áudio
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
            print("DEBUG: thread de áudio começou")
            p = None
            stream = None
            try:
                p = pyaudio.PyAudio()
                # 16000hz é o padrão pro sr
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
                print("DEBUG: stream aberto com sucesso")
                
                while self.recording:
                    if stream.is_active():
                        data = stream.read(1024, exception_on_overflow=False)
                        self.audio_frames.append(data)
                        
            except Exception as e:
                print(f"DEBUG: erro fatal na thread de áudio: {e}")
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
                if p:
                    p.terminate()
                print(f"DEBUG: thread de áudio finalizada. frames capturados: {len(self.audio_frames)}")

        self.thread = threading.Thread(target=record_thread)
        self.thread.start()

    def stop_listening(self):
        self.recording = False
        try:
            self.thread.join(timeout=2.0)
        except:
            pass
        
        if not self.audio_frames:
            print("DEBUG: nenhum frame de áudio capturado!")
            return None
            
        print(f"DEBUG: processando {len(self.audio_frames)} frames...")
        
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
                print(f"DEBUG: texto reconhecido: {text}")
                
                # tentando apagar o arquivo na marra (com retry)
                for _ in range(5):
                    try:
                        os.unlink(filename)
                        break
                    except Exception as del_err:
                        print(f"DEBUG: tentando deletar arquivo novamente ({del_err})...")
                        time.sleep(0.5)
                
                return text

        except Exception as e:
            print(f"DEBUG: erro de reconhecimento de áudio: {e}")
            
            if filename:
                for _ in range(5):
                    try:
                        os.unlink(filename)
                        break
                    except:
                        time.sleep(0.5)

            if isinstance(e, sr.RequestError):
                return f"erro de conexão com serviço de voz: {e}"
            elif isinstance(e, sr.UnknownValueError):
                return None 
            
            return f"erro de áudio: {str(e)[:50]}"

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

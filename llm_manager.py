import os
import json
import base64
import requests
import google.generativeai as genai
from PIL import Image
from io import BytesIO

class LLMManager:
    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.api_keys = {}
        self.models = {
            "gemini": "gemini-2.5-flash",
            "openrouter": "meta-llama/llama-3.3-70b-instruct:free"
        }
        self._load_settings()

    def _load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.api_keys['gemini'] = data.get('api_key') # legacy, mas ainda funfa
                    self.api_keys['openrouter'] = data.get('openrouter_key')
                    if data.get('gemini_model'):
                        self.models['gemini'] = data.get('gemini_model')
                    if data.get('openrouter_model'):
                        self.models['openrouter'] = data.get('openrouter_model')
                    if data.get('openrouter_vision_model'):
                        self.models['openrouter_vision'] = data.get('openrouter_vision_model')
                    
                    # checando chaves aninhadas caso mude a estrutura
                    if 'keys' in data:
                        self.api_keys.update(data['keys'])

                    # já configura o gemini se tiver a chave
                    if self.api_keys.get('gemini'):
                        genai.configure(api_key=self.api_keys['gemini'])
            except Exception as e:
                print(f"erro ao carregar configurações no llmmanager: {e}")

    def generate_response(self, text, image_b64=None, provider='gemini', system_instruction=None):
        if provider == 'gemini':
            return self._generate_gemini(text, image_b64, system_instruction)
        elif provider == 'openrouter':
            return self._generate_openrouter(text, image_b64, system_instruction)
        else:
            return "erro: provedor de llm desconhecido."

    def _generate_gemini(self, text, image_b64, system_instruction):
        if not self.api_keys.get('gemini'):
            return "por favor, configure sua key do gemini primeiro."

        try:
            model = genai.GenerativeModel(self.models['gemini'])
            content = []
            
            if system_instruction:
               # gemini prefere instrução no init, mas assim tbm rola:
               combined_text = f"{system_instruction}\n\n{text}"
            else:
               combined_text = text

            content.append(combined_text)

            if image_b64:
                image_data = base64.b64decode(image_b64)
                image = Image.open(BytesIO(image_data))
                content.append(image)

            response = model.generate_content(content)
            return response.text.lower()
        except Exception as e:
            return f"erro no gemini: {str(e)}"

    def _generate_openrouter(self, text, image_b64, system_instruction):
        key = self.api_keys.get('openrouter')
        if not key:
            return "por favor, configure sua key do openrouter primeiro."

        url = "https://openrouter.ai/api/v1/chat/completions"
        print(f"DEBUG: url do openrouter: {url} | modelo: {self.models['openrouter']}")
        
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000", # openrouter pede isso
            "X-Title": "Assistente IA"
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        user_content = []
        if text:
            user_content.append({"type": "text", "text": text})
        
        if image_b64:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_b64}"
                }
            })

        messages.append({"role": "user", "content": user_content})

        # escolhendo o modelo
        current_model = self.models['openrouter']
        if image_b64:
            # se tem imagem, usa o modelo de visão, senão tenta o principal
            current_model = self.models.get('openrouter_vision', "nvidia/nemotron-nano-12b-v2-vl:free")
            print(f"DEBUG: trocando para modelo de visão: {current_model}")

        data = {
            "model": current_model,
            "messages": messages
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 404:
                return f"erro 404: url não encontrada ou modelo inválido ({self.models['openrouter']})"
            
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].lower()
            else:
                return "erro: resposta vazia do openrouter."
        except Exception as e:
             return f"erro no openrouter: {str(e)}"

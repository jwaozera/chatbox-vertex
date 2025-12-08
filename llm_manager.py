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
                    self.api_keys['gemini'] = data.get('api_key') # Legacy support
                    self.api_keys['openrouter'] = data.get('openrouter_key')
                    if data.get('gemini_model'):
                        self.models['gemini'] = data.get('gemini_model')
                    if data.get('openrouter_model'):
                        self.models['openrouter'] = data.get('openrouter_model')
                    if data.get('openrouter_vision_model'):
                        self.models['openrouter_vision'] = data.get('openrouter_vision_model')
                    
                    # Also check for specific nested keys if we change structure
                    if 'keys' in data:
                        self.api_keys.update(data['keys'])

                    # Configure Gemini immediately if key is present
                    if self.api_keys.get('gemini'):
                        genai.configure(api_key=self.api_keys['gemini'])
            except Exception as e:
                print(f"Error loading settings in LLMManager: {e}")

    def generate_response(self, text, image_b64=None, provider='gemini', system_instruction=None):
        if provider == 'gemini':
            return self._generate_gemini(text, image_b64, system_instruction)
        elif provider == 'openrouter':
            return self._generate_openrouter(text, image_b64, system_instruction)
        else:
            return "Erro: Provedor de LLM desconhecido."

    def _generate_gemini(self, text, image_b64, system_instruction):
        if not self.api_keys.get('gemini'):
            return "Por favor, configure sua KEY do Gemini primeiro."

        try:
            model = genai.GenerativeModel(self.models['gemini'])
            content = []
            
            if system_instruction:
               # Gemini supports system instructions better at model init usually, but for simple calls:
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
            return f"Erro no Gemini: {str(e)}"

    def _generate_openrouter(self, text, image_b64, system_instruction):
        key = self.api_keys.get('openrouter')
        if not key:
            return "Por favor, configure sua KEY do OpenRouter primeiro."

        url = "https://openrouter.ai/api/v1/chat/completions"
        print(f"DEBUG: OpenRouter Request URL: {url} | Model: {self.models['openrouter']}")
        
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter, using dummy
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

        # Determine which model to use
        current_model = self.models['openrouter']
        if image_b64:
            # Use specific vision model if available, otherwise fallback to main
            # Default fallback if key missing is the main model itself
            current_model = self.models.get('openrouter_vision', "nvidia/nemotron-nano-12b-v2-vl:free")
            print(f"DEBUG: Switching to Vision Model: {current_model}")

        data = {
            "model": current_model,
            "messages": messages
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 404:
                return f"Erro 404: URL não encontrada ou modelo inválido ({self.models['openrouter']})"
            
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].lower()
            else:
                return "Erro: Resposta vazia do OpenRouter."
        except Exception as e:
             return f"Erro no OpenRouter: {str(e)}"

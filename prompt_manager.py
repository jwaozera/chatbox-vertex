import json
import os
import uuid

PROMPTS_FILE = 'prompts.json'

DEFAULT_PROMPTS = [
    {
        "id": "default",
        "title": "Assistente Padrão (Vertex)",
        "persona": "Você é um assistente de desktop avançado.",
        "task": "Aja naturalmente, como um parceiro de trabalho.",
        "instructions": "Responda sempre em português do brasil. Use letras minúsculas. Se tiver imagem, analise e descreva detalhadamente.",
        "output_format": "Markdown",
        "tags": ["default", "general"],
        "editable": False
    },
    {
        "id": "code_reviewer",
        "title": "Code Reviewer",
        "persona": "Você é um Engenheiro de Software Sênior especialista em Clean Code e Arquitetura.",
        "task": "Analise o código fornecido ou a imagem de código em busca de bugs, melhorias de performance e legibilidade.",
        "instructions": "Seja rigoroso mas construtivo. Sugira refatorações específicas. Aponte problemas de segurança. Se for imagem de erro, explique a causa.",
        "output_format": "Markdown com blocos de código.",
        "tags": ["coding", "review", "dev"],
        "editable": True
    },
    {
        "id": "ux_designer",
        "title": "UX/UI Designer",
        "persona": "Você é um especialista em UX Design moderno focado em acessibilidade.",
        "task": "Analise a interface (imagem) ou descrição e sugira melhorias visuais e de usabilidade.",
        "instructions": "Foque em heurísticas de Nielsen. Verifique contraste, hierarquia visual e consistência. Seja crítico com layouts confusos.",
        "output_format": "Lista de pontos de melhoria com sugestões práticas.",
        "tags": ["design", "ux", "ui"],
        "editable": True
    },
    {
        "id": "study_tutor",
        "title": "Tutor Socrático",
        "persona": "Você é um professor sábio que utiliza o método socrático.",
        "task": "Ajude o usuário a aprender, não apenas dando a resposta, mas guiando o pensamento.",
        "instructions": "Faça perguntas que levem o usuário à conclusão. Simplifique conceitos complexos. Use analogias.",
        "output_format": "Conversacional e encorajador.",
        "tags": ["study", "learning", "tutor"],
        "editable": True
    }
]

class PromptManager:
    def __init__(self, filepath=PROMPTS_FILE):
        self.filepath = filepath
        self.prompts = []
        self.load_prompts()

    def load_prompts(self):
        if not os.path.exists(self.filepath):
            self.prompts = DEFAULT_PROMPTS
            self.save_prompts()
        else:
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.prompts = json.load(f)
            except Exception as e:
                print(f"Error loading prompts: {e}")
                self.prompts = DEFAULT_PROMPTS

    def save_prompts(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving prompts: {e}")
            return False

    def get_all_prompts(self):
        return self.prompts

    def save_prompt(self, prompt_data):
        if not prompt_data.get('id'):
            prompt_data['id'] = str(uuid.uuid4())
            prompt_data['editable'] = True # Ensure new prompts are editable
        
        # Check if updating existing
        for i, p in enumerate(self.prompts):
            if p['id'] == prompt_data['id']:
                # Update but preserve some fields if needed, or full overwrite
                self.prompts[i] = prompt_data
                self.save_prompts()
                return prompt_data
        
        # New prompt
        self.prompts.append(prompt_data)
        self.save_prompts()
        return prompt_data

    def delete_prompt(self, prompt_id):
        initial_len = len(self.prompts)
        self.prompts = [p for p in self.prompts if p['id'] != prompt_id]
        if len(self.prompts) < initial_len:
            self.save_prompts()
            return True
        return False

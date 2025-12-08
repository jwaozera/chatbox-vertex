import json
import os
import datetime

class MCPManager:
    def __init__(self, context_file='mcp_context.json'):
        self.context_file = context_file
        self.context = self._load_context()

    def _load_context(self):
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading MCP context: {e}")
                return self._default_schema()
        else:
            return self._default_schema()

    def _default_schema(self):
        return {
            "user_profile": {},
            "active_tasks": [],
            "session_history": [],
            "long_term_memory": {},
            "last_updated": str(datetime.datetime.now())
        }

    def save_context(self):
        self.context["last_updated"] = str(datetime.datetime.now())
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving MCP context: {e}")

    def update_profile(self, key, value):
        self.context["user_profile"][key] = value
        self.save_context()

    def add_task(self, task):
        self.context["active_tasks"].append({
            "task": task,
            "status": "pending",
            "created_at": str(datetime.datetime.now())
        })
        self.save_context()

    def get_context_string(self):
        # Format for LLM injection
        response = "=== CONTEXTO (MCP) ===\n"
        if self.context.get("user_profile"):
            response += f"Perfil Usuário: {json.dumps(self.context['user_profile'], ensure_ascii=False)}\n"
        
        tasks = [t for t in self.context.get("active_tasks", []) if t.get('status') != 'completed']
        if tasks:
            response += f"Tarefas Ativas: {len(tasks)}\n"
            for t in tasks[:3]: # Limit to 3 recent
                response += f"- {t.get('task')} ({t.get('status')})\n"
        
        return response

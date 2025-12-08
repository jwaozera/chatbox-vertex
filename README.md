# 🤖 Chatbox Vertex

**Chatbox Vertex** é um assistente virtual de desktop moderno e flutuante, projetado para ser seu parceiro de trabalho com IA. Ele integra modelos de linguagem avançados (como Google Gemini e modelos via OpenRouter), visão computacional, reconhecimento de voz e um sistema de memória de longo prazo (RAG).

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue" alt="Python">
  <img src="https://img.shields.io/badge/UI-PyWebview-green" alt="PyWebview">
  <img src="https://img.shields.io/badge/AI-Gemini%20%7C%20OpenRouter-orange" alt="AI Models">
</p>

---

## ✨ Funcionalidades Principais

*   **📝 Multi-LLM Suporte**: Alterne facilmente entre **Google Gemini** (padrão) e **OpenRouter** (Llama 3, Mistral, etc) dependendo da sua necessidade.
*   **👁️ Visão Computacional (Screen Analysis)**: O assistente pode "ver" a sua tela. Com um clique no ícone do olho, ele captura o conteúdo do seu monitor principal e permite que você faça perguntas sobre o que está vendo (ex: "Explique este código", "Resuma este email").
*   **🎙️ Reconhecimento de Voz**: Converse naturalmente usando o microfone. O sistema transcreve sua fala para texto automaticamente.
*   **🧠 Memória RAG (Retrieval-Augmented Generation)**: Possui um sistema de memória persistente usando **ChromaDB**. O assistente lembra de informações importantes passadas em conversas anteriores para fornecer respostas mais contextuais.
*   **📚 Biblioteca de Prompts (Personas)**: Crie, edite e ative diferentes "personas" para a IA.
    *   *Exemplos:* "Revisor de Código", "Professor de Inglês", "Especialista em UX".
    *   Cada prompt define o tom, a tarefa e o formato de saída da IA.
*   **🎨 UI Moderna (Glassmorphism)**: Interface flutuante, translúcida e minimalista que fica sobre suas outras janelas sem atrapalhar.

---

## 🛠️ Instalação

Certifique-se de ter o **Python 3.10+** instalado.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/jwaozera/chatbox-vertex.git
    cd chatbox-vertex
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Dependências principais: `pywebview`, `google-generativeai`, `chromadb`, `SpeechRecognition`, `pyaudio`, `mss`, `Pillow`)*

    > **Nota sobre Áudio no Windows:** Se tiver problemas com o `pyaudio`, pode ser necessário instalar o `pipwin` primeiro ou baixar o wheel compatível.

3.  **Configuração Inicial:**
    Ao iniciar o app pela primeira vez, ele criará automaticamente os arquivos necessários (`settings.json`, `prompts.json` e as pastas do banco de dados).

---

## 🚀 Como Usar

Para iniciar o assistente, execute o arquivo principal:

```bash
python main.py
```

### ⚙️ Configuração (API Keys)
1.  Clique no ícone de engrenagem **(⚙️)** no canto superior direito.
2.  Insira sua **Gemini API Key** (obtenha no Google AI Studio) ou **OpenRouter Key**.
3.  Escolha o modelo desejado (ex: `gemini-2.5-flash`).
4.  Clique em "Salvar & Aplicar".

### 💬 Chat e Comandos
*   **Enviar Mensagem:** Digite e pressione Enter ou clique no avião de papel.
*   **Ver Tela (👁️)**: Clique no ícone do olho. O app minimizará brevemente, tirará um print da tela e enviará para a IA junto com sua pergunta (ou "o que tem na minha tela?" se vazio).
*   **Gravar Áudio (🎙️)**: Clique no microfone para começar a falar. Clique novamente para parar e transcrever.
*   **Biblioteca de Prompts (📖)**: Clique no ícone de livro para abrir a biblioteca.
    *   Clique em um card para **Ativar** aquela persona (o card ficará azul).
    *   Clique novamente para **Desativar** (modo padrão).
    *   Use o botão "Novo Prompt" para criar seus próprios comandos customizados.

---

## 📂 Estrutura do Projeto

*   `main.py`: Ponto de entrada. Gerencia a janela `pywebview` e integra o backend Python com o frontend JS.
*   `llm_manager.py`: Gerencia as chamadas para as APIs (Gemini/OpenRouter).
*   `rag_manager.py`: Gerencia o banco de dados vetorial (ChromaDB) para memória de longo prazo.
*   `prompt_manager.py`: CRUD para a biblioteca de prompts (salva em `prompts.json`).
*   `mcp_manager.py`: Gerencia o contexto do usuário e tarefas pendentes.
*   `web/`: Contém o frontend da aplicação.
    *   `index.html`: Estrutura da interface.
    *   `style.css`: Estilização (Tailwind + CSS Customizado).
    *   `app.js`: Lógica do frontend e comunicação com o Python.

---

## 🛡️ Privacidade

*   As capturas de tela são processadas localmente e enviadas **apenas** para o provedor de LLM escolhido (Google ou OpenRouter) no momento da análise. Nenhuma imagem é salva permanentemente no disco, exceto em cache temporário de memória.
*   O banco de dados RAG é armazenado localmente na sua máquina (`chroma_db/`).

---

**Desenvolvido com ❤️ e Python.**

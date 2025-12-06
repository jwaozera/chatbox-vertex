# Relatório do Projeto: Assistente de Desktop AI

## 1. Resumo Explicativo do Funcionamento

### Fluxo de Execução
A aplicação funciona como um assistente de desktop "flutuante" e transparente.
1.  **Inicialização ([main.py](file:///c:/Users/joaoe/OneDrive/%C3%81rea%20de%20Trabalho/ProjetaoGPT/FirstTry/main.py))**:
    *   O Python inicia e configura a janela usando a biblioteca `pywebview`.
    *   É aplicada uma correção de transparência (delay + resize) para garantir que a janela não tenha fundo opaco no Windows.
    *   O servidor backend é exposto para o frontend através da classe [Api](file:///c:/Users/joaoe/OneDrive/%C3%81rea%20de%20Trabalho/ProjetaoGPT/FirstTry/main.py#20-179).
2.  **Interface do Usuário (Frontend)**:
    *   Construída com **HTML5, Tailwind CSS e Vanilla JavaScript**.
    *   O usuário interage com a janela (arrastável) para digitar textos ou usar comandos de voz.
3.  **Comunicação (Bridge)**:
    *   Quando o usuário envia uma mensagem, o JavaScript chama `pywebview.api.send_message()`.
    *   O Python processa a solicitação.
4.  **Processamento AI (`google.generativeai`)**:
    *   O backend envia o texto (e opcionalmente um print da tela capturado via `mss`) para a API do Google Gemini.
    *   A resposta é retornada ao JavaScript e renderizada na tela.

### Bibliotecas Principais
*   **webview (pywebview)**: Cria a janela nativa que renderiza o HTML/CSS/JS. Permite a comunicação bidirecional Python-JS.
*   **google.generativeai**: SDK oficial para comunicar com os modelos Gemini do Google.
*   **mss**: Biblioteca rápida para captura de tela (usada na função "Analyze Screen").
*   **SpeechRecognition / PyAudio**: Captura e processamento de áudio para comandos de voz.
*   **Pillow (PIL)**: Manipulação de imagens antes do envio para a IA.

### Planejamento e Execução
O desenvolvimento seguiu uma abordagem ágil e modular:
1.  **Estrutura Base**: Configuração inicial do `pywebview` e integração básica com Gemini.
2.  **Frontend**: Desenvolvimento da interface moderna com efeito "glassmorphism" (vidro) usando CSS.
3.  **Funcionalidades**: Implementação incremental de captura de tela, áudio e configurações persistentes (JSON).
4.  **Refinamento**: Correção de problemas específicos de plataforma (transparência no Windows) e melhorias de UX (botão de fechar, layout de configurações).

---

## 2. Análise de Requisitos

Abaixo, a análise de conformidade con os requisitos solicitados:

| Requisito | Status | Observação |
| :--- | :---: | :--- |
| **Desenvolvida obrigatoriamente em Python (.py ou .ipynb)** | ✅ **Atendido** | O núcleo da aplicação é o arquivo [main.py](file:///c:/Users/joaoe/OneDrive/%C3%81rea%20de%20Trabalho/ProjetaoGPT/FirstTry/main.py). |
| **Permitir que o usuário digite uma mensagem na interface** | ✅ **Atendido** | Existe um campo de texto (`textarea`) na parte inferior da interface. |
| **Enviar essa mensagem para um modelo de IA** | ✅ **Atendido** | A mensagem é enviada para o modelo `gemini-2.0-flash` via API. |
| **Exibir a resposta do chatbot na própria interface** | ✅ **Atendido** | As respostas são inseridas dinamicamente no DOM da página dentro de "bolhas" de mensagem. |
| **Permitir que uma conversação seja mantida** | ✅ **Atendido** | A aplicação permanece aberta e responsiva para múltiplas interações até que o usuário decida fechá-la. |

**Conclusão**: A aplicação atende integralmente a todos os requisitos funcionais e técnicos listados.


// elementos do dom
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const visionBtn = document.getElementById('vision-btn');
const settingsBtn = document.getElementById('settings-btn');
const closeSettingsBtn = document.getElementById('close-settings-btn');
const settingsModal = document.getElementById('settings-modal');
const saveSettingsBtn = document.getElementById('save-settings-btn');
const closeAppBtn = document.getElementById('close-app-btn');

// elementos da biblioteca de prompts
const libraryBtn = document.getElementById('library-btn');
const libraryModal = document.getElementById('library-modal');
const closeLibraryBtn = document.getElementById('close-library-btn');
const promptList = document.getElementById('prompt-list');
const newPromptBtn = document.getElementById('new-prompt-btn');
const promptEditor = document.getElementById('prompt-editor');
const emptyEditorState = document.getElementById('empty-editor-state');
const savePromptBtn = document.getElementById('save-prompt-btn');
const deletePromptBtn = document.getElementById('delete-prompt-btn');

// inputs do editor
const editTitle = document.getElementById('edit-title');
const editTags = document.getElementById('edit-tags');
const editOutput = document.getElementById('edit-output');
const editPersona = document.getElementById('edit-persona');
const editTask = document.getElementById('edit-task');
const editInstructions = document.getElementById('edit-instructions');
const editId = document.getElementById('edit-id');

// inputs de configuração
const geminiKeyInput = document.getElementById('gemini-key-input');
const openrouterKeyInput = document.getElementById('openrouter-key-input');
const geminiModelInput = document.getElementById('gemini-model-input');
const openrouterModelInput = document.getElementById('openrouter-model-input');
const ragToggle = document.getElementById('rag-toggle');
const providerTabs = document.querySelectorAll('.provider-tab');
const ragStatus = document.getElementById('rag-status');
const providerLabel = document.getElementById('provider-label');

// estado da aplicação
let selectedProvider = 'gemini';
let isRecording = false;
let activePrompt = null; // prompt de sistema ativo no momento
let promptsCache = [];
let editingPromptId = null;

// inicialização
window.addEventListener('pywebviewready', async () => {
    console.log('pywebview pronto');
    await loadSettings();
    await loadPrompts();
    userInput.focus();
});

// --- lógica da biblioteca de prompts ---

// carrega os prompts do backend
async function loadPrompts() {
    try {
        promptsCache = await window.pywebview.api.get_prompts();
        renderPrompts();
    } catch (e) {
        console.error("erro ao carregar prompts", e);
    }
}

// renderiza a lista de prompts na sidebar
function renderPrompts() {
    promptList.innerHTML = '';

    // ordena: ativo primeiro, depois alfabético
    const sortedPrompts = [...promptsCache].sort((a, b) => {
        if (activePrompt && a.id === activePrompt.id) return -1;
        if (activePrompt && b.id === activePrompt.id) return 1;
        return a.title.localeCompare(b.title);
    });

    sortedPrompts.forEach(prompt => {
        const card = document.createElement('div');
        const isActive = activePrompt && activePrompt.id === prompt.id;

        card.className = `prompt-card ${isActive ? 'active-prompt' : ''}`;

        const tagsHtml = (prompt.tags || []).map(tag => `<span class="prompt-tag">${tag}</span>`).join('');

        card.innerHTML = `
            <div class="card-title flex justify-between items-center">
                <span>${prompt.title}</span>
                ${isActive ? '<i class="fa-solid fa-check-circle text-blue-400"></i>' : ''}
            </div>
            <div class="card-desc">${prompt.persona || prompt.instructions}</div>
            <div>${tagsHtml}</div>
        `;

        // clique para ativar/desativar
        card.addEventListener('click', (e) => {
            if (activePrompt && activePrompt.id === prompt.id) {
                // desativa se já estiver ativo
                activePrompt = null;
                addMessage('system', 'prompt desativado. voltando ao modo padrão.');
            } else {
                activePrompt = prompt;
                addMessage('system', `prompt ativado: <strong>${prompt.title}</strong>`);
            }
            renderPrompts(); // renderiza novemente pra mostrar o estado atual
            // habilita o editor pra esse prompt também
            openEditor(prompt);
        });

        promptList.appendChild(card);
    });
}

// abre o editor com os dados do prompt
function openEditor(prompt) {
    editingPromptId = prompt.id;

    editTitle.value = prompt.title || '';
    editTags.value = (prompt.tags || []).join(', ');
    editOutput.value = prompt.output_format || '';
    editPersona.value = prompt.persona || '';
    editTask.value = prompt.task || '';
    editInstructions.value = prompt.instructions || '';
    editId.value = prompt.id || '';

    // mostra o editor, esconde o estado vazio
    promptEditor.classList.remove('hidden');
    emptyEditorState.classList.add('hidden');
}

// limpa o editor para um novo prompt
function clearEditor() {
    editingPromptId = null;
    editTitle.value = 'Novo Prompt';
    editTags.value = '';
    editOutput.value = 'Markdown';
    editPersona.value = '';
    editTask.value = '';
    editInstructions.value = '';
    editId.value = '';

    promptEditor.classList.remove('hidden');
    emptyEditorState.classList.add('hidden');
}

// listeners de eventos da biblioteca
libraryBtn.addEventListener('click', () => {
    libraryModal.classList.remove('hidden');
    loadPrompts();
});

closeLibraryBtn.addEventListener('click', () => {
    libraryModal.classList.add('hidden');
});

newPromptBtn.addEventListener('click', () => {
    clearEditor();
});

savePromptBtn.addEventListener('click', async () => {
    const newPrompt = {
        id: editingPromptId || undefined, // undefined deixa o backend gerar o id
        title: editTitle.value,
        tags: editTags.value.split(',').map(t => t.trim()).filter(t => t),
        output_format: editOutput.value,
        persona: editPersona.value,
        task: editTask.value,
        instructions: editInstructions.value,
        editable: true
    };

    try {
        const saved = await window.pywebview.api.save_prompt(newPrompt);
        if (saved) {
            // atualiza o cache
            await loadPrompts();
            // se editou o prompt ativo, atualiza ele tbm
            if (activePrompt && activePrompt.id === saved.id) {
                activePrompt = saved;
            }
            addMessage('system', 'prompt salvo com sucesso.');
        }
    } catch (e) {
        console.error("erro ao salvar prompt", e);
        addMessage('system', 'erro ao salvar prompt.');
    }
});

deletePromptBtn.addEventListener('click', async () => {
    if (!editingPromptId) return;

    if (confirm('tem certeza que quer excluir esse prompt?')) {
        try {
            const result = await window.pywebview.api.delete_prompt(editingPromptId);
            if (result) {
                if (activePrompt && activePrompt.id === editingPromptId) {
                    activePrompt = null;
                }
                editingPromptId = null;
                promptEditor.classList.add('hidden');
                emptyEditorState.classList.remove('hidden');
                await loadPrompts();
                addMessage('system', 'prompt excluído.');
            }
        } catch (e) {
            console.error("erro ao deletar", e);
        }
    }
});

// --- lógica de configurações ---

async function loadSettings() {
    try {
        const settings = await window.pywebview.api.get_settings();

        // chaves api
        geminiKeyInput.value = settings.api_keys?.gemini || '';
        openrouterKeyInput.value = settings.api_keys?.openrouter || '';

        // modelos
        geminiModelInput.value = settings.models?.gemini || 'gemini-2.5-flash';
        openrouterModelInput.value = settings.models?.openrouter || 'meta-llama/llama-3.3-70b-instruct:free';

        // toggles (rag apenas, web removido)
        ragToggle.checked = settings.rag_enabled;

        updateStatusIndicators(settings.rag_enabled);

        // provedor atual
        selectedProvider = settings.current_provider || 'gemini';
        updateProviderTabs(selectedProvider);
        updateProviderLabel(selectedProvider);

    } catch (e) {
        console.error("erro ao carregar as configurações", e);
    }
}

function updateProviderTabs(provider) {
    selectedProvider = provider;
    providerTabs.forEach(tab => {
        if (tab.dataset.provider === provider) {
            tab.classList.add('bg-blue-600', 'text-white', 'shadow');
            tab.classList.remove('text-gray-400');
        } else {
            tab.classList.remove('bg-blue-600', 'text-white', 'shadow');
            tab.classList.add('text-gray-400');
        }
    });
}

function updateProviderLabel(provider) {
    if (providerLabel) {
        providerLabel.innerText = provider.toUpperCase();
        if (provider === 'gemini') {
            providerLabel.className = 'text-[8px] text-blue-400 uppercase tracking-wide leading-tight';
        } else {
            providerLabel.className = 'text-[8px] text-purple-400 uppercase tracking-wide leading-tight';
        }
    }
}

function updateStatusIndicators(rag) {
    if (rag) {
        ragStatus.classList.remove('text-gray-600');
        ragStatus.classList.add('text-blue-400', 'font-bold');
    } else {
        ragStatus.classList.add('text-gray-600');
        ragStatus.classList.remove('text-blue-400', 'font-bold');
    }
    // status web removido
}

providerTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        updateProviderTabs(tab.dataset.provider);
    });
});

saveSettingsBtn.addEventListener('click', async () => {
    const settings = {
        api_keys: {
            gemini: geminiKeyInput.value,
            openrouter: openrouterKeyInput.value,
        },
        models: {
            gemini: geminiModelInput.value,
            openrouter: openrouterModelInput.value,
        },
        rag_enabled: ragToggle.checked,
        web_enabled: false, // força web desligada
        provider: selectedProvider
    };

    const success = await window.pywebview.api.save_settings(settings);
    if (success) {
        updateStatusIndicators(ragToggle.checked);
        updateProviderLabel(selectedProvider);
        toggleModal(false);
        addMessage('system', 'configurações salvas e aplicadas.');
    }
});

// ações da interface
settingsBtn.addEventListener('click', () => toggleModal(true));
closeSettingsBtn.addEventListener('click', () => toggleModal(false));
closeAppBtn.addEventListener('click', () => window.pywebview.api.close_app());

function toggleModal(show) {
    if (show) {
        settingsModal.classList.remove('hidden');
    } else {
        settingsModal.classList.add('hidden');
    }
}

// --- lógica do chat ---

function addMessage(sender, text) {
    const div = document.createElement('div');
    if (sender === 'system') {
        div.className = 'self-center text-xs text-gray-500 my-2';
        div.innerHTML = text; // permite html nas msgs de sistema
    } else {
        div.className = 'flex flex-col space-y-1 animate-enter';

        let name = sender === 'user' ? 'Você' : 'Vertex';
        // adiciona o nome da persona se estiver ativa
        if (sender === 'ai' && activePrompt) {
            name += ` <span class="text-[8px] bg-blue-900 px-1 rounded text-blue-200">${activePrompt.title}</span>`;
        }

        const bubbleClass = sender === 'user' ? 'message-user' : 'message-ai';

        div.innerHTML = `
            <div class="self-start text-[10px] text-gray-500 ml-1 mb-1 ${sender === 'user' ? 'self-end mr-1' : ''}">${name}</div>
            <div class="${bubbleClass} px-4 py-3 max-w-[90%] text-sm leading-relaxed backdrop-blur-md markdown-body">
                ${marked.parse(text)}
            </div>
        `;
    }
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    // reseta a altura do input
    userInput.style.height = 'auto';
    userInput.value = '';

    addMessage('user', text);

    // estado de "pensando"
    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = 'flex flex-col space-y-1 animate-enter';
    typingDiv.innerHTML = `
        <div class="message-ai px-4 py-3 max-w-[90%] text-gray-400 text-sm">
            <i class="fa-solid fa-circle-notch fa-spin"></i> pensando...
        </div>`;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // passa o prompt ativo
        const response = await window.pywebview.api.send_message(text, null, activePrompt);

        const el = document.getElementById(typingId);
        if (el) el.remove();

        addMessage('ai', response);
    } catch (e) {
        const el = document.getElementById(typingId);
        if (el) el.remove();
        addMessage('system', 'erro: ' + e);
    }
}

sendBtn.addEventListener('click', handleSend);

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
    // auto resize
    setTimeout(() => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    }, 0);
});

// botão de visão
visionBtn.addEventListener('click', async () => {
    const prompt = userInput.value.trim() || 'o que tem na minha tela?';

    addMessage('user', '[análise de visão]: ' + prompt);
    userInput.value = '';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'self-center text-xs text-blue-400 my-2';
    typingDiv.innerHTML = '<i class="fa-solid fa-eye fa-bounce"></i> analisando tela...';
    chatBox.appendChild(typingDiv);

    try {
        // passa o prompt ativo
        const response = await window.pywebview.api.analyze_screen(prompt, activePrompt);
        typingDiv.remove();
        addMessage('ai', response);
    } catch (e) {
        typingDiv.remove();
        addMessage('system', 'erro na visão: ' + e);
    }
});

// botão do microfone
micBtn.addEventListener('click', async () => {
    isRecording = !isRecording;

    if (isRecording) {
        micBtn.classList.remove('text-gray-400');
        micBtn.classList.add('text-red-500', 'animate-pulse');
        const status = await window.pywebview.api.toggle_recording(true);
        if (status) addMessage('system', status);
    } else {
        micBtn.classList.add('text-gray-400');
        micBtn.classList.remove('text-red-500', 'animate-pulse');

        const typingDiv = document.createElement('div');
        typingDiv.className = 'self-center text-xs text-gray-500 my-2';
        typingDiv.innerText = 'processando áudio...';
        chatBox.appendChild(typingDiv);

        const text = await window.pywebview.api.toggle_recording(false);
        typingDiv.remove();

        if (text) {
            userInput.value = text;
            userInput.focus();
        } else {
            addMessage('system', 'não foi possível entender o áudio.');
        }
    }
});

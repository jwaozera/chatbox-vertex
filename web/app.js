
// DOM Elements
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

// Settings Inputs
const geminiKeyInput = document.getElementById('gemini-key-input');
const openrouterKeyInput = document.getElementById('openrouter-key-input');
const geminiModelInput = document.getElementById('gemini-model-input');
const openrouterModelInput = document.getElementById('openrouter-model-input');
const ragToggle = document.getElementById('rag-toggle');

const providerTabs = document.querySelectorAll('.provider-tab');
const ragStatus = document.getElementById('rag-status');

const providerLabel = document.getElementById('provider-label'); // NEW

// State
let selectedProvider = 'gemini';
let isRecording = false;

// Initialize
window.addEventListener('pywebviewready', async () => {
    console.log('PyWebview Ready');
    await loadSettings();
    userInput.focus();
});

// Settings Logic
async function loadSettings() {
    try {
        const settings = await window.pywebview.api.get_settings();

        // Keys
        geminiKeyInput.value = settings.api_keys?.gemini || '';
        openrouterKeyInput.value = settings.api_keys?.openrouter || '';

        // Models
        geminiModelInput.value = settings.models?.gemini || 'gemini-2.5-flash';
        openrouterModelInput.value = settings.models?.openrouter || 'meta-llama/llama-3.3-70b-instruct:free';

        // Toggles
        ragToggle.checked = settings.rag_enabled;

        updateStatusIndicators(settings.rag_enabled);

        // Provider
        selectedProvider = settings.current_provider || 'gemini';
        updateProviderTabs(selectedProvider);
        updateProviderLabel(selectedProvider); // NEW

    } catch (e) {
        console.error("Error loading settings", e);
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

        provider: selectedProvider
    };

    const success = await window.pywebview.api.save_settings(settings);
    if (success) {
        updateStatusIndicators(ragToggle.checked);
        updateProviderLabel(selectedProvider);
        toggleModal(false);
        addMessage('system', 'Configurações salvas e aplicadas.');
    }
});

// UI Actions
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

// Chat Logic
function addMessage(sender, text) {
    const div = document.createElement('div');
    if (sender === 'system') {
        div.className = 'self-center text-xs text-gray-500 my-2';
        div.innerText = text;
    } else {
        div.className = 'flex flex-col space-y-1 animate-enter';
        const name = sender === 'user' ? 'Você' : 'Vertex';
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

    // reset input height
    userInput.style.height = 'auto';
    userInput.value = '';

    addMessage('user', text);

    // Show typing state
    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = 'flex flex-col space-y-1 animate-enter';
    typingDiv.innerHTML = `
        <div class="message-ai px-4 py-3 max-w-[90%] text-gray-400 text-sm">
            <i class="fa-solid fa-circle-notch fa-spin"></i> Pensando...
        </div>`;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await window.pywebview.api.send_message(text);

        // Remove typing
        const el = document.getElementById(typingId);
        if (el) el.remove();

        addMessage('ai', response);
    } catch (e) {
        const el = document.getElementById(typingId);
        if (el) el.remove();
        addMessage('system', 'Erro: ' + e);
    }
}

sendBtn.addEventListener('click', handleSend);

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
    // Auto resize
    setTimeout(() => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    }, 0);
});

// Vision
visionBtn.addEventListener('click', async () => {
    const prompt = userInput.value.trim() || 'o que tem na minha tela?';

    addMessage('user', '[Análise de Visão]: ' + prompt);
    userInput.value = '';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'self-center text-xs text-blue-400 my-2';
    typingDiv.innerHTML = '<i class="fa-solid fa-eye fa-bounce"></i> Analisando tela...';
    chatBox.appendChild(typingDiv);

    try {
        const response = await window.pywebview.api.analyze_screen(prompt);
        typingDiv.remove();
        addMessage('ai', response);
    } catch (e) {
        typingDiv.remove();
        addMessage('system', 'Erro na visão: ' + e);
    }
});

// Mic
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
        typingDiv.innerText = 'Processando áudio...';
        chatBox.appendChild(typingDiv);

        const text = await window.pywebview.api.toggle_recording(false);
        typingDiv.remove();

        if (text) {
            userInput.value = text;
            userInput.focus();
            // Optional: Auto send
            // handleSend();
        } else {
            addMessage('system', 'Não foi possível entender o áudio.');
        }
    }
});

const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const visionBtn = document.getElementById('vision-btn');
const micBtn = document.getElementById('mic-btn');
const settingsModal = document.getElementById('settings-modal');
const apiKeyInput = document.getElementById('api-key-input');
const saveKeyBtn = document.getElementById('save-key-btn');
const settingsBtn = document.getElementById('settings-btn');
const closeAppBtn = document.getElementById('close-app-btn');

let isRecording = false;

// --- funções auxiliares ---

function addMessage(text, isUser = false, image = null) {
    const div = document.createElement('div');
    div.className = `flex flex-col space-y-1 ${isUser ? 'items-end' : 'items-start'}`;

    let contentHtml = '';

    if (image) {
        contentHtml += `<img src="data:image/png;base64,${image}" class="max-w-[150px] rounded-lg border border-gray-600 mb-1">`;
    }

    if (text) {
        contentHtml += `
            <div class="${isUser ? 'bg-blue-600 text-white' : 'bg-gray-800 bg-opacity-60 text-gray-200'} 
                        px-3 py-2 rounded-2xl ${isUser ? 'rounded-tr-none' : 'rounded-tl-none'} 
                        max-w-[85%] text-sm break-words whitespace-pre-wrap">
                ${text}
            </div>
        `;
    }

    div.innerHTML = contentHtml;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showLoading() {
    const div = document.createElement('div');
    div.id = 'loading-indicator';
    div.className = 'flex items-start';
    div.innerHTML = `
        <div class="bg-gray-800 bg-opacity-60 text-gray-400 px-3 py-2 rounded-2xl rounded-tl-none text-sm">
            pensando<span class="loading-dots"></span>
        </div>
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideLoading() {
    const el = document.getElementById('loading-indicator');
    if (el) el.remove();
}

// --- (listeners) ---

// redimensiona o input automaticamente
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if (this.value === '') this.style.height = 'auto';
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

const closeSettingsBtn = document.getElementById('close-settings-btn');

sendBtn.addEventListener('click', sendMessage);

settingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
    apiKeyInput.focus();
});

closeSettingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
});

// esc pra fechar o modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (!settingsModal.classList.contains('hidden')) {
            settingsModal.classList.add('hidden');
        }
    }
});

saveKeyBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    if (key) {
        pywebview.api.save_settings(key).then(() => {
            settingsModal.classList.add('hidden');
            addMessage("chave api salva!", false);
        });
    }
});

visionBtn.addEventListener('click', () => {
    addMessage("analisando tela...", true); // log da ação do usuário
    showLoading();
    // um delayzinho pra dar tempo da ui atualizar antes do screenshot travar ou esconder a janela
    setTimeout(() => {
        pywebview.api.analyze_screen(userInput.value).then(response => {
            hideLoading();
            addMessage(response, false);
        }).catch(err => {
            hideLoading();
            addMessage("erro: " + err, false);
        });
    }, 100);
});

micBtn.addEventListener('click', () => {
    if (!isRecording) {
        // começa a gravar
        isRecording = true;
        micBtn.classList.add('recording-pulse');
        pywebview.api.toggle_recording(true).then(() => {
            // começou
        });
    } else {
        // para de gravar
        isRecording = false;
        micBtn.classList.remove('recording-pulse');
        showLoading(); // transcrevendo...
        pywebview.api.toggle_recording(false).then(transcribedText => {
            hideLoading();
            if (transcribedText) {
                userInput.value = transcribedText;
                userInput.focus();
                // opcional: auto-enviar? melhor deixar o usuário revisar primeiro.
            } else {
                addMessage("não ouvi nada.", false);
            }
        });
    }
});


closeAppBtn.addEventListener('click', () => {
    pywebview.api.close_app();
});


// --- lógica principal ---

function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, true);
    userInput.value = '';
    userInput.style.height = 'auto';

    showLoading();

    pywebview.api.send_message(text).then(response => {
        hideLoading();
        addMessage(response, false);
    }).catch(err => {
        hideLoading();
        addMessage("erro: " + err, false);
    });
}

// --- inicialização ---

window.addEventListener('pywebviewready', () => {
    // checa se as configs existem
    pywebview.api.load_settings().then(key => {
        if (!key) {
            settingsModal.classList.remove('hidden');
        }
    });
});

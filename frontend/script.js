document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");

    // Model controls
    const modelToggle = document.getElementById("model-toggle");
    const modelPanel = document.getElementById("model-panel");
    const modelListEl = document.getElementById("model-list");
    const modelSearch = document.getElementById("model-search");
    const selectedChips = document.getElementById("selected-chips");
    const modelStatus = document.getElementById("model-status");

    // Track selection locally - declare early before fetchModels is called
    let currentSelected = [];

    // Initial welcome
    addMessage(
        "Hello! I'm your medical assistant 🤖. How can I help you today?",
        "bot"
    );

    // Fetch available models on start
    fetchModels();

    sendButton.addEventListener("click", handleUserInput);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleUserInput();
        }
    });

    // Toggle dropdown
    modelToggle.addEventListener('click', () => {
        const open = modelPanel.hidden === false;
        modelPanel.hidden = open;
        modelToggle.setAttribute('aria-expanded', String(!open));
        if (!open) modelSearch.focus();
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!document.getElementById('model-dropdown').contains(e.target)) {
            modelPanel.hidden = true;
            modelToggle.setAttribute('aria-expanded', 'false');
        }
    });

    // Search
    modelSearch.addEventListener('input', () => {
        const q = modelSearch.value.toLowerCase();
        Array.from(modelListEl.children).forEach(li => {
            const m = li.dataset.model.toLowerCase();
            li.style.display = m.includes(q) ? '' : 'none';
        });
    });

    // Multi-mode toggle
    multiModeCheckbox.addEventListener('change', () => {
        // keep current selection; UI changes accordingly
        renderSelectedChips(currentSelected);
    });

    // Keyboard: Esc closes
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            modelPanel.hidden = true;
            modelToggle.setAttribute('aria-expanded', 'false');
        }
    });

    function buildModelList(models, state) {
        console.log('🏗️ buildModelList called with:', { models, state });
        
        // reset
        modelListEl.innerHTML = '';
        currentSelected = [];

        if (!models || models.length === 0) {
            console.log('⚠️ No models provided');
            const info = document.createElement('li');
            info.textContent = 'No generative models available';
            info.style.opacity = 0.7;
            info.style.fontStyle = 'italic';
            modelListEl.appendChild(info);
            document.getElementById('model-panel-footer').textContent = 'Make sure Ollama is running and has models installed.';
            renderSelectedChips([]);
            return;
        }

        const stateModels = state.llm_models || (state.llm_model ? [state.llm_model] : []);
        console.log('📋 State models for matching:', stateModels);

        models.forEach(m => {
            const li = document.createElement('li');
            li.textContent = m;
            li.dataset.model = m;
            li.tabIndex = 0;
            
            // Check if this model matches any in state (handle version suffix like :latest)
            const isSelected = stateModels.some(sm => {
                const match = m.startsWith(sm) || sm.startsWith(m);
                console.log(`  Checking "${m}" vs "${sm}": ${match}`);
                return match;
            });
            
            if (isSelected) {
                console.log(`✅ Selected: ${m}`);
                li.classList.add('selected');
                if (currentSelected.length === 0) {
                    currentSelected = [m];
                }
            }
            
            li.addEventListener('click', () => onModelClick(m, li));
            li.addEventListener('keydown', (e) => { if (e.key === 'Enter') onModelClick(m, li); });
            modelListEl.appendChild(li);
        });
        
        // If nothing selected but models exist, select the first one
        if (currentSelected.length === 0 && models.length > 0) {
            console.log('🔄 No match found, selecting first model:', models[0]);
            currentSelected = [models[0]];
            Array.from(modelListEl.children).forEach((node, idx) => {
                if (idx === 0) node.classList.add('selected');
            });
        }
        
        console.log('🎯 Final currentSelected:', currentSelected);
        renderSelectedChips(currentSelected);
        console.log('✅ buildModelList complete');
    }

    function renderSelectedChips(list) {
        selectedChips.innerHTML = '';
        if (!list || list.length === 0) {
            const label = document.querySelector('.selected-label');
            if (label) label.textContent = 'Model';
            return;
        }
        const m = list[0];
        const chip = document.createElement('div');
        chip.className = 'model-chip';
        chip.textContent = m;
        selectedChips.appendChild(chip);
        // update toggle label
        const label = document.querySelector('.selected-label');
        if (label) label.textContent = m;
    }

    async function applyModels(selected) {
        // selected can be string
        console.log('📤 applyModels called with:', selected);
        showStatus('Applying...', false);
        const payload = { llm_model: selected };
        try {
            const res = await fetch('/models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            console.log('📥 applyModels response:', data);
            
            if (data.success) {
                // update UI state from server response
                const state = data.state || {};
                const newSelected = state.llm_models || (state.llm_model ? [state.llm_model] : [selected]);
                console.log('🎯 newSelected from server:', newSelected);
                currentSelected = newSelected;
                
                // update list item highlighting - handle version suffix mismatch
                Array.from(modelListEl.children).forEach(node => {
                    const modelName = node.dataset.model;
                    const isSelected = newSelected.some(ns => modelName.startsWith(ns) || ns.startsWith(modelName));
                    console.log(`  Checking highlight for "${modelName}": ${isSelected}`);
                    node.classList.toggle('selected', isSelected);
                });
                
                renderSelectedChips(currentSelected);
                showStatus(`Model applied: ${newSelected[0]}`);
            } else {
                showStatus(data.error || 'Failed to apply model(s)', true);
            }
        } catch (err) {
            console.error('❌ applyModels error:', err);
            showStatus('Server error applying models', true);
        }
    }

    function onModelClick(modelName, li) {
        console.log('🖱️ onModelClick called for:', modelName);
        // single select only
        currentSelected = [modelName];
        // update UI: mark only this
        Array.from(modelListEl.children).forEach(node => node.classList.toggle('selected', node.dataset.model === modelName));
        renderSelectedChips(currentSelected);
        applyModels(modelName);
        // close panel for convenience
        modelPanel.hidden = true;
        modelToggle.setAttribute('aria-expanded', 'false');
    }

    async function fetchModels() {
        try {
            console.log('🔍 Starting fetchModels...');
            const res = await fetch('/models');
            console.log('✅ Fetch response received, status:', res.status);
            
            if (!res.ok) {
                console.error('❌ Response not ok, status:', res.status);
                showStatus('Server returned error: ' + res.status, true);
                return;
            }
            
            let data;
            try {
                data = await res.json();
                console.log('✅ JSON parsed successfully:', data);
            } catch (parseErr) {
                console.error('❌ JSON parse failed:', parseErr);
                showStatus('Invalid response from server', true);
                return;
            }
            
            if (data && data.success) {
                console.log('✅ data.success is true');
                const models = data.models || [];
                const state = data.state || {};
                console.log('📦 Models:', models);
                console.log('📊 State:', state);
                
                try {
                    buildModelList(models, state);
                    console.log('✅ buildModelList completed');
                    document.getElementById('model-panel-footer').textContent = '';
                } catch (buildErr) {
                    console.error('❌ buildModelList failed:', buildErr);
                    showStatus('Error building model list: ' + buildErr.message, true);
                }
            } else {
                console.warn('⚠️ data.success is false or missing');
                showStatus('Could not fetch models', true);
                document.getElementById('model-panel-footer').textContent = 'Could not fetch models from server.';
            }
        } catch (err) {
            console.error('❌ fetchModels caught exception:', err);
            showStatus('Server error fetching models', true);
            document.getElementById('model-panel-footer').textContent = 'Server error: ' + err.message;
        }
    }

    function showStatus(msg, isError = false) {
        modelStatus.textContent = msg;
        modelStatus.style.color = isError ? 'crimson' : 'green';
        setTimeout(() => {
            // clear non-error messages after a short delay
            if (!isError) modelStatus.textContent = '';
        }, 4000);
    }

    async function handleUserInput() {
        const query = userInput.value.trim();
        if (query === "") return;

        userInput.value = "";
        userInput.disabled = true;
        sendButton.disabled = true;

        addMessage(query, "user");
        const loadingId = addLoadingIndicator();

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query, temperature: 0.7 }),
            });

            const data = await response.json();
            removeLoadingIndicator(loadingId);

            if (data.success) {
                const botReply =
                    typeof data.response === "string"
                        ? data.response
                        : JSON.stringify(data.response, null, 2);

                // ✅ call instant fast typer
                typeMessageFast(botReply, "bot");
            } else {
                addMessage("⚠️ Something went wrong. Please try again.", "bot");
            }
        } catch (error) {
            console.error("Error:", error);
            removeLoadingIndicator(loadingId);
            addMessage("❌ Server error. Please try again.", "bot");
        }

        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 🚀 FAST typewriter effect that won't freeze when tab inactive
    async function typeMessageFast(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message`;
        chatMessages.appendChild(messageDiv);

        let index = 0;
        const chunkSize = 8; // how many characters appear per frame
        const interval = 10; // ms delay between updates

        function typeChunk() {
            if (index < text.length) {
                messageDiv.textContent = text.slice(0, index + chunkSize);
                index += chunkSize;
                chatMessages.scrollTop = chatMessages.scrollHeight;
                // Use requestAnimationFrame or short timeout; both safe
                setTimeout(typeChunk, interval);
            } else {
                messageDiv.textContent = text;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }

        // Start without waiting for focus (doesn't freeze in background)
        requestAnimationFrame(typeChunk);
    }

    function addLoadingIndicator() {
        const loadingDiv = document.createElement("div");
        const id = Date.now();
        loadingDiv.id = `loading-${id}`;
        loadingDiv.className = "loading";
        loadingDiv.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeLoadingIndicator(id) {
        const loadingDiv = document.getElementById(`loading-${id}`);
        if (loadingDiv) loadingDiv.remove();
    }
});

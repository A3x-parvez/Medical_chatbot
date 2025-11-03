document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');

    // Add initial welcome message
    addMessage(
        "Hello! I'm your medical assistant. I can help answer your medical questions based on my knowledge. How can I help you today?",
        'bot'
    );

    // Handle send button click
    sendButton.addEventListener('click', handleUserInput);

    // Handle enter key (but shift+enter for new line)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleUserInput();
        }
    });

    async function handleUserInput() {
        const query = userInput.value.trim();
        if (query === '') return;

        // Clear input and disable
        userInput.value = '';
        userInput.disabled = true;
        sendButton.disabled = true;

        // Add user message
        addMessage(query, 'user');

        // Add loading indicator
        const loadingId = addLoadingIndicator();

        try {
            // Send request to backend
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    temperature: 0.7
                }),
            });

            const data = await response.json();

            // Remove loading indicator
            removeLoadingIndicator(loadingId);

            // Add response to chat
            if (data.success) {
                addMessage(data.response, 'bot');
            } else {
                addMessage(
                    'I apologize, but I encountered an error. Please try again.',
                    'bot'
                );
            }

        } catch (error) {
            console.error('Error:', error);
            removeLoadingIndicator(loadingId);
            addMessage(
                'I apologize, but I encountered an error. Please try again.',
                'bot'
            );
        }

        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        const id = Date.now();
        loadingDiv.id = `loading-${id}`;
        loadingDiv.className = 'loading';
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
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
});
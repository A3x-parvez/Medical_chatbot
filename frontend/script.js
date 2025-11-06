document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");

    // Initial welcome
    addMessage(
        "Hello! I'm your medical assistant 🤖. How can I help you today?",
        "bot"
    );

    sendButton.addEventListener("click", handleUserInput);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleUserInput();
        }
    });

    async function handleUserInput() {
        const query = userInput.value.trim();
        if (query === "") return;

        userInput.value = "";
        userInput.disabled = true;
        sendButton.disabled = true;

        addMessage(query, "user");
        const loadingId = addLoadingIndicator();

        try {
            const response = await fetch("http://127.0.0.1:5000/chat", {
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

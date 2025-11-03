document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");

    // Initial welcome message
    addMessage(
        "Hello! I'm your medical assistant 🤖. I can answer your medical questions based on my knowledge. How can I help you today?",
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

        // Clear and disable input
        userInput.value = "";
        userInput.disabled = true;
        sendButton.disabled = true;

        // Add user message
        addMessage(query, "user");

        // Add loading indicator
        const loadingId = addLoadingIndicator();

        try {
            // Send to Flask backend
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

                await typeMessage(botReply, "bot");
            } else {
                addMessage("⚠️ Something went wrong. Please try again.", "bot");
            }
        } catch (error) {
            console.error("Error:", error);
            removeLoadingIndicator(loadingId);
            addMessage("❌ Server error. Please try again.", "bot");
        }

        // Re-enable input
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

    async function typeMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message`;
        chatMessages.appendChild(messageDiv);

        for (let i = 0; i < text.length; i++) {
            messageDiv.textContent = text.slice(0, i + 1);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            await new Promise((r) => setTimeout(r, 15));
        }
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

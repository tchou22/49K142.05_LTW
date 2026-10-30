document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("chatbotToggle");
    const closeBtn = document.getElementById("chatbotClose");
    const box = document.getElementById("chatbotBox");
    const messages = document.getElementById("chatbotMessages");
    const input = document.getElementById("chatbotInput");
    const sendBtn = document.getElementById("chatbotSend");

    if (!toggleBtn || !closeBtn || !box || !messages || !input || !sendBtn) return;

    toggleBtn.addEventListener("click", function () {
        box.classList.toggle("chatbot-hidden");
    });

    closeBtn.addEventListener("click", function () {
        box.classList.add("chatbot-hidden");
    });

    function appendMessage(text, type) {
        const div = document.createElement("div");
        div.className = "msg " + type;
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function sendMessage(text = null) {
        const message = (text || input.value).trim();
        if (!message) return;

        appendMessage(message, "user");
        input.value = "";

        const loadingMsg = appendMessage("Đang gõ...", "bot");

        const csrfToken = getCookie("csrftoken");
        console.log("CSRF token:", csrfToken);

        fetch("/chatbot/api/chat/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ message: message })
        })
        .then(async response => {
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error("HTTP " + response.status + " - " + (data.reply || data.error || "Unknown error"));
            }

            return data;
        })
        .then(data => {
            loadingMsg.remove();
            appendMessage(data.reply || "Mình chưa có phản hồi.", "bot");
        })
        .catch((error) => {
            console.error("Lỗi:", error);
            loadingMsg.remove();
            appendMessage("Lỗi: " + error.message, "bot");
        });
    }

    sendBtn.addEventListener("click", function () {
        sendMessage();
    });

    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("quick-btn")) {
            sendMessage(e.target.textContent);
            const quickWrap = document.querySelector(".quick-wrap");
            if (quickWrap) quickWrap.style.display = "none";
        }
    });
});
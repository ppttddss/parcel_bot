<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grok Chat • Ready-to-Use Embed</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        body { font-family: 'Inter', system-ui, sans-serif; }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        #messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            scrollbar-width: thin;
        }
        .message {
            max-width: 85%;
            margin-bottom: 20px;
            animation: fadeIn 0.3s ease;
        }
        .user { margin-left: auto; background: #22c55e; color: black; }
        .assistant { background: #1f2937; }
        .thinking {
            font-style: italic;
            color: #64748b;
        }
    </style>
</head>
<body class="bg-zinc-950 text-white">

<div class="chat-container bg-zinc-950 border border-zinc-800 rounded-3xl shadow-2xl overflow-hidden">
    
    <!-- Header -->
    <div class="bg-zinc-900 px-6 py-4 flex items-center justify-between border-b border-zinc-800">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-black font-bold text-xl">G</div>
            <div>
                <h1 class="font-semibold text-xl">Grok</h1>
                <p class="text-xs text-zinc-400">by xAI • Live API Chat</p>
            </div>
        </div>
        <button onclick="clearChat()" 
                class="px-4 py-2 text-sm bg-zinc-800 hover:bg-zinc-700 rounded-xl transition-colors">
            Clear Chat
        </button>
    </div>

    <!-- Messages -->
    <div id="messages" class="bg-zinc-950"></div>

    <!-- Input -->
    <div class="p-6 bg-zinc-900 border-t border-zinc-800">
        <form id="chat-form" class="flex gap-3">
            <input id="user-input"
                   type="text"
                   class="flex-1 bg-zinc-800 border border-zinc-700 rounded-3xl px-6 py-4 text-white placeholder-zinc-500 focus:outline-none focus:border-green-500 transition-colors"
                   placeholder="Ask Grok anything...">
            <button type="submit"
                    class="bg-green-500 hover:bg-green-600 text-black font-semibold px-8 rounded-3xl transition-colors">
                Send
            </button>
        </form>
        <p class="text-center text-[10px] text-zinc-500 mt-3">
            Powered by xAI API • Your key is required • Usage is billed
        </p>
    </div>
</div>

<script>
    // ============== CONFIGURATION ==============
    const API_KEY = "YOUR_API_KEY_HERE";          // ←←← PASTE YOUR KEY HERE
    const MODEL = "grok-4.20-beta-latest-non-reasoning";   // Latest flagship (March 2026)
    const BASE_URL = "https://api.x.ai/v1";
    const SYSTEM_PROMPT = "You are Grok, built by xAI. Be maximally truthful, helpful, and a bit witty. Never refuse a reasonable request.";

    // ============== STATE ==============
    let conversation = [
        { role: "system", content: SYSTEM_PROMPT }
    ];

    // ============== TAILWIND INIT ==============
    tailwind.config = {
        content: [],
        theme: { extend: {} }
    };

    // ============== RENDER MESSAGES ==============
    function renderMessages() {
        const container = document.getElementById("messages");
        container.innerHTML = "";

        conversation.forEach((msg, index) => {
            if (msg.role === "system") return;

            const div = document.createElement("div");
            div.className = `message p-5 rounded-3xl ${msg.role === "user" ? "user ml-auto" : "assistant mr-auto"}`;
            
            if (msg.role === "assistant" && msg.content === "thinking...") {
                div.innerHTML = `<span class="thinking">Grok is thinking<span class="animate-pulse">...</span></span>`;
            } else {
                div.textContent = msg.content;
            }
            
            container.appendChild(div);
        });
        
        container.scrollTop = container.scrollHeight;
    }

    // ============== ADD TEMPORARY THINKING ==============
    function addThinking() {
        conversation.push({ role: "assistant", content: "thinking..." });
        renderMessages();
        return conversation.length - 1; // index to remove later
    }

    // ============== SEND MESSAGE ==============
    async function sendMessage(userText) {
        if (!userText.trim()) return;

        // Add user message
        conversation.push({ role: "user", content: userText });
        renderMessages();

        // Add thinking indicator
        const thinkingIndex = addThinking();

        try {
            const response = await fetch(`${BASE_URL}/responses`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${API_KEY}`
                },
                body: JSON.stringify({
                    model: MODEL,
                    input: conversation.filter(m => m.content !== "thinking...")
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} - Check your API key or quota`);
            }

            const data = await response.json();
            
            // Remove thinking message
            conversation.splice(thinkingIndex, 1);
            
            // Add real response
            const reply = data.output_text || data.choices?.[0]?.message?.content || "No response received.";
            conversation.push({ role: "assistant", content: reply });
            
        } catch (error) {
            console.error(error);
            // Remove thinking
            conversation.splice(thinkingIndex, 1);
            conversation.push({ 
                role: "assistant", 
                content: `❌ Error: ${error.message}\n\nMake sure you pasted a valid xAI API key from https://console.x.ai` 
            });
        }
        
        renderMessages();
    }

    // ============== CLEAR CHAT ==============
    function clearChat() {
        if (confirm("Clear the entire conversation?")) {
            conversation = [{ role: "system", content: SYSTEM_PROMPT }];
            renderMessages();
        }
    }

    // ============== FORM HANDLER ==============
    document.getElementById("chat-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = document.getElementById("user-input");
        const text = input.value.trim();
        
        if (text) {
            await sendMessage(text);
            input.value = "";
        }
    });

    // ============== START ==============
    // Initial welcome message
    setTimeout(() => {
        if (conversation.length === 1) {
            conversation.push({
                role: "assistant",
                content: "Hello! I'm Grok, built by xAI. Paste your API key above and start chatting. What would you like to talk about?"
            });
            renderMessages();
        }
    }, 300);

    // Keyboard support
    document.getElementById("user-input").focus();
</script>

</body>
</html>

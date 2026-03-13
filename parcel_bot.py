<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grok • SharePoint Ready</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: system-ui, sans-serif; margin:0; }
        .chat-container { height: 100vh; display: flex; flex-direction: column; background: #18181b; color: white; }
        #messages { flex: 1; overflow-y: auto; padding: 20px; }
        .message { max-width: 85%; margin-bottom: 20px; padding: 16px; border-radius: 20px; }
        .user { background: #22c55e; color: black; margin-left: auto; }
        .assistant { background: #27272a; }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="bg-zinc-900 px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-green-500 rounded-full flex items-center justify-center text-black text-2xl font-bold">G</div>
            <div><strong>Grok</strong><br><span class="text-xs text-zinc-400">xAI • Embedded in SharePoint</span></div>
        </div>
    </div>
    
    <div id="messages"></div>
    
    <div class="p-6 bg-zinc-900 border-t">
        <input id="user-input" type="text" placeholder="Ask Grok anything..." 
               class="w-full bg-zinc-800 text-white p-4 rounded-3xl border border-zinc-700 focus:border-green-500">
        <p class="text-[10px] text-center text-zinc-500 mt-3">Paste your xAI API key in the code below ↓</p>
    </div>
</div>

<script>
// ============== PUT YOUR xAI API KEY HERE ==============
const API_KEY = "xai-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";   // ←←← CHANGE THIS
const MODEL = "grok-4.20-beta-latest-non-reasoning";
const BASE_URL = "https://api.x.ai/v1";

let conversation = [{ role: "system", content: "You are Grok, built by xAI." }];

function render() {
    const msgDiv = document.getElementById("messages");
    msgDiv.innerHTML = conversation.slice(1).map(m => `
        <div class="message ${m.role==='user' ? 'user' : 'assistant'}">${m.content}</div>
    `).join('');
    msgDiv.scrollTop = msgDiv.scrollHeight;
}

async function send() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text || !API_KEY.includes("xai-")) return alert("Please paste a valid xAI API key in the code first!");
    
    conversation.push({role:"user", content:text});
    render();
    
    const thinkingIndex = conversation.length;
    conversation.push({role:"assistant", content:"thinking..."});
    render();
    
    try {
        const res = await fetch(`${BASE_URL}/responses`, {
            method: "POST",
            headers: {"Content-Type":"application/json", "Authorization": `Bearer ${API_KEY}`},
            body: JSON.stringify({model: MODEL, input: conversation.filter(m=>m.content!=="thinking...")})
        });
        const data = await res.json();
        conversation[thinkingIndex] = {role:"assistant", content: data.output_text || "No reply"};
    } catch(e) {
        conversation[thinkingIndex] = {role:"assistant", content: "❌ API error — check your key or quota"};
    }
    render();
    input.value = "";
}

document.getElementById("user-input").addEventListener("keypress", e => { if(e.key==="Enter") send(); });

// Welcome message
conversation.push({role:"assistant", content:"Hi! I'm Grok. Ask me anything — I'm ready inside SharePoint!"});
render();
</script>

</body>
</html>

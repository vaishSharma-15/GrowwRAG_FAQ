const API_BASE_URL = 'http://localhost:8000';
let chatHistory = [];

// Load chat history from localStorage on page load
function loadChatHistory() {
    const saved = localStorage.getItem('axisFaqChatHistory');
    if (saved) {
        chatHistory = JSON.parse(saved);
    }
}

// Show greeting message on page load
function showGreeting() {
    const chatContainer = document.getElementById('chatContainer');
    const greetingDiv = document.createElement('div');
    greetingDiv.className = 'flex flex-col gap-md';
    greetingDiv.innerHTML = `
        <div class="flex items-center gap-sm">
            <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center">
                <span class="material-symbols-outlined text-[18px] text-on-primary-container" data-weight="fill">hub</span>
            </div>
            <span class="font-label-md text-label-md font-bold text-on-surface">Axis Mutual Fund FAQ Assistant</span>
        </div>
        <div class="glass-panel p-lg rounded-2xl rounded-tl-none max-w-3xl border-l-4 border-l-secondary">
            <p class="font-body-md text-body-md text-on-surface mb-lg">Hello! I'm your Axis Mutual Fund FAQ Assistant. I can help you with information about Axis mutual fund schemes including expense ratios, NAV, exit loads, and more. Feel free to ask me anything about the supported schemes.</p>
        </div>
    `;
    chatContainer.insertBefore(greetingDiv, chatContainer.firstChild);
}

// Save current chat to history
function saveCurrentChat() {
    const chatContainer = document.getElementById('chatContainer');
    
    if (chatContainer.children.length > 0) {
        chatHistory.push({
            chatContent: chatContainer.innerHTML,
            timestamp: new Date().toISOString()
        });
        
        // Save to localStorage
        localStorage.setItem('axisFaqChatHistory', JSON.stringify(chatHistory));
    }
}

// Clear chat
function clearChat() {
    const chatContainer = document.getElementById('chatContainer');
    
    // Save current chat before clearing
    saveCurrentChat();
    
    // Clear the chat
    chatContainer.innerHTML = '';
}

// Add user message to chat
function addUserMessage(message) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-end';
    messageDiv.innerHTML = `
        <div class="max-w-2xl bg-surface-container-high rounded-2xl rounded-tr-none p-lg">
            <p class="font-body-md text-body-md text-on-surface">${message}</p>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    // Scroll to bottom of parent container
    chatContainer.parentElement.scrollTop = chatContainer.parentElement.scrollHeight;
}

// Add AI response to chat
function addAIResponse(message) {
    const chatContainer = document.getElementById('chatContainer');
    const responseDiv = document.createElement('div');
    responseDiv.className = 'flex flex-col gap-md';
    
    responseDiv.innerHTML = `
        <div class="flex items-center gap-sm">
            <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center">
                <span class="material-symbols-outlined text-[18px] text-on-primary-container" data-weight="fill">hub</span>
            </div>
            <span class="font-label-md text-label-md font-bold text-on-surface">Axis Mutual Fund FAQ Assistant</span>
        </div>
        <div class="glass-panel p-lg rounded-2xl rounded-tl-none max-w-3xl border-l-4 border-l-secondary">
            <p class="font-body-md text-body-md text-on-surface mb-lg">${message}</p>
        </div>
    `;
    
    chatContainer.appendChild(responseDiv);
    // Scroll to bottom of parent container
    chatContainer.parentElement.scrollTop = chatContainer.parentElement.scrollHeight;
}

// Add loading indicator
function addLoadingIndicator() {
    const chatContainer = document.getElementById('chatContainer');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'flex flex-col gap-md';
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.innerHTML = `
        <div class="flex items-center gap-sm">
            <div class="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center">
                <span class="material-symbols-outlined text-[18px] text-on-primary-container" data-weight="fill">hub</span>
            </div>
            <span class="font-label-md text-label-md font-bold text-on-surface">Axis Mutual Fund FAQ Assistant</span>
        </div>
        <div class="glass-panel p-lg rounded-2xl rounded-tl-none max-w-3xl border-l-4 border-l-secondary">
            <p class="font-body-md text-body-md text-on-surface-variant flex items-center gap-sm">
                <span class="material-symbols-outlined animate-spin">refresh</span>
                <span>Searching...</span>
            </p>
        </div>
    `;
    chatContainer.appendChild(loadingDiv);
    // Scroll to bottom of parent container
    chatContainer.parentElement.scrollTop = chatContainer.parentElement.scrollHeight;
}

// Remove loading indicator
function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Set query from suggestion chips
function setQuery(question) {
    const input = document.getElementById('queryInput');
    input.value = question;
    input.focus();
}

// Submit query
async function submitQuery() {
    const input = document.getElementById('queryInput');
    const query = input.value.trim();
    
    if (!query) {
        return;
    }
    
    // Add user message
    addUserMessage(query);
    
    // Clear input
    input.value = '';
    
    // Handle basic greetings locally
    const lowerQuery = query.toLowerCase();
    const greetings = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'thank you very much', 'bye', 'goodbye'];
    
    if (greetings.some(g => lowerQuery === g || lowerQuery.startsWith(g + ' '))) {
        let response = '';
        if (lowerQuery.includes('hi') || lowerQuery.includes('hello') || lowerQuery.includes('hey')) {
            response = 'Hello! How can I help you with Axis Mutual Fund schemes today?';
        } else if (lowerQuery.includes('thanks') || lowerQuery.includes('thank')) {
            response = 'You\'re welcome! Feel free to ask if you have more questions about Axis Mutual Fund schemes.';
        } else if (lowerQuery.includes('bye') || lowerQuery.includes('goodbye')) {
            response = 'Goodbye! Feel free to come back if you have more questions about Axis Mutual Fund schemes.';
        }
        addAIResponse(response);
        return;
    }
    
    // Show loading
    addLoadingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        // Remove loading
        removeLoadingIndicator();
        
        if (data.has_answer) {
            let answer = data.answer;
            if (data.source_url) {
                answer += `\n\n📄 Source: ${data.source_url}`;
            }
            if (data.scheme_name) {
                answer += `\n🏦 Scheme: ${data.scheme_name}`;
            }
            if (data.last_updated) {
                answer += `\n📅 Last Updated: ${data.last_updated}`;
            }
            addAIResponse(answer.replace(/\n/g, '<br>'));
        } else {
            addAIResponse(data.answer);
        }
    } catch (error) {
        removeLoadingIndicator();
        addAIResponse('Unable to connect to backend. Please ensure the API server is running.');
    }
}

// Handle Enter key
document.getElementById('queryInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitQuery();
    }
});

// Load chat history on page load
loadChatHistory();

// Show greeting message on page load
showGreeting();

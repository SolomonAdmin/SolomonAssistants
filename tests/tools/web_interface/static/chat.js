class ChatInterface {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.lastMessageType = null;
        this.lastMessageSender = null;
        this.currentMessageGroup = null;
        this.systemMessageCount = 0;
        this.setupEventListeners();
        this.connect();

        // Add system messages indicator to the header
        const header = document.querySelector('.chat-header');
        const indicator = document.createElement('div');
        indicator.className = 'system-messages-indicator hidden';
        indicator.innerHTML = `
            <button class="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="system-message-count"></span>
            </button>
            <div class="system-messages-panel hidden">
                <div class="system-messages-content"></div>
            </div>
        `;
        header.appendChild(indicator);

        // Show/hide system messages panel
        indicator.querySelector('button').addEventListener('click', () => {
            const panel = indicator.querySelector('.system-messages-panel');
            panel.classList.toggle('hidden');
        });
    }

    setupEventListeners() {
        // Send button
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        
        // Enter key in message input
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Disconnect button
        document.getElementById('disconnectBtn').addEventListener('click', () => this.disconnect());
    }

    connect() {
        const apiKey = sessionStorage.getItem('apiKey');
        const assistantId = sessionStorage.getItem('assistantId');
        const vectorStoreId = sessionStorage.getItem('vectorStoreId');

        if (!apiKey || !assistantId) {
            this.showError('Connection details not found. Please return to the connection page.');
            return;
        }

        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/assistant/${assistantId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.connected = true;
            this.addMessage('Connected to Assistant', 'system');
            
            // Initialize the assistant
            this.ws.send(JSON.stringify({
                type: 'initialize',
                api_key: apiKey,
                vector_store_ids: vectorStoreId ? [vectorStoreId] : []
            }));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onclose = () => {
            this.connected = false;
            this.addMessage('Disconnected from Assistant', 'system');
        };

        this.ws.onerror = (error) => {
            this.addMessage(`WebSocket error: ${error.message}`, 'error');
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'stream':
                this.addMessage(data.content, 'assistant');
                break;
            case 'tool':
                if (data.tool === 'call') {
                    this.addMessage(`[Using tool: ${data.name}]`, 'tool');
                } else if (data.tool === 'output') {
                    this.addMessage(`[Tool output: ${data.content}]`, 'tool');
                }
                break;
            case 'error':
                this.addMessage(`Error: ${data.error}`, 'error');
                break;
            case 'system':
                if (data.message && !data.message.includes('Processing')) {
                    this.addMessage(`System: ${data.message}`, 'system');
                }
                break;
            case 'response':
                this.addMessage(data.content, 'assistant');
                break;
            default:
                this.addMessage(`Received unknown message type: ${data.type}`, 'system');
        }
    }

    sendMessage() {
        if (!this.connected) {
            this.addMessage('Not connected to Assistant', 'error');
            return;
        }

        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message) {
            return;
        }

        this.addMessage(message, 'user');
        messageInput.value = '';

        this.ws.send(JSON.stringify({
            type: 'chat_message',
            message: message
        }));
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        // Clear session storage
        sessionStorage.removeItem('apiKey');
        sessionStorage.removeItem('assistantId');
        sessionStorage.removeItem('vectorStoreId');
        // Redirect to connection page
        window.location.href = 'index.html';
    }

    addMessage(message, type) {
        const chatMessages = document.getElementById('chatMessages');

        // Handle system messages
        if (type === 'system') {
            this.systemMessageCount++;
            const indicator = document.querySelector('.system-messages-indicator');
            const counter = indicator.querySelector('.system-message-count');
            const content = indicator.querySelector('.system-messages-content');
            
            indicator.classList.remove('hidden');
            counter.textContent = `${this.systemMessageCount} system message${this.systemMessageCount > 1 ? 's' : ''}`;
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'system-message text-xs text-gray-600 py-1';
            messageDiv.textContent = message;
            content.appendChild(messageDiv);
            return;
        }

        // Handle regular messages
        const sender = type === 'user' ? 'user' : 'assistant';

        // If this message is from the same sender as the last one, add to the current group
        if (sender === this.lastMessageSender && this.currentMessageGroup) {
            const bubble = this.currentMessageGroup.querySelector('.message-bubble');
            const content = document.createElement('div');
            content.className = 'message-content';
            
            if (type === 'assistant') {
                content.innerHTML = marked.parse(message);
            } else {
                content.textContent = message;
            }
            
            bubble.appendChild(content);
        } else {
            // Create new message group
            const messageDiv = document.createElement('div');
            messageDiv.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'} mb-4`;
            
            // Create message bubble
            const bubble = document.createElement('div');
            bubble.className = `message-bubble max-w-[80%] rounded-lg p-4 ${
                type === 'user' 
                    ? 'bg-blue-500 text-white rounded-br-none' 
                    : type === 'assistant'
                    ? 'bg-gray-100 text-gray-800 rounded-bl-none'
                    : type === 'error'
                    ? 'bg-red-100 text-red-700'
                    : type === 'tool'
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-gray-100 text-gray-800'
            }`;

            // Add first message content
            const content = document.createElement('div');
            content.className = 'message-content';
            if (type === 'assistant') {
                content.innerHTML = marked.parse(message);
            } else {
                content.textContent = message;
            }
            bubble.appendChild(content);

            // Add avatar
            if (type === 'user' || type === 'assistant') {
                const avatar = document.createElement('div');
                avatar.className = `w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                    type === 'user' ? 'bg-blue-600' : 'bg-gray-300'
                }`;
                avatar.innerHTML = type === 'user' 
                    ? '<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>'
                    : '<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>';
                
                const container = document.createElement('div');
                container.className = 'flex items-start';
                container.appendChild(avatar);
                container.appendChild(bubble);
                messageDiv.appendChild(container);
            } else {
                messageDiv.appendChild(bubble);
            }

            chatMessages.appendChild(messageDiv);
            this.currentMessageGroup = messageDiv;
        }

        this.lastMessageSender = sender;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showError(message) {
        this.addMessage(message, 'error');
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
}); 
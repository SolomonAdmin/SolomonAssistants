class AssistantBridgeUI {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Connect button
        document.getElementById('connectBtn').addEventListener('click', () => this.connect());
        
        // Send button
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        
        // Enter key in message input
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    connect() {
        const apiKey = document.getElementById('apiKey').value;
        const assistantId = document.getElementById('assistantId').value;
        const vectorStoreId = document.getElementById('vectorStoreId').value;

        if (!apiKey || !assistantId) {
            this.addMessage('Error: API Key and Assistant ID are required', 'error');
            return;
        }

        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/assistant/${assistantId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.connected = true;
            this.addMessage('Connected to WebSocket server', 'system');
            
            // Initialize the assistant bridge
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
            this.addMessage('Disconnected from WebSocket server', 'system');
        };

        this.ws.onerror = (error) => {
            this.addMessage(`WebSocket error: ${error.message}`, 'error');
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'connection_established':
                this.addMessage('Connection established with assistant', 'system');
                break;
            case 'initialized':
                this.addMessage('Assistant bridge initialized successfully', 'system');
                break;
            case 'content_chunk':
                this.addMessage(data.data.content, 'assistant');
                break;
            case 'tool_usage':
                this.addMessage(`Tool usage: ${data.data.message}`, 'tool');
                break;
            case 'error':
                this.addMessage(`Error: ${data.data.message}`, 'error');
                break;
            case 'processing_started':
                this.addMessage('Processing your message...', 'system');
                break;
            case 'processing_complete':
                this.addMessage('Message processing complete', 'system');
                break;
            default:
                this.addMessage(`Received unknown message type: ${data.type}`, 'system');
        }
    }

    sendMessage() {
        if (!this.connected) {
            this.addMessage('Not connected to WebSocket server', 'error');
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

    addMessage(message, type) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-2 ${this.getMessageClass(type)}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    getMessageClass(type) {
        switch (type) {
            case 'user':
                return 'text-blue-600 font-medium';
            case 'assistant':
                return 'text-green-600';
            case 'system':
                return 'text-gray-500 italic';
            case 'error':
                return 'text-red-600';
            case 'tool':
                return 'text-purple-600';
            default:
                return 'text-gray-700';
        }
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AssistantBridgeUI();
}); 
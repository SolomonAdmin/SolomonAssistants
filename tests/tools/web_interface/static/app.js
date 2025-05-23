class AssistantBridgeUI {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.currentResponseTurn = null;
        this.systemMessageCount = 0;
        this.setupEventListeners();
        this.connect();
    }

    setupEventListeners() {
        // Send button click
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key in message input
        const messageInput = document.getElementById('messageInput');
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    connect() {
        const apiKey = sessionStorage.getItem('apiKey');
        const assistantId = sessionStorage.getItem('assistantId');
        const vectorStoreId = sessionStorage.getItem('vectorStoreId');

        if (!apiKey || !assistantId) {
            this.addSystemMessage('Error: API Key and Assistant ID are required');
            return;
        }

        // Create WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/assistant/${assistantId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.connected = true;
            this.addSystemMessage('Connected to WebSocket server');
            
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
            this.addSystemMessage('Disconnected from WebSocket server');
        };

        this.ws.onerror = (error) => {
            this.addSystemMessage(`WebSocket error: ${error.message}`);
        };
    }

    handleWebSocketMessage(data) {
        console.log('Received message:', data);
        
        if (data.type === 'message') {
            if (data.role === 'system') {
                this.addSystemMessage(data.content);
            } else if (data.role === 'assistant') {
                // If this is a new turn or we have the new_turn flag, create a new bubble
                if (data.new_turn || !this.currentResponseTurn) {
                    // Create a new turn for this response
                    console.log("Creating new bubble for assistant message");
                    this.currentResponseTurn = document.createElement('div');
                    this.currentResponseTurn.className = 'mb-2 text-left bg-gray-100 text-gray-800 rounded-lg p-2 mr-auto max-w-[80%]';
                    this.currentResponseTurn.textContent = '';
                    document.getElementById('chatMessages').appendChild(this.currentResponseTurn);
                }
                
                // Append this chunk to the current turn
                this.currentResponseTurn.textContent += data.content;
                this.scrollToBottom();
            }
        } else if (data.type === 'error') {
            this.addSystemMessage(`Error: ${data.error}`);
        }
    }

    addSystemMessage(message) {
        console.log('System:', message);
        
        // Update the system message count badge
        this.systemMessageCount++;
        document.getElementById('systemMessageCount').textContent = this.systemMessageCount;
        
        // Add the message to the tooltip list
        const systemMessageList = document.getElementById('systemMessageList');
        const messageItem = document.createElement('div');
        messageItem.className = 'text-sm text-gray-600 mb-1';
        messageItem.textContent = message;
        systemMessageList.appendChild(messageItem);
        
        // No longer add system messages to the main chat
    }

    sendMessage() {
        if (!this.connected) return;

        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        if (!message) return;

        // Create user message bubble
        const userBubble = document.createElement('div');
        userBubble.className = 'mb-2 text-right bg-blue-500 text-white rounded-lg p-2 ml-auto max-w-[80%]';
        userBubble.textContent = message;
        document.getElementById('chatMessages').appendChild(userBubble);

        // We don't reset currentResponseTurn here anymore - 
        // we'll let the server tell us when to create a new bubble

        // Send to server
        this.ws.send(JSON.stringify({
            type: 'chat_message',
            message: message
        }));

        // Clear input
        messageInput.value = '';
        this.scrollToBottom();
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AssistantBridgeUI();
}); 
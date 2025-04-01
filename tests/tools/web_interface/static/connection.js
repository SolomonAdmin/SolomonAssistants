class ConnectionManager {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Connect button
        document.getElementById('connectBtn').addEventListener('click', () => this.connect());
        
        // Enter key in inputs
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.connect();
                }
            });
        });
    }

    connect() {
        const apiKey = document.getElementById('apiKey').value;
        const assistantId = document.getElementById('assistantId').value;
        const vectorStoreId = document.getElementById('vectorStoreId').value;

        if (!apiKey || !assistantId) {
            this.showError('API Key and Assistant ID are required');
            return;
        }

        // Store connection details in sessionStorage
        sessionStorage.setItem('apiKey', apiKey);
        sessionStorage.setItem('assistantId', assistantId);
        sessionStorage.setItem('vectorStoreId', vectorStoreId);

        // Redirect to chat page
        window.location.href = '/static/chat.html';
    }

    showError(message) {
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4';
        errorDiv.innerHTML = `
            <span class="block sm:inline">${message}</span>
            <span class="absolute top-0 bottom-0 right-0 px-4 py-3">
                <svg class="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <title>Close</title>
                    <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
                </svg>
            </span>
        `;

        // Add close button functionality
        const closeButton = errorDiv.querySelector('svg');
        closeButton.addEventListener('click', () => errorDiv.remove());

        // Insert error at the top of the form
        const form = document.querySelector('.space-y-6');
        form.insertBefore(errorDiv, form.firstChild);
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ConnectionManager();
}); 
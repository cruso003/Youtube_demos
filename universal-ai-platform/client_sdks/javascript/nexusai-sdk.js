/**
 * NexusAI - JavaScript SDK
 * Official client library for NexusAI - The Universal AI Agent Platform for Africa
 * https://nexus.bits-innovate.com
 */

class NexusAIClient {
    /**
     * Initialize the NexusAI client
     * @param {string} apiUrl - Base URL of the NexusAI API (default: production endpoint)
     * @param {string} apiKey - Optional API key for authentication
     */
    constructor(apiUrl = 'https://nexus.bits-innovate.com', apiKey = null) {
        this.apiUrl = apiUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        
        this.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'NexusAI-JavaScript-SDK/1.0.0'
        };
        
        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }

    /**
     * Make HTTP request to the API
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {object} data - Request data
     * @returns {Promise<object>} Response data
     */
    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.apiUrl}${endpoint}`;
        const options = {
            method,
            headers: this.headers
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(responseData.message || `HTTP error! status: ${response.status}`);
            }

            return responseData;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Check API health status
     * @returns {Promise<object>} Health status information
     */
    async healthCheck() {
        return await this.request('/health', 'GET');
    }

    /**
     * Create a new AI agent session
     * @param {object} config - Agent configuration
     * @returns {Promise<object>} Session information
     */
    async createAgent(config) {
        const payload = {
            instructions: config.instructions,
            capabilities: config.capabilities || ['text'],
            business_logic_adapter: config.businessLogicAdapter || null,
            custom_settings: config.customSettings || {},
            client_id: config.clientId || null
        };

        return await this.request('/api/v1/agent/create', 'POST', payload);
    }

    /**
     * Create a new session (alias for createAgent for backwards compatibility)
     * @param {object} config - Session configuration
     * @returns {Promise<object>} Session information
     */
    async createSession(config) {
        return await this.createAgent(config);
    }

    /**
     * Send a message to an agent session
     * @param {string} sessionId - Agent session ID
     * @param {string} message - Message content
     * @param {string} messageType - Type of message ('text', 'image', 'audio')
     * @returns {Promise<object>} Response from the API
     */
    async sendMessage(sessionId, message, messageType = 'text') {
        const payload = {
            message: message,
            type: messageType
        };

        return await this.request(`/api/v1/agent/${sessionId}/message`, 'POST', payload);
    }

    /**
     * Get messages from an agent session
     * @param {string} sessionId - Agent session ID
     * @returns {Promise<array>} List of messages
     */
    async getMessages(sessionId) {
        const response = await this.request(`/api/v1/agent/${sessionId}/messages`);
        return response.messages || [];
    }

    /**
     * Get status of an agent session
     * @param {string} sessionId - Agent session ID
     * @returns {Promise<object>} Session status information
     */
    async getSessionStatus(sessionId) {
        return await this.request(`/api/v1/agent/${sessionId}/status`);
    }

    /**
     * Delete an agent session
     * @param {string} sessionId - Agent session ID
     * @returns {Promise<object>} Deletion confirmation
     */
    async deleteSession(sessionId) {
        return await this.request(`/api/v1/agent/${sessionId}`, 'DELETE');
    }

    /**
     * Get usage summary for billing
     * @param {string} clientId - Client identifier
     * @param {Date} startDate - Start date for usage period
     * @param {Date} endDate - End date for usage period
     * @returns {Promise<object>} Usage summary
     */
    async getUsageSummary(clientId, startDate = null, endDate = null) {
        let url = `/api/v1/usage/${clientId}`;
        const params = new URLSearchParams();

        if (startDate) {
            params.append('start_date', startDate.toISOString());
        }
        if (endDate) {
            params.append('end_date', endDate.toISOString());
        }

        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        return await this.request(url);
    }


    /**
     * List all active agent sessions
     * @returns {Promise<array>} List of active sessions
     */
    async listActiveSessions() {
        const response = await this.request('/api/v1/agents');
        return response.sessions || [];
    }
}

class AgentSession {
    /**
     * High-level wrapper for managing an agent session
     * @param {NexusAIClient} client - NexusAI client instance
     * @param {string} sessionId - Session ID from createAgent
     */
    constructor(client, sessionId) {
        this.client = client;
        this.sessionId = sessionId;
        this.messages = [];
        this.eventListeners = {};
    }

    /**
     * Send a message to the agent
     * @param {string} message - Message content
     * @param {string} messageType - Type of message
     * @returns {Promise<object>} Response from API
     */
    async sendMessage(message, messageType = 'text') {
        return await this.client.sendMessage(this.sessionId, message, messageType);
    }

    /**
     * Get new messages since last call
     * @returns {Promise<array>} New messages
     */
    async getNewMessages() {
        const allMessages = await this.client.getMessages(this.sessionId);
        
        // Filter out messages we already have
        const knownIds = new Set(this.messages.map(msg => msg.id));
        const newMessages = allMessages.filter(msg => !knownIds.has(msg.id));
        
        // Update our message list
        this.messages.push(...newMessages);
        
        // Emit events for new messages
        newMessages.forEach(message => {
            this.emit('message', message);
            if (message.sender === 'assistant') {
                this.emit('response', message);
            }
        });
        
        return newMessages;
    }

    /**
     * Get all messages in the session
     * @returns {Promise<array>} All messages
     */
    async getAllMessages() {
        this.messages = await this.client.getMessages(this.sessionId);
        return this.messages;
    }

    /**
     * Get message history (alias for getAllMessages)
     * @param {number} limit - Maximum number of messages to return (optional)
     * @returns {Promise<array>} Message history
     */
    async getHistory(limit = null) {
        const messages = await this.getAllMessages();
        return limit ? messages.slice(-limit) : messages;
    }

    /**
     * Get session status
     * @returns {Promise<object>} Session status
     */
    async getStatus() {
        return await this.client.getSessionStatus(this.sessionId);
    }

    /**
     * Close the session
     * @returns {Promise<object>} Deletion confirmation
     */
    async close() {
        return await this.client.deleteSession(this.sessionId);
    }

    /**
     * Wait for a response from the agent
     * @param {number} timeout - Maximum time to wait in milliseconds
     * @param {number} pollInterval - How often to check for new messages in milliseconds
     * @returns {Promise<object|null>} The first new assistant message, or null if timeout
     */
    async waitForResponse(timeout = 30000, pollInterval = 500) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            
            const checkForResponse = async () => {
                if (Date.now() - startTime >= timeout) {
                    resolve(null);
                    return;
                }
                
                try {
                    const newMessages = await this.getNewMessages();
                    
                    // Look for assistant messages
                    for (const message of newMessages) {
                        if (message.sender === 'assistant') {
                            resolve(message);
                            return;
                        }
                    }
                    
                    // Continue checking
                    setTimeout(checkForResponse, pollInterval);
                } catch (error) {
                    console.error('Error checking for response:', error);
                    setTimeout(checkForResponse, pollInterval);
                }
            };
            
            checkForResponse();
        });
    }

    /**
     * Start polling for new messages
     * @param {number} interval - Polling interval in milliseconds
     * @returns {number} Interval ID for stopping
     */
    startPolling(interval = 1000) {
        return setInterval(async () => {
            try {
                await this.getNewMessages();
            } catch (error) {
                console.error('Error polling for messages:', error);
            }
        }, interval);
    }

    /**
     * Stop polling for messages
     * @param {number} intervalId - Interval ID from startPolling
     */
    stopPolling(intervalId) {
        clearInterval(intervalId);
    }

    /**
     * Add event listener
     * @param {string} event - Event name ('message', 'response')
     * @param {function} callback - Callback function
     */
    on(event, callback) {
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        this.eventListeners[event].push(callback);
    }

    /**
     * Remove event listener
     * @param {string} event - Event name
     * @param {function} callback - Callback function
     */
    off(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
        }
    }

    /**
     * Emit event
     * @param {string} event - Event name
     * @param {any} data - Event data
     */
    emit(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in event listener:', error);
                }
            });
        }
    }
}

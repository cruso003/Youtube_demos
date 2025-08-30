/**
 * NexusAI - JavaScript SDK
 * Official client library for NexusAI - The Universal AI Agent Platform for Africa
 * https://nexus.bits-innovate.com
 */

// Service configuration enums and classes
const AIModel = {
    GPT_4O_MINI: 'gpt-4o-mini',      // 1 credit per 1K tokens
    GPT_4O: 'gpt-4o',                // 8 credits per 1K tokens
    GPT_4: 'gpt-4',                  // 25 credits per 1K tokens
    CLAUDE_3_HAIKU: 'claude-3-haiku',     // 1 credit per 1K tokens
    CLAUDE_3_SONNET: 'claude-3-sonnet',   // 12 credits per 1K tokens
    GPT_4_VISION: 'gpt-4-vision',         // 50 credits per image
    CLAUDE_3_VISION: 'claude-3-vision'    // 40 credits per image
};

const VoiceProvider = {
    CARTESIA: 'cartesia',            // 0.8 credits per 1K chars (Primary TTS)
    OPENAI_TTS: 'openai-tts',        // 1 credit per 1K chars (Backup TTS)
    DEEPGRAM: 'deepgram',            // 8 credits per minute (Primary STT)
    OPENAI_WHISPER: 'openai-whisper'     // 10 credits per minute (Backup STT)
};

const PhoneProvider = {
    TWILIO: 'twilio',                // 20 credits per minute
    TWILIO_INTERNATIONAL: 'twilio-intl'  // 35 credits per minute
};

class ServiceConfiguration {
    constructor(options = {}) {
        this.primaryAiModel = options.primaryAiModel || AIModel.GPT_4O_MINI;
        this.fallbackAiModel = options.fallbackAiModel || null;
        this.ttsProvider = options.ttsProvider || VoiceProvider.CARTESIA;
        this.sttProvider = options.sttProvider || VoiceProvider.DEEPGRAM;
        this.voiceEnabled = options.voiceEnabled || false;
        this.visionModel = options.visionModel || AIModel.GPT_4_VISION;
        this.visionEnabled = options.visionEnabled || false;
        this.phoneProvider = options.phoneProvider || PhoneProvider.TWILIO;
        this.phoneEnabled = options.phoneEnabled || false;
        this.realtimeEnabled = options.realtimeEnabled || false;
        this.maxCreditsPerRequest = options.maxCreditsPerRequest || null;
        this.costOptimization = options.costOptimization !== undefined ? options.costOptimization : true;
        this.servicePriorities = options.servicePriorities || {
            cost: 'medium',
            accuracy: 'medium',
            speed: 'high'
        };
    }

    toJSON() {
        return {
            primary_ai_model: this.primaryAiModel,
            fallback_ai_model: this.fallbackAiModel,
            tts_provider: this.ttsProvider,
            stt_provider: this.sttProvider,
            voice_enabled: this.voiceEnabled,
            vision_model: this.visionModel,
            vision_enabled: this.visionEnabled,
            phone_provider: this.phoneProvider,
            phone_enabled: this.phoneEnabled,
            realtime_enabled: this.realtimeEnabled,
            max_credits_per_request: this.maxCreditsPerRequest,
            cost_optimization: this.costOptimization,
            service_priorities: this.servicePriorities
        };
    }
}

class ServicePresets {
    static costOptimized() {
        return new ServiceConfiguration({
            primaryAiModel: AIModel.GPT_4O_MINI,
            ttsProvider: VoiceProvider.CARTESIA,
            sttProvider: VoiceProvider.DEEPGRAM,
            visionModel: AIModel.GPT_4_VISION,
            phoneProvider: PhoneProvider.TWILIO,
            costOptimization: true,
            maxCreditsPerRequest: 50,
            servicePriorities: { cost: 'high', accuracy: 'medium', speed: 'medium' }
        });
    }

    static premiumQuality() {
        return new ServiceConfiguration({
            primaryAiModel: AIModel.GPT_4,
            fallbackAiModel: AIModel.GPT_4O,
            ttsProvider: VoiceProvider.CARTESIA,
            sttProvider: VoiceProvider.OPENAI_WHISPER,
            visionModel: AIModel.GPT_4_VISION,
            phoneProvider: PhoneProvider.TWILIO,
            costOptimization: false,
            servicePriorities: { cost: 'low', accuracy: 'high', speed: 'medium' }
        });
    }

    static balanced() {
        return new ServiceConfiguration({
            primaryAiModel: AIModel.GPT_4O,
            fallbackAiModel: AIModel.GPT_4O_MINI,
            ttsProvider: VoiceProvider.CARTESIA,
            sttProvider: VoiceProvider.DEEPGRAM,
            visionModel: AIModel.GPT_4_VISION,
            phoneProvider: PhoneProvider.TWILIO,
            costOptimization: true,
            maxCreditsPerRequest: 200,
            servicePriorities: { cost: 'medium', accuracy: 'high', speed: 'high' }
        });
    }

    static emergencyServices() {
        return new ServiceConfiguration({
            primaryAiModel: AIModel.GPT_4O,
            fallbackAiModel: AIModel.GPT_4,
            ttsProvider: VoiceProvider.CARTESIA,
            sttProvider: VoiceProvider.OPENAI_WHISPER,
            visionModel: AIModel.GPT_4_VISION,
            phoneProvider: PhoneProvider.TWILIO,
            voiceEnabled: true,
            visionEnabled: true,
            phoneEnabled: true,
            realtimeEnabled: true,
            costOptimization: false,
            servicePriorities: { cost: 'low', accuracy: 'high', speed: 'high' }
        });
    }
}

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
        const customSettings = { ...config.customSettings } || {};
        
        // Include service configuration in custom settings if provided
        if (config.serviceConfiguration) {
            customSettings.service_configuration = config.serviceConfiguration.toJSON();
        }
        
        const payload = {
            instructions: config.instructions,
            capabilities: config.capabilities || ['text'],
            business_logic_adapter: config.businessLogicAdapter || null,
            custom_settings: customSettings,
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
     * Get credit-based billing information
     * @param {string} clientId - Client identifier
     * @param {Date} startDate - Start date for billing period
     * @param {Date} endDate - End date for billing period
     * @returns {Promise<object>} Billing information (credit usage)
     */
    async getBillingInfo(clientId, startDate = null, endDate = null) {
        let url = `/api/v1/billing/${clientId}`;
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

    /**
     * Estimate cost for a multi-service workflow
     * @param {object} workflowDescription - Description of expected usage
     * @param {ServiceConfiguration} serviceConfig - Service configuration to use for estimates
     * @returns {object} Cost estimation breakdown
     */
    estimateWorkflowCost(workflowDescription, serviceConfig = null) {
        if (!serviceConfig) {
            serviceConfig = ServicePresets.costOptimized();
        }

        const estimatedCost = {
            totalCredits: 0,
            totalCostUsd: 0.0,
            serviceBreakdown: [],
            warnings: []
        };

        // AI model costs
        if (workflowDescription.aiTokens) {
            const modelCosts = {
                'gpt-4o-mini': [1, 0.00015],
                'gpt-4o': [8, 0.0025],
                'gpt-4': [25, 0.03],
                'claude-3-haiku': [1, 0.00025],
                'claude-3-sonnet': [12, 0.003]
            };

            const [creditsPerK, costPerK] = modelCosts[serviceConfig.primaryAiModel] || [1, 0.001];
            const tokens = workflowDescription.aiTokens;

            const aiCredits = Math.max(1, Math.floor((tokens / 1000) * creditsPerK));
            const aiCost = (tokens / 1000) * costPerK;

            estimatedCost.totalCredits += aiCredits;
            estimatedCost.totalCostUsd += aiCost;
            estimatedCost.serviceBreakdown.push({
                service: 'AI Model',
                provider: serviceConfig.primaryAiModel,
                credits: aiCredits,
                costUsd: aiCost
            });
        }

        // Voice services
        if (workflowDescription.voiceMinutes && serviceConfig.voiceEnabled) {
            const minutes = workflowDescription.voiceMinutes;

            // STT cost
            const sttCredits = serviceConfig.sttProvider === 'deepgram' ? 8 : 10;
            const sttCreditsCost = Math.max(1, Math.floor(minutes * sttCredits));
            const sttCost = minutes * (serviceConfig.sttProvider === 'deepgram' ? 0.0043 : 0.006);

            // TTS cost
            const chars = Math.floor(minutes * 150); // 150 chars per minute estimate
            const ttsRate = serviceConfig.ttsProvider === 'cartesia' ? 0.8 : 1.0;
            const ttsCreditsCost = Math.max(1, Math.floor((chars / 1000) * ttsRate));
            const ttsCost = chars * (serviceConfig.ttsProvider === 'cartesia' ? 0.000011 : 0.000015);

            const voiceCredits = sttCreditsCost + ttsCreditsCost;
            const voiceCost = sttCost + ttsCost;

            estimatedCost.totalCredits += voiceCredits;
            estimatedCost.totalCostUsd += voiceCost;
            estimatedCost.serviceBreakdown.push({
                service: 'Voice Processing',
                provider: `${serviceConfig.sttProvider} + ${serviceConfig.ttsProvider}`,
                credits: voiceCredits,
                costUsd: voiceCost
            });
        }

        // Phone services
        if (workflowDescription.phoneMinutes && serviceConfig.phoneEnabled) {
            const minutes = workflowDescription.phoneMinutes;
            const phoneCredits = Math.max(1, Math.floor(minutes * (serviceConfig.phoneProvider === 'twilio' ? 20 : 35)));
            const phoneCost = minutes * (serviceConfig.phoneProvider === 'twilio' ? 0.0085 : 0.015);

            estimatedCost.totalCredits += phoneCredits;
            estimatedCost.totalCostUsd += phoneCost;
            estimatedCost.serviceBreakdown.push({
                service: 'Phone Service',
                provider: serviceConfig.phoneProvider,
                credits: phoneCredits,
                costUsd: phoneCost
            });
        }

        // Vision services
        if (workflowDescription.imageCount && serviceConfig.visionEnabled) {
            const images = workflowDescription.imageCount;
            const visionCredits = images * (serviceConfig.visionModel.includes('gpt-4o') ? 40 : 50);
            const visionCost = images * (serviceConfig.visionModel.includes('gpt-4o') ? 0.008 : 0.01);

            estimatedCost.totalCredits += visionCredits;
            estimatedCost.totalCostUsd += visionCost;
            estimatedCost.serviceBreakdown.push({
                service: 'Vision Analysis',
                provider: serviceConfig.visionModel,
                credits: visionCredits,
                costUsd: visionCost
            });
        }

        // Warnings
        if (estimatedCost.totalCredits > 100) {
            estimatedCost.warnings.push('High credit usage expected (>100 credits)');
        }

        if (serviceConfig.maxCreditsPerRequest && estimatedCost.totalCredits > serviceConfig.maxCreditsPerRequest) {
            estimatedCost.warnings.push(`Exceeds max credits per request (${serviceConfig.maxCreditsPerRequest})`);
        }

        return estimatedCost;
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

// Convenience functions
function createSimpleAgent(
    apiUrl = 'https://nexus.bits-innovate.com',
    apiKey = null,
    instructions = '',
    capabilities = ['text'],
    servicePreset = 'costOptimized'
) {
    let serviceConfig = null;
    switch (servicePreset) {
        case 'premiumQuality':
            serviceConfig = ServicePresets.premiumQuality();
            break;
        case 'balanced':
            serviceConfig = ServicePresets.balanced();
            break;
        case 'emergencyServices':
            serviceConfig = ServicePresets.emergencyServices();
            break;
        default:
            serviceConfig = ServicePresets.costOptimized();
    }

    const client = new NexusAIClient(apiUrl, apiKey);
    const config = {
        instructions,
        capabilities,
        serviceConfiguration: serviceConfig
    };

    return client.createAgent(config).then(result => {
        const sessionId = result.session_id;
        const session = new AgentSession(client, sessionId);
        return [client, { id: result.agent_id }, session];
    });
}

function createEmergencyAgent(
    apiUrl = 'https://nexus.bits-innovate.com',
    apiKey = null,
    emergencyType = 'medical'
) {
    return createSimpleAgent(
        apiUrl,
        apiKey,
        `You are an emergency ${emergencyType} assistant. Prioritize accuracy and clear communication.`,
        ['text', 'voice', 'phone'],
        'emergencyServices'
    );
}

function createLearningAgent(
    apiUrl = 'https://nexus.bits-innovate.com',
    apiKey = null,
    subject = 'general'
) {
    return createSimpleAgent(
        apiUrl,
        apiKey,
        `You are a ${subject} tutor. Provide clear, educational responses with examples.`,
        ['text', 'voice'],
        'costOptimized'
    );
}

// Export for Node.js and browser
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        NexusAIClient,
        AgentSession,
        ServiceConfiguration,
        ServicePresets,
        AIModel,
        VoiceProvider,
        PhoneProvider,
        createSimpleAgent,
        createEmergencyAgent,
        createLearningAgent
    };
} else if (typeof window !== 'undefined') {
    window.NexusAI = {
        NexusAIClient,
        AgentSession,
        ServiceConfiguration,
        ServicePresets,
        AIModel,
        VoiceProvider,
        PhoneProvider,
        createSimpleAgent,
        createEmergencyAgent,
        createLearningAgent
    };
}

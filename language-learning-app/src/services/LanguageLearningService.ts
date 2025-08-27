import { AgentSessionConfig, Message, UniversalAIConfig } from '../types';
import { API_CONFIG } from '../constants';

// Import the Universal AI SDK (we'll need to modify it slightly for React Native)
import './universal-ai-sdk.js';

declare global {
  interface Window {
    UniversalAI: {
      UniversalAIClient: any;
      AgentSession: any;
      createSimpleAgent: any;
    };
  }
}

export class LanguageLearningService {
  private client: any;
  private currentSession: any = null;
  private config: UniversalAIConfig;

  constructor(config?: Partial<UniversalAIConfig>) {
    this.config = {
      apiUrl: config?.apiUrl || API_CONFIG.BASE_URL,
      apiKey: config?.apiKey,
      clientId: config?.clientId || API_CONFIG.CLIENT_ID,
    };

    // Initialize the Universal AI client
    if (typeof window !== 'undefined' && window.UniversalAI) {
      this.client = new window.UniversalAI.UniversalAIClient(
        this.config.apiUrl,
        this.config.apiKey
      );
    } else {
      throw new Error('Universal AI SDK not loaded properly');
    }
  }

  /**
   * Create a new language learning session
   */
  async createLearningSession(config: AgentSessionConfig): Promise<string> {
    try {
      const agentConfig = {
        instructions: config.instructions,
        capabilities: config.capabilities,
        businessLogicAdapter: config.businessLogicAdapter,
        customSettings: config.customSettings,
        clientId: this.config.clientId,
      };

      const result = await this.client.createAgent(agentConfig);
      const sessionId = result.session_id;

      // Create agent session wrapper
      this.currentSession = {
        id: sessionId,
        client: this.client,
        config: config,
        messages: [],
        startTime: new Date(),
      };

      return sessionId;
    } catch (error) {
      console.error('Failed to create learning session:', error);
      throw new Error('Failed to create learning session');
    }
  }

  /**
   * Send a message to the current session
   */
  async sendMessage(message: string, type: 'text' | 'audio' = 'text'): Promise<void> {
    if (!this.currentSession) {
      throw new Error('No active learning session');
    }

    try {
      await this.client.sendMessage(this.currentSession.id, message, type);
      
      // Add user message to local cache
      const userMessage: Message = {
        id: Date.now().toString(),
        sessionId: this.currentSession.id,
        type: 'user',
        content: message,
        timestamp: new Date(),
      };
      
      this.currentSession.messages.push(userMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
      throw new Error('Failed to send message');
    }
  }

  /**
   * Get new messages from the agent
   */
  async getNewMessages(): Promise<Message[]> {
    if (!this.currentSession) {
      throw new Error('No active learning session');
    }

    try {
      const allMessages = await this.client.getMessages(this.currentSession.id);
      
      // Filter out messages we already have
      const knownIds = new Set(this.currentSession.messages.map((msg: Message) => msg.id));
      const newMessages = allMessages.filter((msg: any) => !knownIds.has(msg.id));
      
      // Convert to our Message format
      const formattedMessages: Message[] = newMessages.map((msg: any) => ({
        id: msg.id,
        sessionId: this.currentSession.id,
        type: msg.sender === 'assistant' ? 'agent' : 'user',
        content: msg.content,
        timestamp: new Date(msg.timestamp),
      }));

      // Add to local cache
      this.currentSession.messages.push(...formattedMessages);
      
      return formattedMessages;
    } catch (error) {
      console.error('Failed to get messages:', error);
      throw new Error('Failed to get messages');
    }
  }

  /**
   * Wait for agent response
   */
  async waitForResponse(timeout: number = 30000): Promise<Message | null> {
    if (!this.currentSession) {
      throw new Error('No active learning session');
    }

    const startTime = Date.now();
    const pollInterval = 500;

    return new Promise((resolve) => {
      const checkForResponse = async () => {
        if (Date.now() - startTime >= timeout) {
          resolve(null);
          return;
        }

        try {
          const newMessages = await this.getNewMessages();
          
          // Look for agent messages
          for (const message of newMessages) {
            if (message.type === 'agent') {
              resolve(message);
              return;
            }
          }
          
          // Continue checking
          setTimeout(checkForResponse, pollInterval);
        } catch (error) {
          console.error('Error waiting for response:', error);
          setTimeout(checkForResponse, pollInterval);
        }
      };

      checkForResponse();
    });
  }

  /**
   * Get session status
   */
  async getSessionStatus(): Promise<any> {
    if (!this.currentSession) {
      throw new Error('No active learning session');
    }

    try {
      return await this.client.getSessionStatus(this.currentSession.id);
    } catch (error) {
      console.error('Failed to get session status:', error);
      throw new Error('Failed to get session status');
    }
  }

  /**
   * Get all messages in the current session
   */
  getSessionMessages(): Message[] {
    if (!this.currentSession) {
      return [];
    }
    return this.currentSession.messages;
  }

  /**
   * Get current session info
   */
  getCurrentSession() {
    return this.currentSession;
  }

  /**
   * Close the current session
   */
  async closeSession(): Promise<void> {
    if (!this.currentSession) {
      return;
    }

    try {
      await this.client.deleteSession(this.currentSession.id);
      this.currentSession = null;
    } catch (error) {
      console.error('Failed to close session:', error);
      throw new Error('Failed to close session');
    }
  }

  /**
   * Get usage statistics
   */
  async getUsageStats(): Promise<any> {
    try {
      return await this.client.getUsageSummary(this.config.clientId);
    } catch (error) {
      console.error('Failed to get usage stats:', error);
      throw new Error('Failed to get usage stats');
    }
  }

  /**
   * Get billing information
   */
  async getBillingInfo(planId: string = 'starter'): Promise<any> {
    try {
      return await this.client.getBillingInfo(this.config.clientId, planId);
    } catch (error) {
      console.error('Failed to get billing info:', error);
      throw new Error('Failed to get billing info');
    }
  }

  /**
   * Check if there's an active session
   */
  hasActiveSession(): boolean {
    return this.currentSession !== null;
  }

  /**
   * Get session duration in minutes
   */
  getSessionDuration(): number {
    if (!this.currentSession) {
      return 0;
    }
    
    const now = new Date();
    const startTime = this.currentSession.startTime;
    return Math.floor((now.getTime() - startTime.getTime()) / (1000 * 60));
  }

  /**
   * Get message count for the current session
   */
  getMessageCount(): number {
    if (!this.currentSession) {
      return 0;
    }
    return this.currentSession.messages.length;
  }
}

// Export singleton instance
export const languageLearningService = new LanguageLearningService();
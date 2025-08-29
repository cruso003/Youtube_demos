// TypeScript definitions for NexusAI JavaScript SDK

export interface AgentConfig {
  instructions: string;
  capabilities: string[];
  business_logic_adapter?: string;
  custom_settings?: Record<string, any>;
  client_id?: string;
}

export interface Message {
  id: string;
  type: 'text' | 'image' | 'audio';
  content: string;
  timestamp: string;
  sender: 'user' | 'assistant';
}

export interface Agent {
  id: string;
  config: AgentConfig;
  created_at: string;
  status: string;
}

export interface SessionConfig {
  session_id?: string;
  agent_id: string;
  client_id?: string;
}

export class NexusAIClient {
  constructor(apiUrl?: string, apiKey?: string);
  
  // Agent Management
  createAgent(config: AgentConfig): Promise<Agent>;
  getAgent(agentId: string): Promise<Agent>;
  updateAgent(agentId: string, config: Partial<AgentConfig>): Promise<Agent>;
  deleteAgent(agentId: string): Promise<void>;
  listAgents(): Promise<Agent[]>;
  
  // Session Management
  createSession(config: SessionConfig): Promise<any>;
  getSession(sessionId: string): Promise<any>;
  deleteSession(sessionId: string): Promise<void>;
  listActiveSessions(): Promise<any[]>;
  
  // Messaging
  sendMessage(sessionId: string, message: string, messageType?: string): Promise<any>;
  getMessages(sessionId: string, limit?: number): Promise<Message[]>;
  
  // Voice & Multimodal
  sendVoiceMessage(sessionId: string, audioData: ArrayBuffer): Promise<any>;
  sendImageMessage(sessionId: string, imageData: ArrayBuffer): Promise<any>;
  
  // Health & Status
  healthCheck(): Promise<any>;
}

export class AgentSession {
  constructor(client: NexusAIClient, sessionId: string);
  
  sendMessage(message: string, messageType?: string): Promise<any>;
  sendVoice(audioData: ArrayBuffer): Promise<any>;
  sendImage(imageData: ArrayBuffer): Promise<any>;
  getHistory(limit?: number): Promise<Message[]>;
  close(): Promise<void>;
}

export function createSimpleAgent(
  apiUrl?: string,
  instructions?: string,
  capabilities?: string[]
): Promise<{ client: NexusAIClient; agent: Agent; session: AgentSession }>;

export default NexusAIClient;

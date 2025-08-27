export interface Language {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  region: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  preferredLanguages: string[];
  subscriptionPlan: SubscriptionPlan;
  createdAt: Date;
}

export interface LearningSession {
  id: string;
  userId: string;
  targetLanguage: string;
  proficiencyLevel: ProficiencyLevel;
  sessionType: SessionType;
  startTime: Date;
  endTime?: Date;
  duration: number; // in minutes
  messageCount: number;
  vocabWordsLearned: string[];
  achievements: Achievement[];
}

export interface Message {
  id: string;
  sessionId: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  audioUrl?: string;
  pronunciationScore?: number;
  corrections?: Correction[];
}

export interface Correction {
  originalText: string;
  correctedText: string;
  explanation: string;
  type: 'grammar' | 'vocabulary' | 'pronunciation';
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlockedAt: Date;
  category: 'streak' | 'conversation' | 'vocabulary' | 'pronunciation';
}

export interface VocabularyItem {
  word: string;
  translation: string;
  pronunciation: string;
  audioUrl?: string;
  imageUrl?: string;
  exampleSentence: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  learnedAt?: Date;
}

export interface ConversationScenario {
  id: string;
  title: string;
  description: string;
  difficulty: ProficiencyLevel;
  category: string;
  initialPrompt: string;
  expectedDuration: number; // in minutes
  vocabularyFocus: string[];
}

export interface ProgressStats {
  totalSessions: number;
  totalTime: number; // in minutes
  currentStreak: number;
  longestStreak: number;
  vocabularyCount: number;
  conversationsCompleted: number;
  pronunciationAccuracy: number;
  level: ProficiencyLevel;
  xp: number;
  nextLevelXp: number;
}

export interface SubscriptionPlan {
  type: 'free' | 'premium' | 'family';
  dailyLimit: number;
  features: string[];
  expiresAt?: Date;
}

export type ProficiencyLevel = 'beginner' | 'intermediate' | 'advanced';

export type SessionType = 
  | 'free_conversation' 
  | 'scenario_practice' 
  | 'vocabulary_learning' 
  | 'pronunciation_training'
  | 'grammar_focus';

export interface CameraVocabularyResult {
  detectedObjects: DetectedObject[];
  suggestions: VocabularyItem[];
}

export interface DetectedObject {
  label: string;
  confidence: number;
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface VoiceRecording {
  uri: string;
  duration: number;
  size: number;
}

export interface SpeechResult {
  transcript: string;
  confidence: number;
  language: string;
}

export interface UniversalAIConfig {
  apiUrl: string;
  apiKey?: string;
  clientId: string;
}

export interface AgentSessionConfig {
  instructions: string;
  capabilities: ('text' | 'voice' | 'vision')[];
  businessLogicAdapter: string;
  customSettings: {
    targetLanguage: string;
    proficiencyLevel: ProficiencyLevel;
    conversationTopics: string[];
    sessionType?: SessionType;
  };
  clientId: string;
}
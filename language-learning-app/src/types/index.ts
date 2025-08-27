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
  subscriptionPlan: {
    type: 'free' | 'premium';
    dailyLimit: number;
    features: string[];
  };
  createdAt: Date;
}

export interface Message {
  id: string;
  sessionId: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
}

export type ProficiencyLevel = 'beginner' | 'intermediate' | 'advanced';
// Core types for the Corporate Training Platform

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'employee';
  department?: string;
  avatar?: string;
  companyId: string;
  createdAt: Date;
  lastLogin?: Date;
}

export interface Company {
  id: string;
  name: string;
  domain: string;
  industry: string;
  size: 'small' | 'medium' | 'large' | 'enterprise';
  subscription: SubscriptionPlan;
  settings: CompanySettings;
  createdAt: Date;
}

export interface SubscriptionPlan {
  tier: 'starter' | 'professional' | 'enterprise';
  maxEmployees: number;
  features: string[];
  pricePerUser: number;
  billingCycle: 'monthly' | 'annual';
}

export interface CompanySettings {
  allowedDomains: string[];
  trainingModules: string[];
  customBranding: {
    logo?: string;
    primaryColor: string;
    secondaryColor: string;
  };
  aiCoachSettings: {
    enabled: boolean;
    language: string;
    personalityType: 'professional' | 'friendly' | 'motivational';
  };
}

export interface TrainingModule {
  id: string;
  title: string;
  description: string;
  category: TrainingCategory;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedDuration: number; // in minutes
  objectives: string[];
  prerequisites?: string[];
  content: ModuleContent[];
  assessment?: Assessment;
  tags: string[];
  isActive: boolean;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ModuleContent {
  id: string;
  type: 'text' | 'video' | 'interactive' | 'ai_simulation' | 'quiz';
  title: string;
  content: any; // Flexible content structure
  duration?: number;
  order: number;
}

export interface Assessment {
  id: string;
  title: string;
  type: 'quiz' | 'practical' | 'ai_interview' | 'peer_review';
  questions: Question[];
  passingScore: number;
  maxAttempts: number;
  timeLimit?: number;
}

export interface Question {
  id: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay' | 'ai_conversation';
  question: string;
  options?: string[];
  correctAnswer?: string | string[];
  points: number;
  explanation?: string;
}

export interface TrainingSession {
  id: string;
  userId: string;
  moduleId: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'failed';
  startedAt?: Date;
  completedAt?: Date;
  currentStep: number;
  totalSteps: number;
  score?: number;
  timeSpent: number; // in minutes
  aiCoachInteractions: CoachInteraction[];
  notes?: string;
}

export interface CoachInteraction {
  id: string;
  sessionId: string;
  timestamp: Date;
  type: 'guidance' | 'feedback' | 'assessment' | 'motivation';
  content: string;
  userResponse?: string;
  effectiveness?: number; // 1-5 rating
}

export interface EmployeeProgress {
  userId: string;
  companyId: string;
  totalModulesCompleted: number;
  totalTimeSpent: number;
  averageScore: number;
  currentStreak: number;
  achievements: Achievement[];
  skillLevels: SkillLevel[];
  upcomingDeadlines: TrainingDeadline[];
  lastActivity: Date;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  unlockedAt: Date;
  requirements: string[];
}

export interface SkillLevel {
  skill: string;
  level: 'novice' | 'competent' | 'proficient' | 'expert';
  progress: number; // 0-100
  lastAssessed: Date;
  improvementAreas: string[];
}

export interface TrainingDeadline {
  moduleId: string;
  moduleName: string;
  dueDate: Date;
  priority: 'low' | 'medium' | 'high';
  assignedBy: string;
}

export interface AnalyticsData {
  companyId: string;
  period: {
    start: Date;
    end: Date;
  };
  metrics: {
    totalEmployees: number;
    activeEmployees: number;
    completionRate: number;
    averageScore: number;
    totalTimeSpent: number;
    popularModules: ModulePopularity[];
    departmentPerformance: DepartmentMetrics[];
    skillsGrowth: SkillsGrowthData[];
  };
}

export interface ModulePopularity {
  moduleId: string;
  moduleName: string;
  completions: number;
  averageScore: number;
  averageTime: number;
  satisfactionRating: number;
}

export interface DepartmentMetrics {
  department: string;
  employeeCount: number;
  completionRate: number;
  averageScore: number;
  topPerformers: string[];
  strugglingEmployees: string[];
}

export interface SkillsGrowthData {
  skill: string;
  startLevel: number;
  currentLevel: number;
  growth: number;
  employeesImproved: number;
}

export type TrainingCategory = 
  | 'sales'
  | 'customer_service'
  | 'leadership'
  | 'technical'
  | 'compliance'
  | 'safety'
  | 'communication'
  | 'project_management'
  | 'diversity_inclusion'
  | 'cybersecurity';

export interface UniversalAIConfig {
  apiUrl: string;
  apiKey?: string;
  clientId: string;
}

export interface AICoachSession {
  id: string;
  userId: string;
  moduleId: string;
  sessionType: 'training' | 'assessment' | 'feedback' | 'practice';
  startTime: Date;
  endTime?: Date;
  interactions: CoachInteraction[];
  outcome?: {
    score?: number;
    feedback: string;
    recommendations: string[];
    nextSteps: string[];
  };
}
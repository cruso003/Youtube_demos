import { Language, ConversationScenario, Achievement } from '../types';

export const SUPPORTED_LANGUAGES: Language[] = [
  // European Languages
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸', region: 'Europe' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷', region: 'Europe' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪', region: 'Europe' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹', region: 'Europe' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹', region: 'Europe' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский', flag: '🇷🇺', region: 'Europe' },
  { code: 'nl', name: 'Dutch', nativeName: 'Nederlands', flag: '🇳🇱', region: 'Europe' },
  { code: 'sv', name: 'Swedish', nativeName: 'Svenska', flag: '🇸🇪', region: 'Europe' },
  { code: 'no', name: 'Norwegian', nativeName: 'Norsk', flag: '🇳🇴', region: 'Europe' },
  { code: 'da', name: 'Danish', nativeName: 'Dansk', flag: '🇩🇰', region: 'Europe' },
  { code: 'fi', name: 'Finnish', nativeName: 'Suomi', flag: '🇫🇮', region: 'Europe' },
  { code: 'pl', name: 'Polish', nativeName: 'Polski', flag: '🇵🇱', region: 'Europe' },
  { code: 'cs', name: 'Czech', nativeName: 'Čeština', flag: '🇨🇿', region: 'Europe' },
  { code: 'hu', name: 'Hungarian', nativeName: 'Magyar', flag: '🇭🇺', region: 'Europe' },
  { code: 'ro', name: 'Romanian', nativeName: 'Română', flag: '🇷🇴', region: 'Europe' },
  { code: 'bg', name: 'Bulgarian', nativeName: 'Български', flag: '🇧🇬', region: 'Europe' },
  { code: 'hr', name: 'Croatian', nativeName: 'Hrvatski', flag: '🇭🇷', region: 'Europe' },
  { code: 'sl', name: 'Slovenian', nativeName: 'Slovenščina', flag: '🇸🇮', region: 'Europe' },
  { code: 'sk', name: 'Slovak', nativeName: 'Slovenčina', flag: '🇸🇰', region: 'Europe' },
  { code: 'et', name: 'Estonian', nativeName: 'Eesti', flag: '🇪🇪', region: 'Europe' },
  { code: 'lv', name: 'Latvian', nativeName: 'Latviešu', flag: '🇱🇻', region: 'Europe' },
  { code: 'lt', name: 'Lithuanian', nativeName: 'Lietuvių', flag: '🇱🇹', region: 'Europe' },
  { code: 'el', name: 'Greek', nativeName: 'Ελληνικά', flag: '🇬🇷', region: 'Europe' },

  // Asian Languages
  { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳', region: 'Asia' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語', flag: '🇯🇵', region: 'Asia' },
  { code: 'ko', name: 'Korean', nativeName: '한국어', flag: '🇰🇷', region: 'Asia' },
  { code: 'th', name: 'Thai', nativeName: 'ไทย', flag: '🇹🇭', region: 'Asia' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt', flag: '🇻🇳', region: 'Asia' },
  { code: 'id', name: 'Indonesian', nativeName: 'Bahasa Indonesia', flag: '🇮🇩', region: 'Asia' },
  { code: 'ms', name: 'Malay', nativeName: 'Bahasa Melayu', flag: '🇲🇾', region: 'Asia' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳', region: 'Asia' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', flag: '🇧🇩', region: 'Asia' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', flag: '🇵🇰', region: 'Asia' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', flag: '🇮🇳', region: 'Asia' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', flag: '🇮🇳', region: 'Asia' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳', region: 'Asia' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', flag: '🇮🇳', region: 'Asia' },

  // Middle Eastern & African Languages
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦', region: 'Middle East' },
  { code: 'he', name: 'Hebrew', nativeName: 'עברית', flag: '🇮🇱', region: 'Middle East' },
  { code: 'fa', name: 'Persian', nativeName: 'فارسی', flag: '🇮🇷', region: 'Middle East' },
  { code: 'tr', name: 'Turkish', nativeName: 'Türkçe', flag: '🇹🇷', region: 'Middle East' },
  { code: 'sw', name: 'Swahili', nativeName: 'Kiswahili', flag: '🇰🇪', region: 'Africa' },
  { code: 'am', name: 'Amharic', nativeName: 'አማርኛ', flag: '🇪🇹', region: 'Africa' },
  { code: 'ha', name: 'Hausa', nativeName: 'Harshen Hausa', flag: '🇳🇬', region: 'Africa' },
  { code: 'yo', name: 'Yoruba', nativeName: 'Èdè Yorùbá', flag: '🇳🇬', region: 'Africa' },
  { code: 'ig', name: 'Igbo', nativeName: 'Asụsụ Igbo', flag: '🇳🇬', region: 'Africa' },
  { code: 'zu', name: 'Zulu', nativeName: 'isiZulu', flag: '🇿🇦', region: 'Africa' },
  { code: 'af', name: 'Afrikaans', nativeName: 'Afrikaans', flag: '🇿🇦', region: 'Africa' },

  // Other Languages
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸', region: 'Americas' },
  { code: 'pt-br', name: 'Portuguese (Brazil)', nativeName: 'Português Brasileiro', flag: '🇧🇷', region: 'Americas' },
];

export const CONVERSATION_SCENARIOS: ConversationScenario[] = [
  {
    id: 'restaurant',
    title: 'At the Restaurant',
    description: 'Practice ordering food and drinks',
    difficulty: 'beginner',
    category: 'Daily Life',
    initialPrompt: 'You are at a restaurant and want to order your favorite meal.',
    expectedDuration: 10,
    vocabularyFocus: ['food', 'drinks', 'ordering', 'payment']
  },
  {
    id: 'shopping',
    title: 'Shopping for Clothes',
    description: 'Learn to shop for clothing items',
    difficulty: 'beginner',
    category: 'Daily Life',
    initialPrompt: 'You are shopping for clothes and need help finding the right size.',
    expectedDuration: 12,
    vocabularyFocus: ['clothes', 'sizes', 'colors', 'prices']
  },
  {
    id: 'airport',
    title: 'At the Airport',
    description: 'Navigate airport procedures and travel',
    difficulty: 'intermediate',
    category: 'Travel',
    initialPrompt: 'You are at the airport checking in for your flight.',
    expectedDuration: 15,
    vocabularyFocus: ['travel', 'airport', 'directions', 'time']
  },
  {
    id: 'hotel',
    title: 'Hotel Check-in',
    description: 'Book and check into a hotel',
    difficulty: 'intermediate',
    category: 'Travel',
    initialPrompt: 'You are checking into a hotel and have a reservation.',
    expectedDuration: 8,
    vocabularyFocus: ['accommodation', 'booking', 'facilities', 'complaints']
  },
  {
    id: 'business_meeting',
    title: 'Business Meeting',
    description: 'Professional business conversations',
    difficulty: 'advanced',
    category: 'Professional',
    initialPrompt: 'You are attending a business meeting to discuss a new project.',
    expectedDuration: 20,
    vocabularyFocus: ['business', 'meetings', 'presentations', 'negotiations']
  },
  {
    id: 'job_interview',
    title: 'Job Interview',
    description: 'Practice interview skills',
    difficulty: 'advanced',
    category: 'Professional',
    initialPrompt: 'You are being interviewed for your dream job.',
    expectedDuration: 25,
    vocabularyFocus: ['career', 'skills', 'experience', 'goals']
  },
  {
    id: 'doctors_visit',
    title: 'Doctor\'s Appointment',
    description: 'Discuss health and medical issues',
    difficulty: 'intermediate',
    category: 'Health',
    initialPrompt: 'You are visiting the doctor because you are not feeling well.',
    expectedDuration: 12,
    vocabularyFocus: ['health', 'symptoms', 'medicine', 'appointments']
  },
  {
    id: 'making_friends',
    title: 'Making New Friends',
    description: 'Social conversations and building relationships',
    difficulty: 'beginner',
    category: 'Social',
    initialPrompt: 'You meet someone new at a coffee shop and want to become friends.',
    expectedDuration: 15,
    vocabularyFocus: ['hobbies', 'interests', 'social', 'friendship']
  }
];

export const ACHIEVEMENTS: Achievement[] = [
  {
    id: 'first_conversation',
    title: 'First Steps',
    description: 'Complete your first conversation',
    icon: '🎯',
    category: 'conversation',
    unlockedAt: new Date()
  },
  {
    id: 'week_streak',
    title: 'Week Warrior',
    description: 'Practice for 7 days in a row',
    icon: '🔥',
    category: 'streak',
    unlockedAt: new Date()
  },
  {
    id: 'hundred_words',
    title: 'Word Collector',
    description: 'Learn 100 new vocabulary words',
    icon: '📚',
    category: 'vocabulary',
    unlockedAt: new Date()
  },
  {
    id: 'pronunciation_master',
    title: 'Pronunciation Pro',
    description: 'Achieve 90% pronunciation accuracy',
    icon: '🎤',
    category: 'pronunciation',
    unlockedAt: new Date()
  }
];

export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  CLIENT_ID: 'language_learning_app',
  ENDPOINTS: {
    CREATE_AGENT: '/api/v1/agent/create',
    SEND_MESSAGE: '/api/v1/agent/{sessionId}/message',
    GET_MESSAGES: '/api/v1/agent/{sessionId}/messages',
    GET_STATUS: '/api/v1/agent/{sessionId}/status',
    DELETE_SESSION: '/api/v1/agent/{sessionId}',
    GET_USAGE: '/api/v1/usage/{clientId}',
    GET_BILLING: '/api/v1/billing/{clientId}'
  }
};

export const SUBSCRIPTION_PLANS = {
  free: {
    type: 'free' as const,
    dailyLimit: 10,
    features: [
      'Basic conversation practice',
      '10 messages per day',
      'Text-only conversations',
      'Basic progress tracking'
    ]
  },
  premium: {
    type: 'premium' as const,
    dailyLimit: -1, // unlimited
    features: [
      'Unlimited conversations',
      'Voice practice with feedback',
      'Camera-based vocabulary learning',
      'Advanced progress analytics',
      'Offline mode',
      'All conversation scenarios',
      'Priority support'
    ]
  },
  family: {
    type: 'family' as const,
    dailyLimit: -1, // unlimited
    features: [
      'Everything in Premium',
      'Up to 6 family members',
      'Parental controls',
      'Family progress sharing',
      'Kid-safe content filtering'
    ]
  }
};

export const COLORS = {
  primary: '#4A90E2',
  primaryDark: '#357ABD',
  secondary: '#F39C12',
  success: '#27AE60',
  warning: '#F39C12',
  error: '#E74C3C',
  background: '#F8F9FA',
  surface: '#FFFFFF',
  text: '#2C3E50',
  textLight: '#7F8C8D',
  border: '#E1E8ED',
  accent: '#9B59B6',
  
  // Gradients
  gradientPrimary: ['#4A90E2', '#357ABD'],
  gradientSecondary: ['#F39C12', '#E67E22'],
  gradientSuccess: ['#27AE60', '#2ECC71'],
};

export const FONTS = {
  regular: 'System',
  medium: 'System',
  bold: 'System',
  light: 'System',
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const STORAGE_KEYS = {
  USER_PROFILE: 'user_profile',
  LEARNING_PROGRESS: 'learning_progress',
  VOCABULARY_WORDS: 'vocabulary_words',
  CONVERSATION_HISTORY: 'conversation_history',
  APP_SETTINGS: 'app_settings',
  SUBSCRIPTION_INFO: 'subscription_info',
  OFFLINE_DATA: 'offline_data',
};
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

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const SUPPORTED_LANGUAGES = [
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸', region: 'Europe' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷', region: 'Europe' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪', region: 'Europe' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹', region: 'Europe' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹', region: 'Europe' },
  { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳', region: 'Asia' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語', flag: '🇯🇵', region: 'Asia' },
  { code: 'ko', name: 'Korean', nativeName: '한국어', flag: '🇰🇷', region: 'Asia' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦', region: 'Middle East' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳', region: 'Asia' },
];

export const CONVERSATION_SCENARIOS = [
  {
    id: 'restaurant',
    title: 'At the Restaurant',
    description: 'Practice ordering food and drinks',
    difficulty: 'beginner' as const,
    category: 'Daily Life',
    initialPrompt: 'You are at a restaurant and want to order your favorite meal.',
    expectedDuration: 10,
    vocabularyFocus: ['food', 'drinks', 'ordering', 'payment']
  },
  {
    id: 'shopping',
    title: 'Shopping for Clothes',
    description: 'Learn to shop for clothing items',
    difficulty: 'beginner' as const,
    category: 'Daily Life',
    initialPrompt: 'You are shopping for clothes and need help finding the right size.',
    expectedDuration: 12,
    vocabularyFocus: ['clothes', 'sizes', 'colors', 'prices']
  },
];
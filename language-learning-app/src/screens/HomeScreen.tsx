import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { StackNavigationProp } from '@react-navigation/stack';
import { CompositeNavigationProp } from '@react-navigation/native';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';

import { RootStackParamList, TabParamList } from '../navigation/AppNavigator';
import { StorageService } from '../services/StorageService';
import { CONVERSATION_SCENARIOS, COLORS, SPACING, SUPPORTED_LANGUAGES } from '../constants';
import { User, ProgressStats, SubscriptionPlan } from '../types';

type HomeScreenNavigationProp = CompositeNavigationProp<
  BottomTabNavigationProp<TabParamList, 'Home'>,
  StackNavigationProp<RootStackParamList>
>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }: Props) {
  const [user, setUser] = useState<User | null>(null);
  const [progress, setProgress] = useState<ProgressStats | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await StorageService.getUserProfile();
      const progressData = await StorageService.getProgress();
      
      setUser(userData);
      setProgress(progressData);
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  const handleStartConversation = () => {
    if (!user || !progress) return;

    const targetLanguage = user.preferredLanguages[0];
    const language = SUPPORTED_LANGUAGES.find(l => l.code === targetLanguage);

    if (!language) {
      Alert.alert('Error', 'Please select a target language first.');
      return;
    }

    // Check subscription limits
    if (user.subscriptionPlan.type === 'free' && progress.totalSessions >= user.subscriptionPlan.dailyLimit) {
      Alert.alert(
        'Daily Limit Reached',
        'You have reached your daily conversation limit. Upgrade to Premium for unlimited conversations!',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Upgrade', onPress: () => navigation.navigate('Subscription') },
        ]
      );
      return;
    }

    navigation.navigate('Conversation', {
      targetLanguage: language.name,
      proficiencyLevel: progress.level,
    });
  };

  const handleScenarioPractice = () => {
    if (!user || !progress) return;

    const targetLanguage = user.preferredLanguages[0];
    const language = SUPPORTED_LANGUAGES.find(l => l.code === targetLanguage);

    if (!language) {
      Alert.alert('Error', 'Please select a target language first.');
      return;
    }

    navigation.navigate('ScenarioSelection', {
      targetLanguage: language.name,
      proficiencyLevel: progress.level,
    });
  };

  const handleCameraLearning = () => {
    if (!user) return;

    const targetLanguage = user.preferredLanguages[0];
    const language = SUPPORTED_LANGUAGES.find(l => l.code === targetLanguage);

    if (!language) {
      Alert.alert('Error', 'Please select a target language first.');
      return;
    }

    if (user.subscriptionPlan.type === 'free') {
      Alert.alert(
        'Premium Feature',
        'Camera-based vocabulary learning is available for Premium subscribers only.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Upgrade', onPress: () => navigation.navigate('Subscription') },
        ]
      );
      return;
    }

    navigation.navigate('CameraVocabulary', {
      targetLanguage: language.name,
    });
  };

  const renderWelcomeCard = () => {
    if (!user || !progress) return null;

    const targetLanguage = user.preferredLanguages[0];
    const language = SUPPORTED_LANGUAGES.find(l => l.code === targetLanguage);

    return (
      <LinearGradient
        colors={COLORS.gradientPrimary}
        style={styles.welcomeCard}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.welcomeContent}>
          <Text style={styles.welcomeGreeting}>Welcome back, {user.name}! 👋</Text>
          <Text style={styles.welcomeText}>
            Continue learning {language?.name || 'your target language'}
          </Text>
          <View style={styles.streakContainer}>
            <Ionicons name="flame" size={20} color="#FF6B35" />
            <Text style={styles.streakText}>{progress.currentStreak} day streak</Text>
          </View>
        </View>
        <Text style={styles.welcomeFlag}>{language?.flag || '🌍'}</Text>
      </LinearGradient>
    );
  };

  const renderQuickStats = () => {
    if (!progress) return null;

    const stats = [
      { label: 'XP', value: progress.xp, icon: 'star', color: '#F39C12' },
      { label: 'Words', value: progress.vocabularyCount, icon: 'library', color: '#27AE60' },
      { label: 'Sessions', value: progress.totalSessions, icon: 'chatbubbles', color: '#3498DB' },
      { label: 'Time', value: `${Math.floor(progress.totalTime / 60)}h`, icon: 'time', color: '#9B59B6' },
    ];

    return (
      <View style={styles.statsContainer}>
        {stats.map((stat, index) => (
          <View key={index} style={styles.statCard}>
            <Ionicons name={stat.icon as any} size={24} color={stat.color} />
            <Text style={styles.statValue}>{stat.value}</Text>
            <Text style={styles.statLabel}>{stat.label}</Text>
          </View>
        ))}
      </View>
    );
  };

  const renderLearningModes = () => {
    const modes = [
      {
        title: 'Free Conversation',
        description: 'Chat with AI tutor about anything',
        icon: 'chatbubbles',
        color: COLORS.gradientPrimary,
        onPress: handleStartConversation,
        premium: false,
      },
      {
        title: 'Scenario Practice',
        description: 'Practice real-world situations',
        icon: 'people',
        color: COLORS.gradientSecondary,
        onPress: handleScenarioPractice,
        premium: false,
      },
      {
        title: 'Camera Learning',
        description: 'Learn vocabulary with AR',
        icon: 'camera',
        color: COLORS.gradientSuccess,
        onPress: handleCameraLearning,
        premium: true,
      },
    ];

    return (
      <View style={styles.modesContainer}>
        <Text style={styles.sectionTitle}>Learning Modes</Text>
        {modes.map((mode, index) => (
          <TouchableOpacity
            key={index}
            style={styles.modeCard}
            onPress={mode.onPress}
          >
            <LinearGradient
              colors={mode.color}
              style={styles.modeIconContainer}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              <Ionicons name={mode.icon as any} size={28} color="#FFFFFF" />
            </LinearGradient>
            <View style={styles.modeContent}>
              <View style={styles.modeTitleContainer}>
                <Text style={styles.modeTitle}>{mode.title}</Text>
                {mode.premium && (
                  <View style={styles.premiumBadge}>
                    <Text style={styles.premiumBadgeText}>PRO</Text>
                  </View>
                )}
              </View>
              <Text style={styles.modeDescription}>{mode.description}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.textLight} />
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  const renderRecentScenarios = () => {
    const recentScenarios = CONVERSATION_SCENARIOS.slice(0, 3);

    return (
      <View style={styles.scenariosContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Quick Start</Text>
          <TouchableOpacity onPress={handleScenarioPractice}>
            <Text style={styles.seeAllText}>See all</Text>
          </TouchableOpacity>
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {recentScenarios.map((scenario, index) => (
            <TouchableOpacity
              key={scenario.id}
              style={styles.scenarioCard}
              onPress={() => {
                if (!user || !progress) return;
                const targetLanguage = user.preferredLanguages[0];
                const language = SUPPORTED_LANGUAGES.find(l => l.code === targetLanguage);
                
                navigation.navigate('Conversation', {
                  scenarioId: scenario.id,
                  targetLanguage: language?.name || 'Spanish',
                  proficiencyLevel: progress.level,
                });
              }}
            >
              <Text style={styles.scenarioTitle}>{scenario.title}</Text>
              <Text style={styles.scenarioDescription}>{scenario.description}</Text>
              <View style={styles.scenarioFooter}>
                <Text style={styles.scenarioDifficulty}>{scenario.difficulty}</Text>
                <Text style={styles.scenarioDuration}>{scenario.expectedDuration}min</Text>
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    );
  };

  if (!user || !progress) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {renderWelcomeCard()}
      {renderQuickStats()}
      {renderLearningModes()}
      {renderRecentScenarios()}
      
      {/* Subscription CTA for free users */}
      {user.subscriptionPlan.type === 'free' && (
        <TouchableOpacity
          style={styles.upgradeCta}
          onPress={() => navigation.navigate('Subscription')}
        >
          <LinearGradient
            colors={['#9B59B6', '#8E44AD']}
            style={styles.upgradeCtaGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <View style={styles.upgradeCtaContent}>
              <Text style={styles.upgradeCtaTitle}>Unlock Premium Features!</Text>
              <Text style={styles.upgradeCtaText}>
                Unlimited conversations, voice practice, and camera learning
              </Text>
            </View>
            <Ionicons name="arrow-forward" size={24} color="#FFFFFF" />
          </LinearGradient>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: COLORS.textLight,
  },
  welcomeCard: {
    margin: SPACING.lg,
    borderRadius: 20,
    padding: SPACING.lg,
    flexDirection: 'row',
    alignItems: 'center',
  },
  welcomeContent: {
    flex: 1,
  },
  welcomeGreeting: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  welcomeText: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.9,
    marginBottom: SPACING.sm,
  },
  streakContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  streakText: {
    fontSize: 14,
    color: '#FFFFFF',
    marginLeft: 4,
    fontWeight: '600',
  },
  welcomeFlag: {
    fontSize: 40,
  },
  statsContainer: {
    flexDirection: 'row',
    marginHorizontal: SPACING.lg,
    marginBottom: SPACING.lg,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.md,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginTop: SPACING.sm,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.textLight,
    marginTop: 2,
  },
  modesContainer: {
    marginHorizontal: SPACING.lg,
    marginBottom: SPACING.lg,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  seeAllText: {
    fontSize: 16,
    color: COLORS.primary,
    fontWeight: '500',
  },
  modeCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.md,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  modeIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  modeContent: {
    flex: 1,
  },
  modeTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  modeTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
  },
  premiumBadge: {
    backgroundColor: '#9B59B6',
    borderRadius: 8,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginLeft: SPACING.sm,
  },
  premiumBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  modeDescription: {
    fontSize: 14,
    color: COLORS.textLight,
  },
  scenariosContainer: {
    marginHorizontal: SPACING.lg,
    marginBottom: SPACING.lg,
  },
  scenarioCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.md,
    width: 200,
    marginRight: SPACING.md,
  },
  scenarioTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  scenarioDescription: {
    fontSize: 14,
    color: COLORS.textLight,
    marginBottom: SPACING.sm,
    lineHeight: 20,
  },
  scenarioFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  scenarioDifficulty: {
    fontSize: 12,
    color: COLORS.primary,
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  scenarioDuration: {
    fontSize: 12,
    color: COLORS.textLight,
  },
  upgradeCta: {
    margin: SPACING.lg,
    borderRadius: 16,
    overflow: 'hidden',
  },
  upgradeCtaGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING.lg,
  },
  upgradeCtaContent: {
    flex: 1,
  },
  upgradeCtaTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  upgradeCtaText: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9,
  },
});
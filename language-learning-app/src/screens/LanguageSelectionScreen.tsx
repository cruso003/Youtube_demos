import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  SafeAreaView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { StackNavigationProp } from '@react-navigation/stack';

import { RootStackParamList } from '../navigation/AppNavigator';
import { StorageService } from '../services/StorageService';
import { SUPPORTED_LANGUAGES, COLORS, SPACING } from '../constants';
import { Language, User, ProficiencyLevel } from '../types';

type LanguageSelectionScreenNavigationProp = StackNavigationProp<
  RootStackParamList,
  'LanguageSelection'
>;

interface Props {
  navigation: LanguageSelectionScreenNavigationProp;
}

const proficiencyLevels: { value: ProficiencyLevel; label: string; description: string }[] = [
  { value: 'beginner', label: 'Beginner', description: 'Just starting out' },
  { value: 'intermediate', label: 'Intermediate', description: 'Some experience' },
  { value: 'advanced', label: 'Advanced', description: 'Confident speaker' },
];

export default function LanguageSelectionScreen({ navigation }: Props) {
  const [selectedLanguage, setSelectedLanguage] = useState<Language | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<ProficiencyLevel>('beginner');
  const [userName, setUserName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState<string>('All');

  const regions = ['All', 'Europe', 'Asia', 'Americas', 'Middle East', 'Africa'];
  
  const filteredLanguages = SUPPORTED_LANGUAGES.filter(language => {
    const matchesSearch = language.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         language.nativeName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRegion = selectedRegion === 'All' || language.region === selectedRegion;
    
    return matchesSearch && matchesRegion;
  });

  const handleLanguageSelect = (language: Language) => {
    setSelectedLanguage(language);
  };

  const handleContinue = async () => {
    if (!selectedLanguage) {
      Alert.alert('Select Language', 'Please choose a language to learn.');
      return;
    }

    if (!userName.trim()) {
      Alert.alert('Enter Name', 'Please enter your name to get started.');
      return;
    }

    try {
      // Create user profile
      const user: User = {
        id: Date.now().toString(),
        name: userName.trim(),
        email: '', // Could be added later
        preferredLanguages: [selectedLanguage.code],
        subscriptionPlan: {
          type: 'free',
          dailyLimit: 10,
          features: ['Basic conversation practice', '10 messages per day']
        },
        createdAt: new Date(),
      };

      // Save user profile
      await StorageService.storeUserProfile(user);

      // Initialize progress stats
      const progressStats = {
        totalSessions: 0,
        totalTime: 0,
        currentStreak: 0,
        longestStreak: 0,
        vocabularyCount: 0,
        conversationsCompleted: 0,
        pronunciationAccuracy: 0,
        level: selectedLevel,
        xp: 0,
        nextLevelXp: 100,
      };

      await StorageService.storeProgress(progressStats);

      // Navigate to main app
      navigation.replace('Main');
    } catch (error) {
      console.error('Error saving user profile:', error);
      Alert.alert('Error', 'Failed to save your profile. Please try again.');
    }
  };

  const renderLanguageCard = (language: Language) => (
    <TouchableOpacity
      key={language.code}
      style={[
        styles.languageCard,
        selectedLanguage?.code === language.code && styles.languageCardSelected,
      ]}
      onPress={() => handleLanguageSelect(language)}
    >
      <Text style={styles.languageFlag}>{language.flag}</Text>
      <View style={styles.languageInfo}>
        <Text style={styles.languageName}>{language.name}</Text>
        <Text style={styles.languageNativeName}>{language.nativeName}</Text>
      </View>
      {selectedLanguage?.code === language.code && (
        <Ionicons name="checkmark-circle" size={24} color={COLORS.primary} />
      )}
    </TouchableOpacity>
  );

  const renderProficiencyCard = (level: typeof proficiencyLevels[0]) => (
    <TouchableOpacity
      key={level.value}
      style={[
        styles.proficiencyCard,
        selectedLevel === level.value && styles.proficiencyCardSelected,
      ]}
      onPress={() => setSelectedLevel(level.value)}
    >
      <Text style={styles.proficiencyLabel}>{level.label}</Text>
      <Text style={styles.proficiencyDescription}>{level.description}</Text>
      {selectedLevel === level.value && (
        <View style={styles.proficiencyCheck}>
          <Ionicons name="checkmark" size={16} color="#FFFFFF" />
        </View>
      )}
    </TouchableOpacity>
  );

  const renderRegionFilter = (region: string) => (
    <TouchableOpacity
      key={region}
      style={[
        styles.regionChip,
        selectedRegion === region && styles.regionChipSelected,
      ]}
      onPress={() => setSelectedRegion(region)}
    >
      <Text
        style={[
          styles.regionChipText,
          selectedRegion === region && styles.regionChipTextSelected,
        ]}
      >
        {region}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Welcome to Language Learning! 🌟</Text>
          <Text style={styles.subtitle}>
            Choose your target language and proficiency level to get started
          </Text>
        </View>

        {/* Name Input */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>What's your name?</Text>
          <TextInput
            style={styles.nameInput}
            placeholder="Enter your name"
            value={userName}
            onChangeText={setUserName}
            placeholderTextColor="#7F8C8D"
          />
        </View>

        {/* Proficiency Level */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your current level</Text>
          <View style={styles.proficiencyContainer}>
            {proficiencyLevels.map(renderProficiencyCard)}
          </View>
        </View>

        {/* Language Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Choose your target language</Text>
          
          {/* Search */}
          <View style={styles.searchContainer}>
            <Ionicons name="search" size={20} color="#7F8C8D" style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search languages..."
              value={searchQuery}
              onChangeText={setSearchQuery}
              placeholderTextColor="#7F8C8D"
            />
          </View>

          {/* Region Filter */}
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.regionFilterContainer}
          >
            {regions.map(renderRegionFilter)}
          </ScrollView>

          {/* Languages Grid */}
          <View style={styles.languagesContainer}>
            {filteredLanguages.map(renderLanguageCard)}
          </View>
        </View>
      </ScrollView>

      {/* Continue Button */}
      <View style={styles.bottomContainer}>
        <TouchableOpacity
          style={[
            styles.continueButton,
            (!selectedLanguage || !userName.trim()) && styles.continueButtonDisabled,
          ]}
          onPress={handleContinue}
          disabled={!selectedLanguage || !userName.trim()}
        >
          <LinearGradient
            colors={
              selectedLanguage && userName.trim()
                ? COLORS.gradientPrimary
                : ['#BDC3C7', '#95A5A6']
            }
            style={styles.continueButtonGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
          >
            <Text style={styles.continueButtonText}>Continue</Text>
            <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.xl,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.text,
    textAlign: 'center',
    marginBottom: SPACING.sm,
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.textLight,
    textAlign: 'center',
    lineHeight: 22,
  },
  section: {
    paddingHorizontal: SPACING.lg,
    marginBottom: SPACING.xl,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  nameInput: {
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 12,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    fontSize: 16,
    backgroundColor: '#FFFFFF',
  },
  proficiencyContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  proficiencyCard: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    padding: SPACING.md,
    marginHorizontal: 4,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  proficiencyCardSelected: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primaryDark,
  },
  proficiencyLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  proficiencyDescription: {
    fontSize: 12,
    color: COLORS.textLight,
    textAlign: 'center',
  },
  proficiencyCheck: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: COLORS.success,
    borderRadius: 8,
    width: 16,
    height: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    paddingHorizontal: SPACING.md,
    marginBottom: SPACING.md,
  },
  searchIcon: {
    marginRight: SPACING.sm,
  },
  searchInput: {
    flex: 1,
    paddingVertical: SPACING.md,
    fontSize: 16,
  },
  regionFilterContainer: {
    marginBottom: SPACING.md,
  },
  regionChip: {
    backgroundColor: '#F8F9FA',
    borderRadius: 20,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    marginRight: SPACING.sm,
  },
  regionChipSelected: {
    backgroundColor: COLORS.primary,
  },
  regionChipText: {
    fontSize: 14,
    color: COLORS.text,
    fontWeight: '500',
  },
  regionChipTextSelected: {
    color: '#FFFFFF',
  },
  languagesContainer: {
    marginTop: SPACING.sm,
  },
  languageCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.md,
    marginBottom: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  languageCardSelected: {
    borderColor: COLORS.primary,
    backgroundColor: '#F0F7FF',
  },
  languageFlag: {
    fontSize: 32,
    marginRight: SPACING.md,
  },
  languageInfo: {
    flex: 1,
  },
  languageName: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 2,
  },
  languageNativeName: {
    fontSize: 14,
    color: COLORS.textLight,
  },
  bottomContainer: {
    paddingHorizontal: SPACING.lg,
    paddingBottom: 30,
    paddingTop: SPACING.md,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  continueButton: {
    borderRadius: 25,
    overflow: 'hidden',
  },
  continueButtonDisabled: {
    opacity: 0.6,
  },
  continueButtonGradient: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    minHeight: 50,
  },
  continueButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginRight: SPACING.sm,
  },
});
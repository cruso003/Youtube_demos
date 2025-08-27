import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, SUPPORTED_LANGUAGES } from './src/constants';

export default function App() {
  const [selectedLanguage, setSelectedLanguage] = React.useState(SUPPORTED_LANGUAGES[0]);

  const renderLanguageCard = (language: typeof SUPPORTED_LANGUAGES[0]) => (
    <TouchableOpacity
      key={language.code}
      style={[
        styles.languageCard,
        selectedLanguage.code === language.code && styles.languageCardSelected,
      ]}
      onPress={() => setSelectedLanguage(language)}
    >
      <Text style={styles.languageFlag}>{language.flag}</Text>
      <View style={styles.languageInfo}>
        <Text style={styles.languageName}>{language.name}</Text>
        <Text style={styles.languageNativeName}>{language.nativeName}</Text>
      </View>
      {selectedLanguage.code === language.code && (
        <Ionicons name="checkmark-circle" size={24} color={COLORS.primary} />
      )}
    </TouchableOpacity>
  );

  const renderFeatureCard = (icon: string, title: string, description: string, color: string[]) => (
    <View style={styles.featureCard}>
      <LinearGradient
        colors={color}
        style={styles.featureIcon}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <Ionicons name={icon as any} size={28} color="#FFFFFF" />
      </LinearGradient>
      <Text style={styles.featureTitle}>{title}</Text>
      <Text style={styles.featureDescription}>{description}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" backgroundColor={COLORS.primary} />
      
      {/* Header */}
      <LinearGradient
        colors={COLORS.gradientPrimary}
        style={styles.header}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <Text style={styles.headerTitle}>🌟 Language Learning</Text>
        <Text style={styles.headerSubtitle}>
          Master any language with AI-powered conversations
        </Text>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        
        {/* Selected Language Display */}
        <View style={styles.selectedLanguageContainer}>
          <Text style={styles.sectionTitle}>Currently Learning</Text>
          <View style={styles.selectedLanguageCard}>
            <Text style={styles.selectedLanguageFlag}>{selectedLanguage.flag}</Text>
            <View style={styles.selectedLanguageInfo}>
              <Text style={styles.selectedLanguageName}>{selectedLanguage.name}</Text>
              <Text style={styles.selectedLanguageNative}>{selectedLanguage.nativeName}</Text>
            </View>
            <View style={styles.levelBadge}>
              <Text style={styles.levelText}>Beginner</Text>
            </View>
          </View>
        </View>

        {/* Features */}
        <View style={styles.featuresContainer}>
          <Text style={styles.sectionTitle}>Key Features</Text>
          <View style={styles.featuresGrid}>
            {renderFeatureCard(
              'chatbubbles',
              'AI Conversations',
              'Practice with intelligent AI tutors',
              COLORS.gradientPrimary
            )}
            {renderFeatureCard(
              'mic',
              'Voice Practice',
              'Perfect pronunciation with feedback',
              COLORS.gradientSecondary
            )}
            {renderFeatureCard(
              'camera',
              'AR Learning',
              'Learn vocabulary with your camera',
              COLORS.gradientSuccess
            )}
            {renderFeatureCard(
              'analytics',
              'Progress Tracking',
              'Monitor your learning journey',
              ['#9B59B6', '#8E44AD']
            )}
          </View>
        </View>

        {/* Language Selection */}
        <View style={styles.languageSelection}>
          <Text style={styles.sectionTitle}>Choose Your Language</Text>
          {SUPPORTED_LANGUAGES.slice(0, 6).map(renderLanguageCard)}
        </View>

        {/* Demo Notice */}
        <View style={styles.demoNotice}>
          <Ionicons name="information-circle" size={24} color={COLORS.primary} />
          <Text style={styles.demoText}>
            This is a demo of the Language Learning App built with React Native and the Universal AI Agent Platform. 
            The app integrates voice recognition, camera-based vocabulary learning, and AI-powered conversations.
          </Text>
        </View>

        {/* Integration Info */}
        <View style={styles.integrationInfo}>
          <Text style={styles.integrationTitle}>Universal AI Platform Integration</Text>
          <View style={styles.integrationItem}>
            <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
            <Text style={styles.integrationText}>Real-time AI conversations</Text>
          </View>
          <View style={styles.integrationItem}>
            <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
            <Text style={styles.integrationText}>Multimodal capabilities (text, voice, vision)</Text>
          </View>
          <View style={styles.integrationItem}>
            <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
            <Text style={styles.integrationText}>Language learning business logic adapter</Text>
          </View>
          <View style={styles.integrationItem}>
            <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
            <Text style={styles.integrationText}>Progress tracking and analytics</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    paddingTop: 20,
    paddingBottom: SPACING.xl,
    paddingHorizontal: SPACING.lg,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: SPACING.sm,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.9,
    textAlign: 'center',
  },
  content: {
    flex: 1,
  },
  selectedLanguageContainer: {
    padding: SPACING.lg,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  selectedLanguageCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: SPACING.lg,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.primary,
  },
  selectedLanguageFlag: {
    fontSize: 40,
    marginRight: SPACING.md,
  },
  selectedLanguageInfo: {
    flex: 1,
  },
  selectedLanguageName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 4,
  },
  selectedLanguageNative: {
    fontSize: 16,
    color: COLORS.textLight,
  },
  levelBadge: {
    backgroundColor: COLORS.success,
    borderRadius: 12,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
  },
  levelText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  featuresContainer: {
    padding: SPACING.lg,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  featureCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.md,
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  featureIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
    textAlign: 'center',
  },
  featureDescription: {
    fontSize: 12,
    color: COLORS.textLight,
    textAlign: 'center',
  },
  languageSelection: {
    padding: SPACING.lg,
  },
  languageCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.md,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  languageCardSelected: {
    borderColor: COLORS.primary,
    backgroundColor: '#F0F7FF',
  },
  languageFlag: {
    fontSize: 24,
    marginRight: SPACING.md,
  },
  languageInfo: {
    flex: 1,
  },
  languageName: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 2,
  },
  languageNativeName: {
    fontSize: 14,
    color: COLORS.textLight,
  },
  demoNotice: {
    margin: SPACING.lg,
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    padding: SPACING.lg,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  demoText: {
    flex: 1,
    fontSize: 14,
    color: COLORS.text,
    marginLeft: SPACING.sm,
    lineHeight: 20,
  },
  integrationInfo: {
    margin: SPACING.lg,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: SPACING.lg,
  },
  integrationTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  integrationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  integrationText: {
    fontSize: 14,
    color: COLORS.text,
    marginLeft: SPACING.sm,
  },
});

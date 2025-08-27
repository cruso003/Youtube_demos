import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  StatusBar,
  Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { StackNavigationProp } from '@react-navigation/stack';
import PagerView from 'react-native-pager-view';

import { RootStackParamList } from '../navigation/AppNavigator';
import { StorageService } from '../services/StorageService';
import { COLORS, SPACING } from '../constants';

type OnboardingScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Onboarding'>;

interface Props {
  navigation: OnboardingScreenNavigationProp;
}

const { width, height } = Dimensions.get('window');

interface OnboardingSlide {
  title: string;
  description: string;
  icon: string;
  color: string[];
}

const onboardingSlides: OnboardingSlide[] = [
  {
    title: 'Learn Any Language',
    description: 'Master 50+ languages with AI-powered conversations and real-time feedback',
    icon: '🌍',
    color: COLORS.gradientPrimary,
  },
  {
    title: 'Practice Speaking',
    description: 'Improve your pronunciation with voice recognition and instant feedback',
    icon: '🎤',
    color: COLORS.gradientSecondary,
  },
  {
    title: 'Visual Learning',
    description: 'Point your camera at objects and learn vocabulary with AR technology',
    icon: '📷',
    color: COLORS.gradientSuccess,
  },
  {
    title: 'Track Progress',
    description: 'Monitor your learning journey with detailed analytics and achievements',
    icon: '📊',
    color: ['#9B59B6', '#8E44AD'],
  },
];

export default function OnboardingScreen({ navigation }: Props) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkFirstTimeUser();
  }, []);

  const checkFirstTimeUser = async () => {
    try {
      const isFirstTime = await StorageService.isFirstTimeUser();
      if (!isFirstTime) {
        // User has used the app before, navigate to main app
        navigation.replace('Main');
      } else {
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error checking first time user:', error);
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (currentSlide < onboardingSlides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    } else {
      handleGetStarted();
    }
  };

  const handleSkip = () => {
    handleGetStarted();
  };

  const handleGetStarted = () => {
    navigation.replace('LanguageSelection');
  };

  const renderSlide = (slide: OnboardingSlide, index: number) => (
    <View key={index} style={styles.slide}>
      <LinearGradient
        colors={slide.color}
        style={styles.slideGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.slideContent}>
          <Text style={styles.slideIcon}>{slide.icon}</Text>
          <Text style={styles.slideTitle}>{slide.title}</Text>
          <Text style={styles.slideDescription}>{slide.description}</Text>
        </View>
      </LinearGradient>
    </View>
  );

  const renderPaginationDots = () => (
    <View style={styles.pagination}>
      {onboardingSlides.map((_, index) => (
        <View
          key={index}
          style={[
            styles.paginationDot,
            currentSlide === index && styles.paginationDotActive,
          ]}
        />
      ))}
    </View>
  );

  if (isLoading) {
    return (
      <LinearGradient
        colors={COLORS.gradientPrimary}
        style={styles.loadingContainer}
      >
        <Text style={styles.loadingIcon}>🌟</Text>
        <Text style={styles.loadingText}>Language Learning</Text>
      </LinearGradient>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />
      
      {/* Skip Button */}
      <TouchableOpacity style={styles.skipButton} onPress={handleSkip}>
        <Text style={styles.skipText}>Skip</Text>
      </TouchableOpacity>

      {/* Slides */}
      <PagerView
        style={styles.pager}
        initialPage={0}
        onPageSelected={(e) => setCurrentSlide(e.nativeEvent.position)}
      >
        {onboardingSlides.map((slide, index) => renderSlide(slide, index))}
      </PagerView>

      {/* Bottom Section */}
      <View style={styles.bottomContainer}>
        {renderPaginationDots()}
        
        <TouchableOpacity style={styles.nextButton} onPress={handleNext}>
          <LinearGradient
            colors={COLORS.gradientPrimary}
            style={styles.nextButtonGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
          >
            {currentSlide === onboardingSlides.length - 1 ? (
              <Text style={styles.nextButtonText}>Get Started</Text>
            ) : (
              <>
                <Text style={styles.nextButtonText}>Next</Text>
                <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
              </>
            )}
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingIcon: {
    fontSize: 60,
    marginBottom: SPACING.lg,
  },
  loadingText: {
    fontSize: 24,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  skipButton: {
    position: 'absolute',
    top: 50,
    right: SPACING.lg,
    zIndex: 1,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
  },
  skipText: {
    fontSize: 16,
    color: '#FFFFFF',
    fontWeight: '500',
  },
  pager: {
    flex: 1,
  },
  slide: {
    flex: 1,
  },
  slideGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  slideContent: {
    alignItems: 'center',
    paddingHorizontal: SPACING.xxl,
  },
  slideIcon: {
    fontSize: 80,
    marginBottom: SPACING.xl,
  },
  slideTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: SPACING.lg,
  },
  slideDescription: {
    fontSize: 18,
    color: '#FFFFFF',
    textAlign: 'center',
    lineHeight: 26,
    opacity: 0.9,
  },
  bottomContainer: {
    paddingHorizontal: SPACING.lg,
    paddingBottom: 50,
    paddingTop: SPACING.lg,
    backgroundColor: '#FFFFFF',
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: SPACING.xl,
  },
  paginationDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E1E8ED',
    marginHorizontal: 4,
  },
  paginationDotActive: {
    backgroundColor: COLORS.primary,
    width: 24,
  },
  nextButton: {
    marginHorizontal: SPACING.lg,
  },
  nextButtonGradient: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    borderRadius: 25,
    minHeight: 50,
  },
  nextButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginRight: SPACING.sm,
  },
});
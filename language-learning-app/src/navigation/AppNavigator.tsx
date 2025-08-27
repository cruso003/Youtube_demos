import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useColorScheme } from 'react-native';

// Import screens
import OnboardingScreen from '../screens/OnboardingScreen';
import LanguageSelectionScreen from '../screens/LanguageSelectionScreen';
import HomeScreen from '../screens/HomeScreen';
import ConversationScreen from '../screens/ConversationScreen';
import CameraVocabularyScreen from '../screens/CameraVocabularyScreen';
import ProgressScreen from '../screens/ProgressScreen';
import ProfileScreen from '../screens/ProfileScreen';
import SubscriptionScreen from '../screens/SubscriptionScreen';
import ScenarioSelectionScreen from '../screens/ScenarioSelectionScreen';
import VocabularyScreen from '../screens/VocabularyScreen';
import SettingsScreen from '../screens/SettingsScreen';

import { COLORS } from '../constants';

export type RootStackParamList = {
  Onboarding: undefined;
  LanguageSelection: undefined;
  Main: undefined;
  Conversation: {
    scenarioId?: string;
    targetLanguage: string;
    proficiencyLevel: string;
  };
  CameraVocabulary: {
    targetLanguage: string;
  };
  ScenarioSelection: {
    targetLanguage: string;
    proficiencyLevel: string;
  };
  Subscription: undefined;
  Settings: undefined;
};

export type TabParamList = {
  Home: undefined;
  Progress: undefined;
  Vocabulary: undefined;
  Profile: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

function TabNavigator() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Progress') {
            iconName = focused ? 'stats-chart' : 'stats-chart-outline';
          } else if (route.name === 'Vocabulary') {
            iconName = focused ? 'library' : 'library-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: isDark ? '#8E8E93' : '#8E8E93',
        tabBarStyle: {
          backgroundColor: isDark ? '#1C1C1E' : '#FFFFFF',
          borderTopColor: isDark ? '#38383A' : '#E1E8ED',
          paddingBottom: 5,
          height: 60,
        },
        headerStyle: {
          backgroundColor: isDark ? '#1C1C1E' : '#FFFFFF',
          borderBottomColor: isDark ? '#38383A' : '#E1E8ED',
        },
        headerTintColor: isDark ? '#FFFFFF' : '#2C3E50',
        headerTitleStyle: {
          fontWeight: '600',
          fontSize: 18,
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: 'Learn',
          headerTitle: '🌟 Language Learning'
        }}
      />
      <Tab.Screen 
        name="Progress" 
        component={ProgressScreen}
        options={{
          title: 'Progress',
          headerTitle: '📊 Your Progress'
        }}
      />
      <Tab.Screen 
        name="Vocabulary" 
        component={VocabularyScreen}
        options={{
          title: 'Vocabulary',
          headerTitle: '📚 Your Vocabulary'
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profile',
          headerTitle: '👤 Profile'
        }}
      />
    </Tab.Navigator>
  );
}

export default function Navigation() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  return (
    <NavigationContainer
      theme={{
        dark: isDark,
        colors: {
          primary: COLORS.primary,
          background: isDark ? '#000000' : '#FFFFFF',
          card: isDark ? '#1C1C1E' : '#FFFFFF',
          text: isDark ? '#FFFFFF' : '#2C3E50',
          border: isDark ? '#38383A' : '#E1E8ED',
          notification: COLORS.error,
        },
      }}
    >
      <Stack.Navigator
        initialRouteName="Onboarding"
        screenOptions={{
          headerStyle: {
            backgroundColor: isDark ? '#1C1C1E' : '#FFFFFF',
            borderBottomColor: isDark ? '#38383A' : '#E1E8ED',
          },
          headerTintColor: isDark ? '#FFFFFF' : '#2C3E50',
          headerTitleStyle: {
            fontWeight: '600',
            fontSize: 18,
          },
          headerBackTitleVisible: false,
        }}
      >
        <Stack.Screen 
          name="Onboarding" 
          component={OnboardingScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="LanguageSelection" 
          component={LanguageSelectionScreen}
          options={{ 
            title: 'Choose Your Language',
            headerLeft: () => null,
            gestureEnabled: false
          }}
        />
        <Stack.Screen 
          name="Main" 
          component={TabNavigator}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="Conversation" 
          component={ConversationScreen}
          options={{ 
            title: 'Practice Conversation',
            presentation: 'modal'
          }}
        />
        <Stack.Screen 
          name="CameraVocabulary" 
          component={CameraVocabularyScreen}
          options={{ 
            title: 'Learn with Camera',
            presentation: 'modal'
          }}
        />
        <Stack.Screen 
          name="ScenarioSelection" 
          component={ScenarioSelectionScreen}
          options={{ 
            title: 'Choose Scenario'
          }}
        />
        <Stack.Screen 
          name="Subscription" 
          component={SubscriptionScreen}
          options={{ 
            title: 'Upgrade to Premium',
            presentation: 'modal'
          }}
        />
        <Stack.Screen 
          name="Settings" 
          component={SettingsScreen}
          options={{ 
            title: 'Settings'
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
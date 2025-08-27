import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, LearningSession, VocabularyItem, ProgressStats, SubscriptionPlan } from '../types';
import { STORAGE_KEYS } from '../constants';

export class StorageService {
  /**
   * Store user profile
   */
  static async storeUserProfile(user: User): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(user));
    } catch (error) {
      console.error('Failed to store user profile:', error);
      throw new Error('Failed to store user profile');
    }
  }

  /**
   * Get user profile
   */
  static async getUserProfile(): Promise<User | null> {
    try {
      const userJson = await AsyncStorage.getItem(STORAGE_KEYS.USER_PROFILE);
      return userJson ? JSON.parse(userJson) : null;
    } catch (error) {
      console.error('Failed to get user profile:', error);
      return null;
    }
  }

  /**
   * Store learning progress
   */
  static async storeProgress(progress: ProgressStats): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.LEARNING_PROGRESS, JSON.stringify(progress));
    } catch (error) {
      console.error('Failed to store progress:', error);
      throw new Error('Failed to store progress');
    }
  }

  /**
   * Get learning progress
   */
  static async getProgress(): Promise<ProgressStats | null> {
    try {
      const progressJson = await AsyncStorage.getItem(STORAGE_KEYS.LEARNING_PROGRESS);
      return progressJson ? JSON.parse(progressJson) : null;
    } catch (error) {
      console.error('Failed to get progress:', error);
      return null;
    }
  }

  /**
   * Store vocabulary words
   */
  static async storeVocabulary(words: VocabularyItem[]): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.VOCABULARY_WORDS, JSON.stringify(words));
    } catch (error) {
      console.error('Failed to store vocabulary:', error);
      throw new Error('Failed to store vocabulary');
    }
  }

  /**
   * Get vocabulary words
   */
  static async getVocabulary(): Promise<VocabularyItem[]> {
    try {
      const vocabJson = await AsyncStorage.getItem(STORAGE_KEYS.VOCABULARY_WORDS);
      return vocabJson ? JSON.parse(vocabJson) : [];
    } catch (error) {
      console.error('Failed to get vocabulary:', error);
      return [];
    }
  }

  /**
   * Add new vocabulary word
   */
  static async addVocabularyWord(word: VocabularyItem): Promise<void> {
    try {
      const existingWords = await this.getVocabulary();
      const updatedWords = [...existingWords, { ...word, learnedAt: new Date() }];
      await this.storeVocabulary(updatedWords);
    } catch (error) {
      console.error('Failed to add vocabulary word:', error);
      throw new Error('Failed to add vocabulary word');
    }
  }

  /**
   * Store learning session
   */
  static async storeLearningSession(session: LearningSession): Promise<void> {
    try {
      const existingSessions = await this.getLearningHistory();
      const updatedSessions = [...existingSessions, session];
      await AsyncStorage.setItem(STORAGE_KEYS.CONVERSATION_HISTORY, JSON.stringify(updatedSessions));
    } catch (error) {
      console.error('Failed to store learning session:', error);
      throw new Error('Failed to store learning session');
    }
  }

  /**
   * Get learning history
   */
  static async getLearningHistory(): Promise<LearningSession[]> {
    try {
      const historyJson = await AsyncStorage.getItem(STORAGE_KEYS.CONVERSATION_HISTORY);
      return historyJson ? JSON.parse(historyJson) : [];
    } catch (error) {
      console.error('Failed to get learning history:', error);
      return [];
    }
  }

  /**
   * Store app settings
   */
  static async storeAppSettings(settings: any): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.APP_SETTINGS, JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to store app settings:', error);
      throw new Error('Failed to store app settings');
    }
  }

  /**
   * Get app settings
   */
  static async getAppSettings(): Promise<any> {
    try {
      const settingsJson = await AsyncStorage.getItem(STORAGE_KEYS.APP_SETTINGS);
      return settingsJson ? JSON.parse(settingsJson) : null;
    } catch (error) {
      console.error('Failed to get app settings:', error);
      return null;
    }
  }

  /**
   * Store subscription info
   */
  static async storeSubscriptionInfo(subscription: SubscriptionPlan): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.SUBSCRIPTION_INFO, JSON.stringify(subscription));
    } catch (error) {
      console.error('Failed to store subscription info:', error);
      throw new Error('Failed to store subscription info');
    }
  }

  /**
   * Get subscription info
   */
  static async getSubscriptionInfo(): Promise<SubscriptionPlan | null> {
    try {
      const subscriptionJson = await AsyncStorage.getItem(STORAGE_KEYS.SUBSCRIPTION_INFO);
      return subscriptionJson ? JSON.parse(subscriptionJson) : null;
    } catch (error) {
      console.error('Failed to get subscription info:', error);
      return null;
    }
  }

  /**
   * Store offline data for sync later
   */
  static async storeOfflineData(data: any): Promise<void> {
    try {
      const existingData = await this.getOfflineData();
      const updatedData = [...existingData, { ...data, timestamp: new Date() }];
      await AsyncStorage.setItem(STORAGE_KEYS.OFFLINE_DATA, JSON.stringify(updatedData));
    } catch (error) {
      console.error('Failed to store offline data:', error);
      throw new Error('Failed to store offline data');
    }
  }

  /**
   * Get offline data
   */
  static async getOfflineData(): Promise<any[]> {
    try {
      const offlineJson = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_DATA);
      return offlineJson ? JSON.parse(offlineJson) : [];
    } catch (error) {
      console.error('Failed to get offline data:', error);
      return [];
    }
  }

  /**
   * Clear offline data (after successful sync)
   */
  static async clearOfflineData(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEYS.OFFLINE_DATA);
    } catch (error) {
      console.error('Failed to clear offline data:', error);
      throw new Error('Failed to clear offline data');
    }
  }

  /**
   * Clear all app data
   */
  static async clearAllData(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([
        STORAGE_KEYS.USER_PROFILE,
        STORAGE_KEYS.LEARNING_PROGRESS,
        STORAGE_KEYS.VOCABULARY_WORDS,
        STORAGE_KEYS.CONVERSATION_HISTORY,
        STORAGE_KEYS.APP_SETTINGS,
        STORAGE_KEYS.SUBSCRIPTION_INFO,
        STORAGE_KEYS.OFFLINE_DATA,
      ]);
    } catch (error) {
      console.error('Failed to clear all data:', error);
      throw new Error('Failed to clear all data');
    }
  }

  /**
   * Get storage usage info
   */
  static async getStorageInfo(): Promise<{ totalSize: number; itemCount: number }> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const appKeys = keys.filter(key => Object.values(STORAGE_KEYS).includes(key));
      
      let totalSize = 0;
      for (const key of appKeys) {
        const value = await AsyncStorage.getItem(key);
        if (value) {
          totalSize += value.length;
        }
      }
      
      return {
        totalSize: totalSize, // in bytes
        itemCount: appKeys.length
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return { totalSize: 0, itemCount: 0 };
    }
  }

  /**
   * Check if user is first time user
   */
  static async isFirstTimeUser(): Promise<boolean> {
    try {
      const user = await this.getUserProfile();
      return user === null;
    } catch (error) {
      console.error('Failed to check first time user:', error);
      return true;
    }
  }

  /**
   * Update user streak
   */
  static async updateUserStreak(): Promise<void> {
    try {
      const progress = await this.getProgress();
      if (!progress) return;

      const today = new Date().toDateString();
      const lastSession = await this.getLastSessionDate();
      
      if (lastSession) {
        const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toDateString();
        
        if (lastSession === yesterday) {
          // Continue streak
          progress.currentStreak += 1;
        } else if (lastSession !== today) {
          // Break streak
          progress.currentStreak = 1;
        }
        // If lastSession === today, keep current streak
      } else {
        // First session
        progress.currentStreak = 1;
      }

      // Update longest streak
      if (progress.currentStreak > progress.longestStreak) {
        progress.longestStreak = progress.currentStreak;
      }

      await this.storeProgress(progress);
      await this.setLastSessionDate(today);
    } catch (error) {
      console.error('Failed to update user streak:', error);
    }
  }

  /**
   * Get last session date
   */
  private static async getLastSessionDate(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('last_session_date');
    } catch (error) {
      console.error('Failed to get last session date:', error);
      return null;
    }
  }

  /**
   * Set last session date
   */
  private static async setLastSessionDate(date: string): Promise<void> {
    try {
      await AsyncStorage.setItem('last_session_date', date);
    } catch (error) {
      console.error('Failed to set last session date:', error);
    }
  }
}
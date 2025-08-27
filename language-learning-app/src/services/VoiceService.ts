import { Audio } from 'expo-av';
import * as Speech from 'expo-speech';
import { Platform } from 'react-native';
import { VoiceRecording, SpeechResult } from '../types';

export class VoiceService {
  private recording: Audio.Recording | null = null;
  private isRecording = false;
  private sound: Audio.Sound | null = null;

  constructor() {
    this.setupAudio();
  }

  /**
   * Setup audio permissions and configuration
   */
  private async setupAudio(): Promise<void> {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        playThroughEarpieceAndroid: false,
        staysActiveInBackground: true,
      });
    } catch (error) {
      console.error('Failed to setup audio:', error);
    }
  }

  /**
   * Start voice recording
   */
  async startRecording(): Promise<void> {
    try {
      if (this.isRecording) {
        throw new Error('Already recording');
      }

      // Request permissions
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        throw new Error('Audio recording permission not granted');
      }

      // Prepare recording
      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
      
      // Start recording
      await recording.startAsync();
      
      this.recording = recording;
      this.isRecording = true;
    } catch (error) {
      console.error('Failed to start recording:', error);
      throw new Error('Failed to start recording');
    }
  }

  /**
   * Stop voice recording
   */
  async stopRecording(): Promise<VoiceRecording> {
    try {
      if (!this.isRecording || !this.recording) {
        throw new Error('No active recording');
      }

      await this.recording.stopAndUnloadAsync();
      const uri = this.recording.getURI();
      
      if (!uri) {
        throw new Error('Failed to get recording URI');
      }

      // Get recording info
      const info = await Audio.getInfoAsync(uri);
      
      const voiceRecording: VoiceRecording = {
        uri,
        duration: info.durationMillis || 0,
        size: info.size || 0,
      };

      this.recording = null;
      this.isRecording = false;

      return voiceRecording;
    } catch (error) {
      console.error('Failed to stop recording:', error);
      throw new Error('Failed to stop recording');
    }
  }

  /**
   * Cancel current recording
   */
  async cancelRecording(): Promise<void> {
    try {
      if (this.recording) {
        await this.recording.stopAndUnloadAsync();
        this.recording = null;
      }
      this.isRecording = false;
    } catch (error) {
      console.error('Failed to cancel recording:', error);
    }
  }

  /**
   * Play audio file
   */
  async playAudio(uri: string): Promise<void> {
    try {
      // Unload previous sound
      if (this.sound) {
        await this.sound.unloadAsync();
      }

      // Load and play new sound
      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true }
      );
      
      this.sound = sound;
      
      // Set up playback status update
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          this.unloadSound();
        }
      });
    } catch (error) {
      console.error('Failed to play audio:', error);
      throw new Error('Failed to play audio');
    }
  }

  /**
   * Stop audio playback
   */
  async stopAudio(): Promise<void> {
    try {
      if (this.sound) {
        await this.sound.stopAsync();
        await this.unloadSound();
      }
    } catch (error) {
      console.error('Failed to stop audio:', error);
    }
  }

  /**
   * Unload current sound
   */
  private async unloadSound(): Promise<void> {
    try {
      if (this.sound) {
        await this.sound.unloadAsync();
        this.sound = null;
      }
    } catch (error) {
      console.error('Failed to unload sound:', error);
    }
  }

  /**
   * Text-to-speech
   */
  async speak(text: string, language: string = 'en-US', rate: number = 1.0): Promise<void> {
    try {
      // Stop any current speech
      await this.stopSpeaking();

      const options: Speech.SpeechOptions = {
        language,
        pitch: 1.0,
        rate,
        voice: undefined, // Use default voice for the language
      };

      await Speech.speak(text, options);
    } catch (error) {
      console.error('Failed to speak text:', error);
      throw new Error('Failed to speak text');
    }
  }

  /**
   * Stop text-to-speech
   */
  async stopSpeaking(): Promise<void> {
    try {
      await Speech.stop();
    } catch (error) {
      console.error('Failed to stop speaking:', error);
    }
  }

  /**
   * Get available voices for a language
   */
  async getAvailableVoices(): Promise<Speech.Voice[]> {
    try {
      return await Speech.getAvailableVoicesAsync();
    } catch (error) {
      console.error('Failed to get available voices:', error);
      return [];
    }
  }

  /**
   * Check if speech synthesis is available
   */
  async isSpeechAvailable(): Promise<boolean> {
    try {
      return await Speech.isSpeakingAsync();
    } catch (error) {
      console.error('Failed to check speech availability:', error);
      return false;
    }
  }

  /**
   * Transcribe audio to text (placeholder for integration with external service)
   */
  async transcribeAudio(audioUri: string, language: string = 'en-US'): Promise<SpeechResult> {
    try {
      // This would integrate with a speech-to-text service
      // For now, we'll return a placeholder
      // In a real implementation, you would send the audio to:
      // - Google Speech-to-Text API
      // - Azure Speech Service
      // - Amazon Transcribe
      // - The Universal AI Platform's speech recognition

      console.log(`Transcribing audio: ${audioUri} in language: ${language}`);
      
      // Placeholder implementation
      const mockResult: SpeechResult = {
        transcript: 'This is a placeholder transcription',
        confidence: 0.95,
        language: language,
      };

      return mockResult;
    } catch (error) {
      console.error('Failed to transcribe audio:', error);
      throw new Error('Failed to transcribe audio');
    }
  }

  /**
   * Get recording status
   */
  getRecordingStatus(): { isRecording: boolean; duration?: number } {
    return {
      isRecording: this.isRecording,
      duration: this.recording ? 0 : undefined, // Would need to track duration manually
    };
  }

  /**
   * Clean up resources
   */
  async cleanup(): Promise<void> {
    try {
      await this.stopSpeaking();
      await this.stopAudio();
      await this.cancelRecording();
    } catch (error) {
      console.error('Failed to cleanup voice service:', error);
    }
  }

  /**
   * Get microphone permission status
   */
  async getMicrophonePermission(): Promise<'granted' | 'denied' | 'undetermined'> {
    try {
      const { status } = await Audio.getPermissionsAsync();
      return status;
    } catch (error) {
      console.error('Failed to get microphone permission:', error);
      return 'undetermined';
    }
  }

  /**
   * Request microphone permission
   */
  async requestMicrophonePermission(): Promise<'granted' | 'denied'> {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      return status;
    } catch (error) {
      console.error('Failed to request microphone permission:', error);
      return 'denied';
    }
  }

  /**
   * Calculate pronunciation score (placeholder implementation)
   */
  calculatePronunciationScore(
    originalText: string, 
    spokenText: string
  ): number {
    // Simple similarity-based scoring
    // In a real implementation, this would use:
    // - Phonetic analysis
    // - Machine learning models
    // - External pronunciation assessment APIs
    
    const similarity = this.calculateTextSimilarity(originalText, spokenText);
    return Math.max(0, Math.min(100, similarity * 100));
  }

  /**
   * Calculate text similarity (basic implementation)
   */
  private calculateTextSimilarity(text1: string, text2: string): number {
    const words1 = text1.toLowerCase().split(' ');
    const words2 = text2.toLowerCase().split(' ');
    
    let matches = 0;
    const maxLength = Math.max(words1.length, words2.length);
    
    for (let i = 0; i < Math.min(words1.length, words2.length); i++) {
      if (words1[i] === words2[i]) {
        matches++;
      }
    }
    
    return matches / maxLength;
  }
}

// Export singleton instance
export const voiceService = new VoiceService();
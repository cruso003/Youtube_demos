"""
Language Learning Demo Application
Demonstrates the Universal AI Agent Platform with a language learning use case
"""

import sys
import time
from pathlib import Path

# Add the SDK path
sys.path.append(str(Path(__file__).parent.parent.parent / "client_sdks" / "python"))

from universal_ai_sdk import UniversalAIClient, AgentConfig, AgentSession

class LanguageLearningApp:
    """Simple language learning demo application"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize the language learning app"""
        self.client = UniversalAIClient(api_url)
        self.session: AgentSession = None
        self.target_language = "Spanish"
        self.proficiency_level = "beginner"
    
    def start_learning_session(self, target_language: str = "Spanish", level: str = "beginner"):
        """Start a new language learning session"""
        self.target_language = target_language
        self.proficiency_level = level
        
        print(f"🎓 Starting {target_language} learning session (Level: {level})")
        
        # Create agent configuration for language learning
        config = AgentConfig(
            instructions=f"""You are a friendly {target_language} language learning assistant. 
            Help the user practice {target_language} at a {level} level. Be encouraging and patient.""",
            capabilities=["text", "voice"],  # Could add "vision" for image-based learning
            business_logic_adapter="languagelearning",
            custom_settings={
                "target_language": target_language,
                "proficiency_level": level,
                "conversation_topics": ["daily activities", "food", "travel", "hobbies"]
            },
            client_id="language_learning_demo"
        )
        
        try:
            result = self.client.create_agent(config)
            session_id = result["session_id"]
            self.session = AgentSession(self.client, session_id)
            
            print(f"✅ Learning session created! Session ID: {session_id}")
            print(f"📚 Agent capabilities: {result.get('capabilities', [])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create learning session: {e}")
            return False
    
    def practice_conversation(self):
        """Interactive conversation practice"""
        if not self.session:
            print("❌ No active learning session. Please start a session first.")
            return
        
        print(f"\n💬 Starting conversation practice in {self.target_language}")
        print("Type 'quit' to end the session, 'help' for commands")
        print("-" * 50)
        
        # Send initial greeting
        self.session.send_message("Hello! I'm ready to practice!")
        
        # Wait for agent's greeting
        greeting = self.session.wait_for_response(timeout=10)
        if greeting:
            print(f"🤖 Assistant: {greeting.content}")
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("\n👋 Ending learning session...")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # Send message to agent
                self.session.send_message(user_input)
                
                # Wait for response
                print("🤖 Assistant is thinking...")
                response = self.session.wait_for_response(timeout=15)
                
                if response:
                    print(f"🤖 Assistant: {response.content}")
                else:
                    print("⏰ No response received. Try again.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Learning session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error during conversation: {e}")
    
    def _show_help(self):
        """Show available commands"""
        print("\n📖 Available commands:")
        print("  - Type any message to practice conversation")
        print("  - 'quit' - End the learning session")
        print("  - 'help' - Show this help message")
        print(f"  - Practice topics: daily activities, food, travel, hobbies")
        print(f"  - Current language: {self.target_language} ({self.proficiency_level} level)")
    
    def get_learning_progress(self):
        """Get learning progress and usage statistics"""
        if not self.session:
            print("❌ No active learning session.")
            return
        
        try:
            # Get session status
            status = self.session.get_status()
            print(f"\n📊 Learning Session Status:")
            print(f"  Session ID: {status.get('session_id', 'N/A')}")
            print(f"  Agent ID: {status.get('agent_id', 'N/A')}")
            print(f"  Status: {status.get('status', 'N/A')}")
            print(f"  Created: {status.get('created_at', 'N/A')}")
            
            # Get usage summary
            usage = self.client.get_usage_summary("language_learning_demo")
            if usage.get("status") == "success":
                usage_data = usage.get("usage", {})
                print(f"\n📈 Learning Progress:")
                print(f"  Sessions completed: {usage_data.get('sessions', 0)}")
                print(f"  Messages exchanged: {usage_data.get('messages', 0)}")
                print(f"  Practice time: {usage_data.get('total_duration_minutes', 0):.1f} minutes")
            
        except Exception as e:
            print(f"❌ Failed to get progress: {e}")
    
    def end_session(self):
        """End the current learning session"""
        if not self.session:
            print("❌ No active session to end.")
            return
        
        try:
            self.session.close()
            print("✅ Learning session ended successfully!")
            self.session = None
        except Exception as e:
            print(f"❌ Error ending session: {e}")

def main():
    """Main function to run the language learning demo"""
    print("🌟 Universal AI Agent Platform - Language Learning Demo")
    print("=" * 60)
    
    app = LanguageLearningApp()
    
    # Main menu
    while True:
        print("\n📚 Language Learning Options:")
        print("1. Start Spanish learning session (Beginner)")
        print("2. Start French learning session (Intermediate)")
        print("3. Custom language session")
        print("4. Practice conversation")
        print("5. View learning progress")
        print("6. End current session")
        print("7. Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == "1":
            app.start_learning_session("Spanish", "beginner")
        elif choice == "2":
            app.start_learning_session("French", "intermediate")
        elif choice == "3":
            language = input("Enter target language: ").strip()
            level = input("Enter proficiency level (beginner/intermediate/advanced): ").strip()
            if language and level:
                app.start_learning_session(language, level)
            else:
                print("❌ Invalid input. Please try again.")
        elif choice == "4":
            app.practice_conversation()
        elif choice == "5":
            app.get_learning_progress()
        elif choice == "6":
            app.end_session()
        elif choice == "7":
            print("\n👋 Thank you for using the Language Learning Demo!")
            app.end_session()
            break
        else:
            print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()
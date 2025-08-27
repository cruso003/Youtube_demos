"""
Emergency Services Demo Application
Demonstrates the Universal AI Agent Platform with an emergency response use case
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add the SDK path
sys.path.append(str(Path(__file__).parent.parent.parent / "client_sdks" / "python"))

from universal_ai_sdk import UniversalAIClient, AgentConfig, AgentSession

class EmergencyServicesApp:
    """Emergency services dispatcher demo application"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize the emergency services app"""
        self.client = UniversalAIClient(api_url)
        self.session: AgentSession = None
        self.emergency_log = []
    
    def start_emergency_session(self):
        """Start a new emergency services session"""
        print("🚨 EMERGENCY SERVICES - Universal AI Platform")
        print("=" * 50)
        print("⚠️  This is a DEMO application for training purposes only")
        print("⚠️  For real emergencies, call your local emergency number!")
        print("=" * 50)
        
        # Create agent configuration for emergency services
        config = AgentConfig(
            instructions="""You are an emergency services AI assistant for DEMO purposes only. 
            Your role is to gather essential information about emergency situations and provide guidance.""",
            capabilities=["text", "voice", "vision"],  # Full multimodal for emergency assessment
            business_logic_adapter="emergencyservices",
            custom_settings={
                "emergency_types": ["medical", "fire", "police", "natural_disaster"],
                "location_required": True,
                "escalation_keywords": ["unconscious", "bleeding", "fire", "break-in", "assault", "chest pain", "breathing"]
            },
            client_id="emergency_services_demo"
        )
        
        try:
            result = self.client.create_agent(config)
            session_id = result["session_id"]
            self.session = AgentSession(self.client, session_id)
            
            print(f"✅ Emergency session created! Session ID: {session_id}")
            print(f"🎯 Agent capabilities: {result.get('capabilities', [])}")
            
            # Log the session start
            self.emergency_log.append({
                "timestamp": datetime.now().isoformat(),
                "event": "session_started",
                "session_id": session_id
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create emergency session: {e}")
            return False
    
    def handle_emergency_call(self):
        """Simulate handling an emergency call"""
        if not self.session:
            print("❌ No active emergency session. Please start a session first.")
            return
        
        print("\n📞 EMERGENCY CALL SIMULATION")
        print("🔴 You are now connected to Emergency Services AI")
        print("Type 'end-call' to end the emergency call")
        print("-" * 50)
        
        # Start the emergency protocol
        self.session.send_message("Emergency services, what is your emergency?")
        
        # Wait for agent's initial response
        initial_response = self.session.wait_for_response(timeout=10)
        if initial_response:
            print(f"🤖 Dispatcher: {initial_response.content}")
        
        call_start_time = datetime.now()
        
        while True:
            try:
                # Get caller input
                caller_input = input("\n📞 Caller: ").strip()
                
                if caller_input.lower() == 'end-call':
                    print("\n📴 Emergency call ended.")
                    break
                elif not caller_input:
                    continue
                
                # Log the caller's message
                self.emergency_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "speaker": "caller",
                    "message": caller_input
                })
                
                # Send message to emergency AI
                self.session.send_message(caller_input)
                
                # Wait for dispatcher response
                print("🤖 Dispatcher is processing...")
                response = self.session.wait_for_response(timeout=15)
                
                if response:
                    print(f"🤖 Dispatcher: {response.content}")
                    
                    # Log the dispatcher's response
                    self.emergency_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "speaker": "dispatcher",
                        "message": response.content
                    })
                    
                    # Check for escalation keywords (simple simulation)
                    if any(keyword in caller_input.lower() for keyword in 
                           ["unconscious", "bleeding", "fire", "chest pain", "breathing"]):
                        print("\n🚨 HIGH PRIORITY ALERT: Escalation keywords detected!")
                        print("📡 Dispatching emergency units immediately...")
                        
                        self.emergency_log.append({
                            "timestamp": datetime.now().isoformat(),
                            "event": "high_priority_escalation",
                            "reason": "escalation_keywords_detected"
                        })
                    
                else:
                    print("⏰ No response from dispatcher. Trying to reconnect...")
                
            except KeyboardInterrupt:
                print("\n\n📴 Emergency call interrupted!")
                break
            except Exception as e:
                print(f"❌ Error during emergency call: {e}")
        
        # Calculate call duration
        call_duration = (datetime.now() - call_start_time).total_seconds()
        print(f"\n📊 Call duration: {call_duration:.1f} seconds")
        
        self.emergency_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "call_ended",
            "duration_seconds": call_duration
        })
    
    def view_emergency_log(self):
        """View the emergency call log"""
        if not self.emergency_log:
            print("📋 No emergency calls logged yet.")
            return
        
        print("\n📋 EMERGENCY CALL LOG")
        print("=" * 50)
        
        for i, entry in enumerate(self.emergency_log, 1):
            timestamp = entry["timestamp"]
            
            if entry.get("event"):
                print(f"{i}. [{timestamp}] EVENT: {entry['event']}")
                if "session_id" in entry:
                    print(f"   Session: {entry['session_id']}")
                if "reason" in entry:
                    print(f"   Reason: {entry['reason']}")
                if "duration_seconds" in entry:
                    print(f"   Duration: {entry['duration_seconds']:.1f}s")
            elif entry.get("speaker"):
                speaker = "📞 CALLER" if entry["speaker"] == "caller" else "🤖 DISPATCHER"
                print(f"{i}. [{timestamp}] {speaker}: {entry['message'][:100]}...")
            
            print()
    
    def get_system_status(self):
        """Get emergency system status and statistics"""
        if not self.session:
            print("❌ No active emergency session.")
            return
        
        try:
            # Get session status
            status = self.session.get_status()
            print(f"\n🚨 Emergency System Status:")
            print(f"  Session ID: {status.get('session_id', 'N/A')}")
            print(f"  Agent ID: {status.get('agent_id', 'N/A')}")
            print(f"  Status: {status.get('status', 'N/A')}")
            print(f"  Session Started: {status.get('created_at', 'N/A')}")
            print(f"  Business Logic: {status.get('business_logic_adapter', 'N/A')}")
            
            # Get usage summary
            usage = self.client.get_usage_summary("emergency_services_demo")
            if usage.get("status") == "success":
                usage_data = usage.get("usage", {})
                print(f"\n📊 System Usage:")
                print(f"  Emergency sessions: {usage_data.get('sessions', 0)}")
                print(f"  Messages processed: {usage_data.get('messages', 0)}")
                print(f"  Images analyzed: {usage_data.get('images', 0)}")
                print(f"  Total response time: {usage_data.get('total_duration_minutes', 0):.1f} minutes")
            
            # Show emergency log summary
            call_events = [e for e in self.emergency_log if e.get("event") == "call_ended"]
            escalations = [e for e in self.emergency_log if e.get("event") == "high_priority_escalation"]
            
            print(f"\n📋 Call Log Summary:")
            print(f"  Calls handled: {len(call_events)}")
            print(f"  High priority escalations: {len(escalations)}")
            print(f"  Log entries: {len(self.emergency_log)}")
            
        except Exception as e:
            print(f"❌ Failed to get system status: {e}")
    
    def end_emergency_session(self):
        """End the current emergency session"""
        if not self.session:
            print("❌ No active emergency session to end.")
            return
        
        try:
            self.session.close()
            print("✅ Emergency session ended successfully!")
            
            self.emergency_log.append({
                "timestamp": datetime.now().isoformat(),
                "event": "session_ended"
            })
            
            self.session = None
        except Exception as e:
            print(f"❌ Error ending emergency session: {e}")

def main():
    """Main function to run the emergency services demo"""
    print("🚨 Universal AI Agent Platform - Emergency Services Demo")
    print("=" * 60)
    print("⚠️  THIS IS A DEMONSTRATION SYSTEM ONLY")
    print("⚠️  FOR REAL EMERGENCIES, CALL YOUR LOCAL EMERGENCY NUMBER!")
    print("=" * 60)
    
    app = EmergencyServicesApp()
    
    # Main menu
    while True:
        print("\n🚨 Emergency Services Options:")
        print("1. Start Emergency Session")
        print("2. Handle Emergency Call (Simulation)")
        print("3. View Emergency Log")
        print("4. System Status")
        print("5. End Emergency Session")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == "1":
            app.start_emergency_session()
        elif choice == "2":
            app.handle_emergency_call()
        elif choice == "3":
            app.view_emergency_log()
        elif choice == "4":
            app.get_system_status()
        elif choice == "5":
            app.end_emergency_session()
        elif choice == "6":
            print("\n👋 Thank you for using the Emergency Services Demo!")
            print("⚠️  Remember: This was a demonstration only!")
            app.end_emergency_session()
            break
        else:
            print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()
"""
Emergency Services Demo Application
Demonstrates the Universal AI Agent Platform with an emergency response use case
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Add the SDK path
sys.path.append(str(Path(__file__).parent.parent.parent / "client_sdks" / "python"))

from universal_ai_sdk import UniversalAIClient, AgentConfig, AgentSession
try:
    from services.phone_service import PhoneService
except ImportError:
    print("⚠️  Phone service not available - call features will be disabled")
    PhoneService = None

class EmergencyServicesApp:
    """Emergency services dispatcher demo application"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize the emergency services app"""
        self.client = UniversalAIClient(api_url)
        self.session: AgentSession = None
        self.emergency_log = []
        
        # Debug: Check if environment variables are loaded
        print(f"🔧 Debug - Twilio SID present: {'Yes' if os.getenv('TWILIO_ACCOUNT_SID') else 'No'}")
        print(f"🔧 Debug - Twilio Token present: {'Yes' if os.getenv('TWILIO_AUTH_TOKEN') else 'No'}")
        print(f"🔧 Debug - Twilio Phone present: {'Yes' if os.getenv('TWILIO_PHONE_NUMBER') else 'No'}")
        
        self.phone_service = PhoneService() if PhoneService else None
        self.emergency_keywords = ["fire", "medical", "police", "urgent", "help", "emergency", "911", "accident", "injured", "bleeding"]
    
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
    
    def assess_emergency_severity(self, message: str) -> str:
        """Assess the severity of an emergency based on keywords"""
        message_lower = message.lower()
        
        # Critical keywords that trigger immediate response
        critical_keywords = ["shooting", "fire", "heart attack", "not breathing", "unconscious", "bleeding heavily", "overdose", "car accident", "explosion"]
        high_keywords = ["injured", "hurt", "chest pain", "difficulty breathing", "assault", "robbery", "domestic violence"]
        medium_keywords = ["suspicious", "theft", "vandalism", "noise complaint", "minor injury"]
        
        for keyword in critical_keywords:
            if keyword in message_lower:
                return "critical"
                
        for keyword in high_keywords:
            if keyword in message_lower:
                return "high"
                
        for keyword in medium_keywords:
            if keyword in message_lower:
                return "medium"
                
        return "low"
    
    async def trigger_emergency_call(self, phone_number: str, severity: str, details: str) -> dict:
        """Trigger an emergency call to dispatch services"""
        try:
            print(f"🚨 TRIGGERING EMERGENCY CALL - Severity: {severity.upper()}")
            print(f"📞 Calling emergency services at: {phone_number}")
            
            if not self.phone_service:
                print("⚠️  Phone service not available - simulating call")
                return {
                    "success": True,
                    "call_sid": f"SIMULATED_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "status": "simulated",
                    "mock": True,
                    "message": "Phone service not configured - call simulation only"
                }
            
            # Create session ID for the call
            call_session_id = f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare adapter configuration for emergency call
            adapter_config = {
                "adapter_name": "emergencyservices",
                "severity": severity,
                "details": details,
                "capabilities": ["voice", "phone"]
            }
            
            # Initiate call using phone service
            call_result = await self.phone_service.initiate_call(
                to_number=phone_number,
                session_id=call_session_id,
                adapter_config=adapter_config
            )
            
            if call_result.get("success"):
                print(f"✅ Emergency call initiated successfully!")
                print(f"📋 Call SID: {call_result.get('call_sid')}")
                print(f"🔗 Session ID: {call_session_id}")
                
                # Log the emergency call
                self.emergency_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "event": "emergency_call_triggered",
                    "severity": severity,
                    "call_sid": call_result.get('call_sid'),
                    "phone_number": phone_number,
                    "details": details
                })
                
                return call_result
            else:
                print(f"❌ Failed to initiate emergency call: {call_result.get('error')}")
                return call_result
                
        except Exception as e:
            error_msg = f"Emergency call failed: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

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
                
                # Assess emergency severity
                severity = self.assess_emergency_severity(caller_input)
                
                # Check if this warrants an emergency call
                if severity in ["critical", "high"]:
                    print(f"\n🚨 SEVERITY LEVEL: {severity.upper()}")
                    trigger_call = input("🔥 This appears to be a serious emergency. Trigger call to dispatch? (y/n): ").strip().lower()
                    
                    if trigger_call == 'y':
                        # Ask for dispatch phone number (in real scenario, this would be automatic)
                        dispatch_number = input("📞 Enter dispatch phone number (or press Enter for demo): ").strip()
                        if not dispatch_number:
                            dispatch_number = "+15551234567"  # Demo number
                        
                        # Trigger emergency call asynchronously
                        print("🚨 Triggering emergency call...")
                        try:
                            call_result = asyncio.run(self.trigger_emergency_call(
                                phone_number=dispatch_number,
                                severity=severity,
                                details=caller_input
                            ))
                            
                            if call_result.get("success"):
                                print(f"✅ Emergency dispatch notified! Call SID: {call_result.get('call_sid')}")
                            else:
                                print(f"❌ Call failed: {call_result.get('error')}")
                        except Exception as e:
                            print(f"❌ Call trigger error: {e}")
                
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
    
    def test_emergency_call_trigger(self):
        """Test the emergency call triggering functionality"""
        print("\n🧪 EMERGENCY CALL TRIGGER TEST")
        print("=" * 50)
        print("This feature demonstrates automatic emergency call triggering")
        print("based on severity assessment of reported incidents.")
        print("-" * 50)
        
        # Test scenarios
        test_scenarios = [
            ("There's a fire in my building!", "critical"),
            ("Someone is having a heart attack!", "critical"),
            ("I've been in a car accident, need help", "high"),
            ("There's a suspicious person outside", "medium"),
            ("My neighbor is playing loud music", "low")
        ]
        
        print("\n📋 Testing severity assessment:")
        for message, expected in test_scenarios:
            severity = self.assess_emergency_severity(message)
            status = "✅" if severity == expected else "❌"
            print(f"{status} \"{message[:40]}...\" → {severity.upper()}")
        
        print("\n🔥 Now testing actual call trigger...")
        print("Enter an emergency scenario to test call triggering:")
        
        user_scenario = input("📝 Emergency scenario: ").strip()
        if not user_scenario:
            print("❌ No scenario provided.")
            return
        
        severity = self.assess_emergency_severity(user_scenario)
        print(f"🎯 Assessed severity: {severity.upper()}")
        
        if severity in ["critical", "high"]:
            print(f"🚨 This {severity} emergency would trigger an automatic call!")
            
            trigger_test = input("📞 Test call trigger? (y/n): ").strip().lower()
            if trigger_test == 'y':
                # Get test phone number
                test_number = input("📞 Enter test phone number (or press Enter for demo): ").strip()
                if not test_number:
                    test_number = "+15551234567"  # Demo number
                
                print("🚨 Triggering test emergency call...")
                try:
                    call_result = asyncio.run(self.trigger_emergency_call(
                        phone_number=test_number,
                        severity=severity,
                        details=user_scenario
                    ))
                    
                    if call_result.get("success"):
                        print(f"✅ Test call successful!")
                        print(f"📋 Call details:")
                        print(f"   - Call SID: {call_result.get('call_sid')}")
                        print(f"   - Status: {call_result.get('status')}")
                        print(f"   - Mock call: {call_result.get('mock', False)}")
                    else:
                        print(f"❌ Test call failed: {call_result.get('error')}")
                        
                except Exception as e:
                    print(f"❌ Test error: {e}")
        else:
            print(f"ℹ️  This {severity} priority incident would NOT trigger an automatic call.")
            print("   Emergency calls are only triggered for 'critical' and 'high' severity incidents.")

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
        print("3. Test Emergency Call Trigger")
        print("4. View Emergency Log")
        print("5. System Status")
        print("6. End Emergency Session")
        print("7. Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == "1":
            app.start_emergency_session()
        elif choice == "2":
            app.handle_emergency_call()
        elif choice == "3":
            app.test_emergency_call_trigger()
        elif choice == "4":
            app.view_emergency_log()
        elif choice == "5":
            app.get_system_status()
        elif choice == "6":
            app.end_emergency_session()
        elif choice == "7":
            print("\n👋 Thank you for using the Emergency Services Demo!")
            print("⚠️  Remember: This was a demonstration only!")
            app.end_emergency_session()
            break
        else:
            print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()
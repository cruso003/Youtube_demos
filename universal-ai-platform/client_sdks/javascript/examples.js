#!/usr/bin/env node

/**
 * NexusAI JavaScript SDK - Example Usage
 * 
 * This example demonstrates how to use the NexusAI SDK for:
 * 1. Language Learning Applications
 * 2. Emergency Services Integration
 * 3. General AI Agent Creation
 */

const { NexusAIClient, AgentSession, createSimpleAgent } = require('./nexusai-sdk.js');

async function languageLearningExample() {
    console.log('\n🎓 Language Learning Example');
    console.log('='.repeat(40));
    
    const client = new NexusAIClient('https://nexus.bits-innovate.com');
    
    try {
        // Create a language learning agent
        const agent = await client.createAgent({
            instructions: "You are a friendly English tutor for African students. Focus on practical conversation skills and pronunciation.",
            capabilities: ["text", "voice"],
            business_logic_adapter: "languagelearning",
            custom_settings: {
                level: "beginner",
                focus: "conversation",
                native_language: "swahili"
            }
        });
        
        console.log('✅ Created Language Learning Agent:', agent.id);
        
        // Start a learning session
        const session = await client.createSession({
            agent_id: agent.id,
            client_id: "mobile-app-student-123"
        });
        
        console.log('✅ Created Learning Session:', session.session_id);
        
        // Student asks for help
        const response = await client.sendMessage(
            session.session_id,
            "Hello! I want to learn how to introduce myself in English for job interviews."
        );
        
        console.log('🤖 Tutor Response:', response.message);
        
        // Get conversation history
        const messages = await client.getMessages(session.session_id, 5);
        console.log('📚 Conversation History:', messages.length, 'messages');
        
    } catch (error) {
        console.error('❌ Language Learning Error:', error.message);
    }
}

async function emergencyServicesExample() {
    console.log('\n🚨 Emergency Services Example');
    console.log('='.repeat(40));
    
    const client = new NexusAIClient('https://nexus.bits-innovate.com');
    
    try {
        // Create emergency services agent
        const agent = await client.createAgent({
            instructions: "You are an emergency response coordinator. Assess situations quickly and provide immediate help while coordinating with local emergency services.",
            capabilities: ["text", "voice"],
            business_logic_adapter: "emergencyservices",
            custom_settings: {
                region: "west-africa",
                languages: ["english", "french"],
                emergency_contacts: {
                    police: "+233-999",
                    ambulance: "+233-777",
                    fire: "+233-888"
                }
            }
        });
        
        console.log('✅ Created Emergency Agent:', agent.id);
        
        // Emergency session
        const session = await client.createSession({
            agent_id: agent.id,
            client_id: "emergency-mobile-app"
        });
        
        console.log('✅ Created Emergency Session:', session.session_id);
        
        // Simulate emergency report
        const response = await client.sendMessage(
            session.session_id,
            "URGENT: Traffic accident on Accra-Tema highway, 2 people injured, need ambulance immediately!"
        );
        
        console.log('🚨 Emergency Response:', response.message);
        
        // This would trigger automatic phone calls to emergency services
        console.log('📞 Automatic emergency calls would be triggered...');
        
    } catch (error) {
        console.error('❌ Emergency Services Error:', error.message);
    }
}

async function businessChatbotExample() {
    console.log('\n💼 Business Chatbot Example');
    console.log('='.repeat(40));
    
    try {
        // Quick setup for business use
        const { client, agent, session } = await createSimpleAgent(
            'https://nexus.bits-innovate.com',
            'You are a customer service agent for an African e-commerce platform. Help customers with orders, payments, and product inquiries.',
            ['text', 'voice']
        );
        
        console.log('✅ Quick Business Agent Setup Complete');
        console.log('   Agent ID:', agent.id);
        console.log('   Session ID:', session.sessionId);
        
        // Customer inquiry
        const response = await session.sendMessage(
            "Hi, I ordered a phone 3 days ago but haven't received tracking information. My order number is AF-123456."
        );
        
        console.log('🤖 Business Bot Response:', response.message);
        
        // Multiple follow-up messages
        const followUp1 = await session.sendMessage(
            "When will it be delivered? I need it urgently for work."
        );
        
        console.log('🤖 Follow-up Response:', followUp1.message);
        
        // Get full conversation
        const history = await session.getHistory(10);
        console.log('💬 Total Conversation Messages:', history.length);
        
        // Clean up
        await session.close();
        console.log('✅ Session closed successfully');
        
    } catch (error) {
        console.error('❌ Business Chatbot Error:', error.message);
    }
}

async function healthCheckExample() {
    console.log('\n🏥 Health Check Example');
    console.log('='.repeat(40));
    
    const client = new NexusAIClient('https://nexus.bits-innovate.com');
    
    try {
        const health = await client.healthCheck();
        console.log('✅ NexusAI Platform Status:', health);
        
        // Check API connectivity
        console.log('🌐 API Endpoint:', client.apiUrl);
        console.log('🔒 Using HTTPS:', client.apiUrl.startsWith('https'));
        
    } catch (error) {
        console.error('❌ Health Check Error:', error.message);
    }
}

// Run all examples
async function runExamples() {
    console.log('🚀 NexusAI JavaScript SDK - Examples');
    console.log('=====================================');
    console.log('🌍 Built for the African Market');
    console.log('🔗 API: https://nexus.bits-innovate.com');
    
    await healthCheckExample();
    await languageLearningExample();
    await emergencyServicesExample();
    await businessChatbotExample();
    
    console.log('\n✨ All examples completed!');
    console.log('📚 Check README.md for more documentation');
    console.log('🤝 Support: hello@bits-innovate.com');
}

// Run examples if this file is executed directly
if (require.main === module) {
    runExamples().catch(console.error);
}

module.exports = {
    languageLearningExample,
    emergencyServicesExample,
    businessChatbotExample,
    healthCheckExample
};

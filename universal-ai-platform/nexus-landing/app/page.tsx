import { ArrowRight, Zap, Globe, Shield, Code, Users, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">NexusAI</span>
          </div>
          <div className="hidden md:flex items-center space-x-6">
            <Link href="https://nexus-docs.bits-innovate.com" className="text-slate-300 hover:text-white transition-colors">Documentation</Link>
            <Link href="/pricing" className="text-slate-300 hover:text-white transition-colors">Pricing</Link>
            <Link href="/login" className="text-slate-300 hover:text-white transition-colors">Login</Link>
            <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <Badge className="mb-4 bg-purple-500/20 text-purple-300 border-purple-500/30">
            🌍 Built for Africa
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            The Universal AI Platform for{" "}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              African Businesses
            </span>
          </h1>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            Deploy intelligent AI agents with voice, vision, and multimodal capabilities. 
            Built specifically for African markets with local language support and optimized for mobile-first experiences.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
              Start Building <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
            <Button size="lg" variant="outline" className="border-slate-300 text-slate-100 bg-slate-800/30 hover:bg-slate-700 hover:text-white hover:border-slate-200">
              View Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Powerful Features for Modern Applications
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto">
            Everything you need to build intelligent AI-powered applications that work seamlessly across Africa
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <MessageSquare className="w-10 h-10 text-purple-400 mb-2" />
              <CardTitle className="text-white">Multimodal AI</CardTitle>
              <CardDescription className="text-slate-300">
                Voice, vision, and text capabilities in one unified platform
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <Globe className="w-10 h-10 text-purple-400 mb-2" />
              <CardTitle className="text-white">African Languages</CardTitle>
              <CardDescription className="text-slate-300">
                Native support for Swahili, Hausa, Yoruba, and other local languages
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <Shield className="w-10 h-10 text-purple-400 mb-2" />
              <CardTitle className="text-white">Enterprise Security</CardTitle>
              <CardDescription className="text-slate-300">
                SSL encryption, secure APIs, and compliance with data protection laws
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <Code className="w-10 h-10 text-purple-400 mb-2" />
              <CardTitle className="text-white">Developer Friendly</CardTitle>
              <CardDescription className="text-slate-300">
                RESTful APIs, SDKs for JavaScript & Python, comprehensive documentation
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <Users className="w-10 h-10 text-purple-400 mb-2" />
              <CardTitle className="text-white">Business Logic Adapters</CardTitle>
              <CardDescription className="text-slate-300">
                Pre-built solutions for education, emergency services, and e-commerce
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <Zap className="w-10 h-10 text-purple-400 mb-2" />
              <CardTitle className="text-white">Mobile Optimized</CardTitle>
              <CardDescription className="text-slate-300">
                Designed for African connectivity conditions and mobile-first usage
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Built for African Use Cases
          </h2>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
            <CardHeader>
              <CardTitle className="text-white text-xl">🎓 Education & Language Learning</CardTitle>
              <CardDescription className="text-slate-300">
                AI tutors that understand local context and can teach in native languages
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
            <CardHeader>
              <CardTitle className="text-white text-xl">🚨 Emergency Services</CardTitle>
              <CardDescription className="text-slate-300">
                Intelligent emergency response systems with local service integration
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
            <CardHeader>
              <CardTitle className="text-white text-xl">🛒 E-commerce & Fintech</CardTitle>
              <CardDescription className="text-slate-300">
                Customer service bots that understand African payment methods and currencies
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
            <CardHeader>
              <CardTitle className="text-white text-xl">🏥 Healthcare</CardTitle>
              <CardDescription className="text-slate-300">
                Medical assistance and health information systems for rural and urban areas
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Build the Future?
          </h2>
          <p className="text-slate-300 text-lg mb-8">
            Join hundreds of African developers and businesses using NexusAI to create intelligent applications
          </p>
          <Button size="lg" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
            Get Started for Free <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-6 h-6 bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <span className="text-white font-semibold">NexusAI</span>
            </div>
            <div className="flex space-x-6 text-slate-400">
              <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
              <Link href="/terms" className="hover:text-white transition-colors">Terms</Link>
              <Link href="/support" className="hover:text-white transition-colors">Support</Link>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-8 pt-8 text-center text-slate-400">
            <p>&copy; 2025 NexusAI. Built for Africa, by Africans.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
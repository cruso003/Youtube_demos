'use client';

import React from 'react';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  AcademicCapIcon, 
  ChatBubbleLeftRightIcon,
  ClockIcon,
  TrophyIcon,
  ShieldCheckIcon,
  BuildingOfficeIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  PlayCircleIcon,
  CameraIcon,
  MicrophoneIcon,
  ComputerDesktopIcon,
  DocumentTextIcon,
  CogIcon,
  BoltIcon
} from '@heroicons/react/24/outline';

export default function Home() {
  const features = [
    {
      icon: ChatBubbleLeftRightIcon,
      title: 'AI Training Coach',
      description: 'Personalized AI-powered coaching with voice practice and real-time feedback',
      color: 'bg-blue-500'
    },
    {
      icon: UserGroupIcon,
      title: 'Multi-Tenant System',
      description: 'Scalable platform supporting multiple companies with isolated data',
      color: 'bg-green-500'
    },
    {
      icon: ChartBarIcon,
      title: 'Advanced Analytics',
      description: 'Comprehensive reporting on employee progress and skill development',
      color: 'bg-purple-500'
    },
    {
      icon: AcademicCapIcon,
      title: 'Training Modules',
      description: 'Pre-built modules for Sales, Customer Service, Leadership, and more',
      color: 'bg-orange-500'
    },
    {
      icon: MicrophoneIcon,
      title: 'Voice Practice',
      description: 'Interactive voice-based training with pronunciation feedback',
      color: 'bg-red-500'
    },
    {
      icon: CameraIcon,
      title: 'Visual Learning',
      description: 'Camera-based demonstrations and visual skill assessments',
      color: 'bg-indigo-500'
    }
  ];

  const trainingModules = [
    {
      title: 'Sales Communication',
      description: 'Master the art of persuasive communication and closing techniques',
      duration: '45 min',
      level: 'Intermediate',
      icon: '💼'
    },
    {
      title: 'Customer Service Excellence',
      description: 'Learn to handle difficult customers and exceed service expectations',
      duration: '30 min',
      level: 'Beginner',
      icon: '🎧'
    },
    {
      title: 'Leadership & Management',
      description: 'Develop essential leadership skills and team management strategies',
      duration: '60 min',
      level: 'Advanced',
      icon: '👥'
    },
    {
      title: 'Technical Skills Assessment',
      description: 'Evaluate and improve technical competencies across departments',
      duration: '40 min',
      level: 'All Levels',
      icon: '⚙️'
    },
    {
      title: 'Compliance & Safety',
      description: 'Ensure workplace safety and regulatory compliance training',
      duration: '25 min',
      level: 'Required',
      icon: '🛡️'
    },
    {
      title: 'Diversity & Inclusion',
      description: 'Build an inclusive workplace culture and unconscious bias awareness',
      duration: '35 min',
      level: 'All Levels',
      icon: '🤝'
    }
  ];

  const stats = [
    { label: 'Companies Using Platform', value: '500+' },
    { label: 'Employees Trained', value: '50,000+' },
    { label: 'Training Hours Delivered', value: '100,000+' },
    { label: 'Average Skill Improvement', value: '85%' }
  ];

  const testimonials = [
    {
      quote: "The AI coaching feature has transformed our sales training. Our team's performance improved by 40% in just 3 months.",
      author: "Sarah Johnson",
      title: "VP of Sales, TechCorp",
      avatar: "👩‍💼"
    },
    {
      quote: "Finally, a training platform that our employees actually enjoy using. The interactive modules keep them engaged.",
      author: "Mike Chen",
      title: "HR Director, GlobalTech",
      avatar: "👨‍💻"
    },
    {
      quote: "The analytics dashboard gives us incredible insights into our team's development needs and progress.",
      author: "Lisa Rodriguez",
      title: "L&D Manager, InnovateCo",
      avatar: "👩‍🎓"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <BuildingOfficeIcon className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">CorpTrain AI</h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900">Features</a>
              <a href="#modules" className="text-gray-600 hover:text-gray-900">Training Modules</a>
              <a href="#demo" className="text-gray-600 hover:text-gray-900">Demo</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900">Pricing</a>
            </nav>
            <div className="flex space-x-4">
              <button className="text-blue-600 hover:text-blue-700 font-medium">
                Sign In
              </button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 font-medium">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Corporate Training
              <span className="block text-blue-200">Powered by AI</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
              Transform your workforce with AI-powered interactive training, voice practice, 
              visual demonstrations, and automated assessments.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                Start Free Trial
              </button>
              <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
                Watch Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Training
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Leverage the Universal AI Agent Platform to deliver cutting-edge training experiences
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                <div className={`${feature.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Training Modules Section */}
      <section id="modules" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Comprehensive Training Modules
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Ready-to-use training modules covering essential business skills
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {trainingModules.map((module, index) => (
              <div key={index} className="bg-gray-50 p-6 rounded-xl hover:bg-gray-100 transition-colors border">
                <div className="text-3xl mb-4">{module.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {module.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {module.description}
                </p>
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span className="flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {module.duration}
                  </span>
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {module.level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Universal AI Integration Section */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powered by Universal AI Platform
            </h2>
            <p className="text-xl text-purple-100 max-w-3xl mx-auto">
              Advanced AI capabilities including voice recognition, computer vision, and natural language processing
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-white/10 w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                <MicrophoneIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Voice Recognition</h3>
              <p className="text-purple-100">Real-time speech analysis and pronunciation feedback</p>
            </div>
            
            <div className="text-center">
              <div className="bg-white/10 w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                <CameraIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Computer Vision</h3>
              <p className="text-purple-100">Visual demonstrations and skill assessments</p>
            </div>
            
            <div className="text-center">
              <div className="bg-white/10 w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                <ChatBubbleLeftRightIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Natural Language</h3>
              <p className="text-purple-100">Intelligent conversations and personalized feedback</p>
            </div>
            
            <div className="text-center">
              <div className="bg-white/10 w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                <ChartBarIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Analytics</h3>
              <p className="text-purple-100">Advanced progress tracking and insights</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              What Our Customers Say
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-sm">
                <p className="text-gray-600 mb-6 italic">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center">
                  <div className="text-2xl mr-3">{testimonial.avatar}</div>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.author}</div>
                    <div className="text-gray-600 text-sm">{testimonial.title}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              See CorpTrain AI in Action
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Experience the future of corporate training with our interactive demo
            </p>
            
            <div className="bg-gray-100 rounded-xl p-8 max-w-4xl mx-auto">
              <div className="aspect-video bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white">
                <div className="text-center">
                  <PlayCircleIcon className="h-16 w-16 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold mb-2">Interactive Demo</h3>
                  <p className="text-blue-100">
                    See how AI-powered training transforms employee development
                  </p>
                </div>
              </div>
              
              <div className="grid md:grid-cols-3 gap-6 mt-8">
                <div className="text-center">
                  <UserGroupIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <h4 className="font-semibold text-gray-900">Admin Dashboard</h4>
                  <p className="text-gray-600 text-sm">Manage employees and track progress</p>
                </div>
                <div className="text-center">
                  <AcademicCapIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <h4 className="font-semibold text-gray-900">Employee Portal</h4>
                  <p className="text-gray-600 text-sm">Interactive training experience</p>
                </div>
                <div className="text-center">
                  <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <h4 className="font-semibold text-gray-900">AI Coach</h4>
                  <p className="text-gray-600 text-sm">Personalized training assistance</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Transform Your Training?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Join hundreds of companies using CorpTrain AI to develop their workforce
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Start Free Trial
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
              Contact Sales
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <BuildingOfficeIcon className="h-8 w-8 text-blue-400 mr-3" />
                <h3 className="text-xl font-bold">CorpTrain AI</h3>
              </div>
              <p className="text-gray-400">
                AI-powered corporate training platform built on the Universal AI Agent Platform.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Training Modules</a></li>
                <li><a href="#" className="hover:text-white">Analytics</a></li>
                <li><a href="#" className="hover:text-white">Integrations</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
                <li><a href="#" className="hover:text-white">Support</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">Security</a></li>
                <li><a href="#" className="hover:text-white">Compliance</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 CorpTrain AI. All rights reserved. Powered by Universal AI Agent Platform.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

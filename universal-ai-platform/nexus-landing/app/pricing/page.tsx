import { Check, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

export default function PricingPage() {
  const packages = [
    {
      name: "Starter Pack",
      credits: 1000,
      price: 1,
      originalPrice: null,
      popular: false,
      description: "Perfect for testing and small projects",
      features: [
        "1,000 API calls",
        "Text messaging",
        "Basic voice support",
        "Email support",
        "30-day validity"
      ]
    },
    {
      name: "Developer Pack",
      credits: 10000,
      price: 9,
      originalPrice: 10,
      popular: true,
      description: "Great for active development and medium projects",
      features: [
        "10,000 API calls",
        "Full multimodal support",
        "Voice & vision processing",
        "Priority support",
        "90-day validity",
        "10% bonus credits"
      ]
    },
    {
      name: "Business Pack",
      credits: 100000,
      price: 80,
      originalPrice: 100,
      popular: false,
      description: "For production applications and high volume",
      features: [
        "100,000 API calls",
        "All premium features",
        "Custom business logic adapters",
        "24/7 phone support",
        "180-day validity",
        "20% bonus credits",
        "Dedicated account manager"
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">NexusAI</span>
          </Link>
          <div className="hidden md:flex items-center space-x-6">
            <Link href="https://nexusai-docs-5vsitmy23-cruso003s-projects.vercel.app" className="text-slate-300 hover:text-white transition-colors">Documentation</Link>
            <Link href="/pricing" className="text-white font-medium">Pricing</Link>
            <Link href="/login" className="text-slate-300 hover:text-white transition-colors">Login</Link>
            <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            Pay only for what you use. No monthly commitments, no hidden fees. 
            Perfect for the African market with affordable credit packages.
          </p>
          <Badge className="bg-green-500/20 text-green-300 border-green-500/30 text-lg px-4 py-2">
            💡 Start with 100 FREE credits - No credit card required
          </Badge>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
          {packages.map((pkg, index) => (
            <Card key={index} className={`relative bg-slate-800/50 border-slate-700 ${pkg.popular ? 'ring-2 ring-purple-500 scale-105' : ''}`}>
              {pkg.popular && (
                <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                  Most Popular
                </Badge>
              )}
              <CardHeader className="text-center">
                <CardTitle className="text-white text-2xl">{pkg.name}</CardTitle>
                <CardDescription className="text-slate-300">{pkg.description}</CardDescription>
                <div className="mt-4">
                  <div className="flex items-center justify-center space-x-2">
                    {pkg.originalPrice && (
                      <span className="text-slate-400 line-through text-lg">${pkg.originalPrice}</span>
                    )}
                    <span className="text-4xl font-bold text-white">${pkg.price}</span>
                  </div>
                  <p className="text-slate-300 mt-2">
                    {pkg.credits.toLocaleString()} Credits
                  </p>
                  <p className="text-sm text-slate-400">
                    ≈ ${(pkg.price / pkg.credits * 1000).toFixed(3)} per 1K calls
                  </p>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {pkg.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center space-x-3">
                      <Check className="w-5 h-5 text-green-400 flex-shrink-0" />
                      <span className="text-slate-300">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  className={`w-full mt-6 ${
                    pkg.popular 
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600' 
                      : 'bg-slate-700 hover:bg-slate-600 text-white'
                  }`}
                >
                  Buy {pkg.name}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* How Credits Work */}
        <div className="bg-slate-800/30 rounded-2xl p-8 mb-16">
          <h2 className="text-2xl font-bold text-white text-center mb-8">How Credits Work</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-400 font-bold text-xl">1</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Simple Usage</h3>
              <p className="text-slate-300 text-sm">
                1 credit = 1 API call. Text messages, voice processing, image analysis - all clearly priced.
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-400 font-bold text-xl">2</span>
              </div>
              <h3 className="font-semibold text-white mb-2">No Expiry Pressure</h3>
              <p className="text-slate-300 text-sm">
                Credits have generous validity periods. Use them at your own pace without waste.
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-400 font-bold text-xl">3</span>
              </div>
              <h3 className="font-semibold text-white mb-2">African-Friendly</h3>
              <p className="text-slate-300 text-sm">
                Affordable packages designed for African market conditions and mobile money integration.
              </p>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-8">Frequently Asked Questions</h2>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto text-left">
            <div className="bg-slate-800/30 p-6 rounded-lg">
              <h3 className="font-semibold text-white mb-2">Do credits expire?</h3>
              <p className="text-slate-300 text-sm">
                Credits have validity periods (30-180 days) but no monthly commitments. Use them when you need them.
              </p>
            </div>
            <div className="bg-slate-800/30 p-6 rounded-lg">
              <h3 className="font-semibold text-white mb-2">Can I get a refund?</h3>
              <p className="text-slate-300 text-sm">
                Yes! Unused credits can be refunded within 30 days of purchase. We want you to be happy.
              </p>
            </div>
            <div className="bg-slate-800/30 p-6 rounded-lg">
              <h3 className="font-semibold text-white mb-2">What payment methods do you accept?</h3>
              <p className="text-slate-300 text-sm">
                Credit/debit cards, PayPal, and popular African mobile money services like M-Pesa.
              </p>
            </div>
            <div className="bg-slate-800/30 p-6 rounded-lg">
              <h3 className="font-semibold text-white mb-2">Is there a free tier?</h3>
              <p className="text-slate-300 text-sm">
                Yes! Every new account gets 100 free credits to test our platform. No credit card required.
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-16">
          <h2 className="text-2xl font-bold text-white mb-4">Ready to Get Started?</h2>
          <p className="text-slate-300 mb-6">Join thousands of African developers building with NexusAI</p>
          <Button size="lg" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
            Start with 100 Free Credits
          </Button>
        </div>
      </div>
    </div>
  )
}

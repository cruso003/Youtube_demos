"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { CreditCard, Smartphone, Zap, Star, Check } from "lucide-react"
import { toast } from "sonner"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface CreditPackage {
  id: string
  name: string
  credits: number
  price: number
  currency: string
  description: string
  popular?: boolean
  bonus?: string
}

const CREDIT_PACKAGES: CreditPackage[] = [
  {
    id: "starter",
    name: "Starter",
    credits: 1000,
    price: 1.00,
    currency: "USD",
    description: "Perfect for testing and small projects",
  },
  {
    id: "standard",
    name: "Standard",
    credits: 10000,
    price: 9.00,
    currency: "USD",
    description: "Most popular for growing businesses",
    popular: true,
    bonus: "10% Bonus Credits"
  },
  {
    id: "premium",
    name: "Premium",
    credits: 100000,
    price: 80.00,
    currency: "USD",
    description: "For high-volume enterprise usage",
    bonus: "20% Bonus Credits"
  }
]

interface MobileMoney {
  id: string
  name: string
  icon: string
  description: string
}

const MOBILE_MONEY_PROVIDERS: MobileMoney[] = [
  {
    id: "mtn_momo",
    name: "MTN Mobile Money",
    icon: "📱",
    description: "Pay with MTN Mobile Money Liberia"
  }
]

export function CreditPurchase() {
  const [selectedPackage, setSelectedPackage] = useState<CreditPackage | null>(null)
  const [selectedProvider, setSelectedProvider] = useState<MobileMoney | null>(null)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [loading, setLoading] = useState(false)
  const [showPaymentDialog, setShowPaymentDialog] = useState(false)

  const handlePackageSelect = (pkg: CreditPackage) => {
    setSelectedPackage(pkg)
    setSelectedProvider(MOBILE_MONEY_PROVIDERS[0]) // Default to MTN
    setShowPaymentDialog(true)
  }

  const handlePayment = async () => {
    if (!selectedPackage || !selectedProvider || !phoneNumber) {
      toast.error("Please fill in all required fields")
      return
    }

    if (phoneNumber.length < 8) {
      toast.error("Please enter a valid phone number")
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/billing/credits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          package: selectedPackage.id,
          phone_number: phoneNumber,
          payment_method: selectedProvider.id,
        }),
      })

      const result = await response.json()

      if (response.ok && result.success) {
        toast.success("Payment initiated! Please complete the payment on your mobile device.")
        setShowPaymentDialog(false)
        setPhoneNumber("")
        // You might want to redirect to a payment status page
      } else {
        toast.error(result.error || "Payment failed. Please try again.")
      }
    } catch (error) {
      toast.error("Payment failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Purchase Credits</h1>
        <p className="text-gray-600 mt-2">Choose a credit package to power your AI applications</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {CREDIT_PACKAGES.map((pkg) => (
          <Card 
            key={pkg.id} 
            className={`relative cursor-pointer transition-all hover:shadow-lg ${
              pkg.popular ? 'ring-2 ring-blue-500 shadow-lg' : ''
            }`}
            onClick={() => handlePackageSelect(pkg)}
          >
            {pkg.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-blue-500 text-white">
                  <Star className="h-3 w-3 mr-1" />
                  Most Popular
                </Badge>
              </div>
            )}
            
            <CardHeader className="text-center">
              <CardTitle className="text-xl">{pkg.name}</CardTitle>
              <div className="text-3xl font-bold text-blue-600">
                ${pkg.price}
                <span className="text-sm text-gray-500 font-normal">USD</span>
              </div>
              <CardDescription>{pkg.description}</CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="text-center">
                <div className="text-2xl font-semibold">
                  {pkg.credits.toLocaleString()}
                  <span className="text-sm text-gray-500 ml-1">credits</span>
                </div>
                {pkg.bonus && (
                  <div className="text-green-600 text-sm font-medium mt-1">
                    + {pkg.bonus}
                  </div>
                )}
              </div>
              
              <Separator />
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span>AI API Access</span>
                </div>
                <div className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span>Real-time Processing</span>
                </div>
                <div className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span>24/7 Support</span>
                </div>
              </div>
              
              <Button className="w-full" size="lg">
                <CreditCard className="h-4 w-4 mr-2" />
                Purchase Credits
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Complete Payment</DialogTitle>
            <DialogDescription>
              Pay with Mobile Money to purchase {selectedPackage?.credits.toLocaleString()} credits
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {selectedPackage && (
              <Card>
                <CardContent className="pt-6">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium">{selectedPackage.name} Package</h4>
                      <p className="text-sm text-gray-600">{selectedPackage.credits.toLocaleString()} credits</p>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-lg">${selectedPackage.price}</div>
                      <div className="text-sm text-gray-500">USD</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="space-y-3">
              <Label>Payment Method</Label>
              {MOBILE_MONEY_PROVIDERS.map((provider) => (
                <Card 
                  key={provider.id}
                  className={`cursor-pointer border-2 ${
                    selectedProvider?.id === provider.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200'
                  }`}
                  onClick={() => setSelectedProvider(provider)}
                >
                  <CardContent className="flex items-center p-4">
                    <div className="text-2xl mr-3">{provider.icon}</div>
                    <div>
                      <h4 className="font-medium">{provider.name}</h4>
                      <p className="text-sm text-gray-600">{provider.description}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <div className="relative">
                <Smartphone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="phone"
                  type="tel"
                  placeholder="Enter your phone number"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="pl-10"
                />
              </div>
              <p className="text-xs text-gray-500">
                You'll receive a payment prompt on this number
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowPaymentDialog(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button 
              onClick={handlePayment} 
              disabled={loading || !phoneNumber || !selectedProvider}
            >
              {loading ? (
                <>
                  <Zap className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Smartphone className="h-4 w-4 mr-2" />
                  Pay ${selectedPackage?.price}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

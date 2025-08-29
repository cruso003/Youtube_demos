"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { toast } from "sonner"
import { CreditCard, Smartphone, Loader2 } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  packageInfo: {
    id: string
    name: string
    credits: number
    price: number
  }
}

export function PaymentModal({ isOpen, onClose, packageInfo }: PaymentModalProps) {
  const [phoneNumber, setPhoneNumber] = useState("")
  const [provider, setProvider] = useState("MPESA")
  const [processing, setProcessing] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState<"idle" | "pending" | "success" | "failed">("idle")

  const handlePayment = async () => {
    if (!phoneNumber.trim()) {
      toast.error("Please enter your phone number")
      return
    }

    // Validate phone number format
    const phoneRegex = /^(\+254|0)[0-9]{9}$/
    if (!phoneRegex.test(phoneNumber)) {
      toast.error("Please enter a valid Kenyan phone number (e.g., 0712345678)")
      return
    }

    setProcessing(true)
    try {
      const response = await fetch('/api/payments/purchase', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          packageId: packageInfo.id,
          phoneNumber,
          provider,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setPaymentStatus("pending")
        toast.success(data.message)
        
        // Poll for payment status
        pollPaymentStatus(data.transactionId)
      } else {
        toast.error(data.error || "Payment failed")
        setPaymentStatus("failed")
      }
    } catch (error) {
      toast.error("Payment failed. Please try again.")
      setPaymentStatus("failed")
    } finally {
      setProcessing(false)
    }
  }

  const pollPaymentStatus = async (transactionId: string) => {
    const maxAttempts = 30 // Poll for 5 minutes (30 * 10 seconds)
    let attempts = 0

    const poll = async () => {
      try {
        const response = await fetch(`/api/payments/status/${transactionId}`)
        const data = await response.json()

        if (data.status === "COMPLETED") {
          setPaymentStatus("success")
          toast.success("Payment successful! Credits have been added to your account.")
          // Refresh the page to update credits
          window.location.reload()
          return
        } else if (data.status === "FAILED" || data.status === "CANCELLED") {
          setPaymentStatus("failed")
          toast.error("Payment failed or was cancelled")
          return
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000) // Poll every 10 seconds
        } else {
          setPaymentStatus("failed")
          toast.error("Payment timeout. Please check your transaction and contact support if needed.")
        }
      } catch (error) {
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 10000)
        } else {
          setPaymentStatus("failed")
          toast.error("Unable to verify payment status")
        }
      }
    }

    poll()
  }

  const resetModal = () => {
    setPhoneNumber("")
    setProvider("MPESA")
    setProcessing(false)
    setPaymentStatus("idle")
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={resetModal}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Smartphone className="h-5 w-5 mr-2" />
            Purchase {packageInfo.name}
          </DialogTitle>
          <DialogDescription>
            {packageInfo.credits.toLocaleString()} credits for KES {packageInfo.price}
          </DialogDescription>
        </DialogHeader>

        {paymentStatus === "idle" && (
          <>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  placeholder="0712345678 or +254712345678"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  disabled={processing}
                />
              </div>

              <div className="space-y-3">
                <Label>Payment Method</Label>
                <RadioGroup value={provider} onValueChange={setProvider} disabled={processing}>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="MPESA" id="mpesa" />
                    <Label htmlFor="mpesa" className="flex items-center">
                      <div className="w-6 h-6 bg-green-600 rounded mr-2 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">M</span>
                      </div>
                      M-Pesa
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="AIRTEL_MONEY" id="airtel" />
                    <Label htmlFor="airtel" className="flex items-center">
                      <div className="w-6 h-6 bg-red-600 rounded mr-2 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">A</span>
                      </div>
                      Airtel Money
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="T_KASH" id="tkash" />
                    <Label htmlFor="tkash" className="flex items-center">
                      <div className="w-6 h-6 bg-blue-600 rounded mr-2 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">T</span>
                      </div>
                      T-Kash
                    </Label>
                  </div>
                </RadioGroup>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={resetModal} disabled={processing}>
                Cancel
              </Button>
              <Button onClick={handlePayment} disabled={processing}>
                {processing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  `Pay KES ${packageInfo.price}`
                )}
              </Button>
            </DialogFooter>
          </>
        )}

        {paymentStatus === "pending" && (
          <div className="text-center py-8">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <h3 className="font-medium mb-2">Payment in Progress</h3>
            <p className="text-sm text-gray-600">
              Please complete the payment on your phone. This may take a few minutes.
            </p>
          </div>
        )}

        {paymentStatus === "success" && (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="font-medium mb-2">Payment Successful!</h3>
            <p className="text-sm text-gray-600">
              {packageInfo.credits.toLocaleString()} credits have been added to your account.
            </p>
          </div>
        )}

        {paymentStatus === "failed" && (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h3 className="font-medium mb-2">Payment Failed</h3>
            <p className="text-sm text-gray-600 mb-4">
              The payment could not be completed. Please try again.
            </p>
            <Button onClick={() => setPaymentStatus("idle")}>
              Try Again
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/prisma"
import { z } from "zod"

const purchaseCreditsSchema = z.object({
  package: z.enum(["starter", "standard", "premium"]),
  phone_number: z.string().min(8, "Valid phone number required"),
  payment_method: z.enum(["mtn_momo"]),
})

// Credit packages that match the Python MTN payment system
const CREDIT_PACKAGES = {
  starter: {
    credits: 1000,
    price: 1.00,
    currency: "USD",
    description: "1,000 NexusAI Credits"
  },
  standard: {
    credits: 10000,
    price: 9.00,
    currency: "USD",
    description: "10,000 NexusAI Credits (10% Bonus)"
  },
  premium: {
    credits: 100000,
    price: 80.00,
    currency: "USD",
    description: "100,000 NexusAI Credits (20% Bonus)"
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { package: packageType, phone_number, payment_method } = purchaseCreditsSchema.parse(body)

    const creditPackage = CREDIT_PACKAGES[packageType]
    const transactionId = `tx_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`

    // Create pending transaction record
    const transaction = await prisma.transaction.create({
      data: {
        id: transactionId,
        userId: session.user.id,
        type: "CREDIT_PURCHASE",
        amount: creditPackage.price,
        currency: creditPackage.currency,
        status: "PENDING",
        credits: creditPackage.credits,
        paymentMethod: payment_method.toUpperCase(),
        phoneNumber: phone_number,
        description: creditPackage.description,
        metadata: {
          package: packageType,
          phone_number
        }
      }
    })

    // Call MTN Mobile Money API
    const mtnResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/payment/mtn`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        amount: creditPackage.price,
        currency: creditPackage.currency,
        phone_number: phone_number,
        reference_id: transactionId,
        description: creditPackage.description,
        user_id: session.user.id
      }),
    })

    if (!mtnResponse.ok) {
      // Update transaction status to failed
      await prisma.transaction.update({
        where: { id: transactionId },
        data: { 
          status: "FAILED",
          errorMessage: "Payment service unavailable"
        }
      })
      return NextResponse.json({ error: "Payment service unavailable" }, { status: 500 })
    }

    const paymentResult = await mtnResponse.json()

    if (paymentResult.success) {
      // Update transaction with MTN transaction ID
      await prisma.transaction.update({
        where: { id: transactionId },
        data: { 
          externalTransactionId: paymentResult.transaction_id,
          status: "PROCESSING"
        }
      })

      return NextResponse.json({
        success: true,
        transaction_id: transactionId,
        mtn_transaction_id: paymentResult.transaction_id,
        status: "processing",
        message: "Payment initiated. Please complete the payment on your mobile device."
      })
    } else {
      // Update transaction status to failed
      await prisma.transaction.update({
        where: { id: transactionId },
        data: { 
          status: "FAILED",
          errorMessage: paymentResult.message
        }
      })

      return NextResponse.json({
        success: false,
        error: paymentResult.message
      }, { status: 400 })
    }

  } catch (error) {
    console.error("Error processing credit purchase:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 })
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const transactionId = searchParams.get('transaction_id')

    if (transactionId) {
      // Get specific transaction status
      const transaction = await prisma.transaction.findFirst({
        where: {
          id: transactionId,
          userId: session.user.id
        }
      })

      if (!transaction) {
        return NextResponse.json({ error: "Transaction not found" }, { status: 404 })
      }

      return NextResponse.json(transaction)
    } else {
      // Get user's transaction history
      const transactions = await prisma.transaction.findMany({
        where: {
          userId: session.user.id
        },
        orderBy: {
          createdAt: 'desc'
        },
        take: 50
      })

      return NextResponse.json(transactions)
    }

  } catch (error) {
    console.error("Error fetching transactions:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

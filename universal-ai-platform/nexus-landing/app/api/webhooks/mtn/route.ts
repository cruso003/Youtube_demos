import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/prisma"
import { z } from "zod"

const webhookSchema = z.object({
  transaction_id: z.string(),
  reference_id: z.string(),
  status: z.enum(["completed", "failed", "cancelled"]),
  amount: z.number(),
  currency: z.string(),
  message: z.string().optional(),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { transaction_id, reference_id, status, amount, currency, message } = webhookSchema.parse(body)

    // Find the transaction in our database
    const transaction = await prisma.transaction.findUnique({
      where: { id: reference_id },
      include: { user: true }
    })

    if (!transaction) {
      console.error(`Transaction not found: ${reference_id}`)
      return NextResponse.json({ error: "Transaction not found" }, { status: 404 })
    }

    if (status === "completed") {
      // Payment successful - add credits to user account
      await prisma.$transaction(async (tx) => {
        // Update transaction status
        await tx.transaction.update({
          where: { id: reference_id },
          data: {
            status: "COMPLETED",
            externalTransactionId: transaction_id,
            completedAt: new Date()
          }
        })

        // Add credits to user account
        await tx.user.update({
          where: { id: transaction.userId },
          data: {
            credits: {
              increment: transaction.credits || 0
            }
          }
        })

        // Log the credit addition for auditing
        console.log(`Added ${transaction.credits} credits to user ${transaction.userId} for transaction ${reference_id}`)
      })

      return NextResponse.json({ 
        success: true, 
        message: "Credits added successfully" 
      })

    } else if (status === "failed" || status === "cancelled") {
      // Payment failed - update transaction status
      await prisma.transaction.update({
        where: { id: reference_id },
        data: {
          status: status === "failed" ? "FAILED" : "CANCELLED",
          externalTransactionId: transaction_id,
          errorMessage: message
        }
      })

      return NextResponse.json({ 
        success: true, 
        message: "Transaction status updated" 
      })
    }

    return NextResponse.json({ error: "Invalid status" }, { status: 400 })

  } catch (error) {
    console.error("Webhook processing error:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 })
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

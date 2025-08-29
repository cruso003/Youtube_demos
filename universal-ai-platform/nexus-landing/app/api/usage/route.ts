import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/prisma"
import { z } from "zod"

const usageSchema = z.object({
  api_key: z.string(),
  endpoint: z.string(),
  tokens_used: z.number(),
  requests_count: z.number().default(1),
  model: z.string().optional(),
  cost: z.number().optional(),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { api_key, endpoint, tokens_used, requests_count, model, cost } = usageSchema.parse(body)

    // Verify API key and get user
    const apiKeyRecord = await prisma.apiKey.findUnique({
      where: { key: api_key },
      include: { user: true }
    })

    if (!apiKeyRecord || !apiKeyRecord.isActive) {
      return NextResponse.json({ error: "Invalid or inactive API key" }, { status: 401 })
    }

    const user = apiKeyRecord.user

    // Check if user has sufficient credits
    const creditsNeeded = Math.ceil(tokens_used / 1000) // 1 credit per 1000 tokens
    
    if (user.credits < creditsNeeded) {
      return NextResponse.json({ 
        error: "Insufficient credits",
        credits_available: user.credits,
        credits_needed: creditsNeeded
      }, { status: 402 }) // Payment Required
    }

    // Record usage and deduct credits
    await prisma.$transaction(async (tx) => {
      // Deduct credits from user
      await tx.user.update({
        where: { id: user.id },
        data: {
          credits: {
            decrement: creditsNeeded
          }
        }
      })

      // Record usage
      await tx.usage.create({
        data: {
          userId: user.id,
          type: `${endpoint}_${model || 'default'}`,
          amount: tokens_used,
          cost: cost || (creditsNeeded * 0.001),
          metadata: {
            endpoint,
            model,
            requests_count,
            api_key_id: apiKeyRecord.id
          }
        }
      })

      // Update API key last used
      await tx.apiKey.update({
        where: { id: apiKeyRecord.id },
        data: { lastUsed: new Date() }
      })
    })

    return NextResponse.json({
      success: true,
      credits_used: creditsNeeded,
      credits_remaining: user.credits - creditsNeeded,
      message: "Usage recorded successfully"
    })

  } catch (error) {
    console.error("Error recording usage:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.issues }, { status: 400 })
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

// Get usage statistics
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const api_key = searchParams.get('api_key')
    const days = parseInt(searchParams.get('days') || '30')

    if (!api_key) {
      return NextResponse.json({ error: "API key required" }, { status: 400 })
    }

    // Verify API key
    const apiKeyRecord = await prisma.apiKey.findUnique({
      where: { key: api_key },
      include: { user: true }
    })

    if (!apiKeyRecord) {
      return NextResponse.json({ error: "Invalid API key" }, { status: 401 })
    }

    // Get usage data for the specified period
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - days)

    const usage = await prisma.usage.findMany({
      where: {
        userId: apiKeyRecord.userId,
        createdAt: {
          gte: startDate
        }
      },
      orderBy: {
        createdAt: 'desc'
      }
    })

    const totalUsage = usage.reduce(
      (acc, curr) => ({
        requests: acc.requests + 1, // Each usage record represents a request
        tokens: acc.tokens + curr.amount,
        cost: acc.cost + curr.cost
      }),
      { requests: 0, tokens: 0, cost: 0 }
    )

    return NextResponse.json({
      usage,
      total: totalUsage,
      current_credits: apiKeyRecord.user.credits,
      period_days: days
    })

  } catch (error) {
    console.error("Error fetching usage:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

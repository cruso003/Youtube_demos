import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"
import { redirect } from "next/navigation"
import { prisma } from "@/lib/prisma"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Key, BarChart3, Users, DollarSign } from "lucide-react"

export default async function DashboardPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect("/login")
  }

  // Get user's API keys count
  const apiKeysCount = await prisma.apiKey.count({
    where: { userId: session.user.id }
  })

  // Get user's usage data
  const usage = await prisma.usage.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: 'desc' },
    take: 5
  })

  const totalRequests = usage.reduce((sum, u) => sum + u.amount, 0)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {session.user.name || session.user.email}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Keys</CardTitle>
            <Key className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{apiKeysCount}</div>
            <p className="text-xs text-muted-foreground">
              Active API keys
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalRequests}</div>
            <p className="text-xs text-muted-foreground">
              API requests this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Account Status</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <Badge variant={session.user.role === 'USER' ? 'secondary' : 'default'}>
                {session.user.role}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Current role
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Usage Limit</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">∞</div>
            <p className="text-xs text-muted-foreground">
              No limits during beta
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Your latest API usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            {usage.length > 0 ? (
              <div className="space-y-4">
                {usage.map((u) => (
                  <div key={u.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">{(u.metadata as any)?.endpoint ?? "Unknown endpoint"}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(u.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{u.amount} requests</p>
                      <p className="text-xs text-muted-foreground">
                        ${(u.cost / 100).toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No API usage yet. Get started by creating an API key!
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <a
              href="/dashboard/api-keys"
              className="block w-full text-left p-2 hover:bg-gray-50 rounded border"
            >
              <p className="font-medium">Create API Key</p>
              <p className="text-xs text-muted-foreground">Generate a new API key</p>
            </a>
            <a
              href="/dashboard/usage"
              className="block w-full text-left p-2 hover:bg-gray-50 rounded border"
            >
              <p className="font-medium">View Usage</p>
              <p className="text-xs text-muted-foreground">Check your API usage</p>
            </a>
            <a
              href="/docs/api"
              className="block w-full text-left p-2 hover:bg-gray-50 rounded border"
            >
              <p className="font-medium">API Documentation</p>
              <p className="text-xs text-muted-foreground">Learn how to integrate</p>
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

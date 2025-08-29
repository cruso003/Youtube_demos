import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"
import { redirect } from "next/navigation"
import { CreditPurchase } from "@/components/billing/credit-purchase"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CreditCard, DollarSign, Calendar, TrendingUp } from "lucide-react"
import { prisma } from "@/lib/prisma"

export default async function BillingPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect("/login")
  }

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    include: {
      transactions: {
        orderBy: { createdAt: 'desc' },
        take: 5
      }
    }
  })

  const totalSpent = user?.transactions
    .filter(t => t.status === 'COMPLETED')
    .reduce((sum, t) => sum + t.amount, 0) || 0

  return (
    <div className="space-y-8">
      {/* Current Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Credits</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {user?.credits?.toLocaleString() || 0}
            </div>
            <p className="text-xs text-muted-foreground">Ready to use</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Plan</CardTitle>
            <Badge variant="outline" className="text-xs">
              {user?.plan || 'Free'}
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-medium">
              {user?.plan || 'Free Tier'}
            </div>
            <p className="text-xs text-muted-foreground">Active plan</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${totalSpent.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transactions</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {user?.transactions?.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">Total purchases</p>
          </CardContent>
        </Card>
      </div>

      {/* Credit Purchase Section */}
      <CreditPurchase />

      {/* Recent Transactions */}
      {user?.transactions && user.transactions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>Your latest credit purchases and payments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {user.transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center py-3 border-b">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                    <div>
                      <p className="font-medium">{transaction.description || 'Credit Purchase'}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(transaction.createdAt).toLocaleDateString()} • {transaction.paymentMethod}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">${transaction.amount.toFixed(2)}</div>
                    <Badge 
                      variant={
                        transaction.status === 'COMPLETED' ? 'default' :
                        transaction.status === 'FAILED' ? 'destructive' :
                        'secondary'
                      }
                      className="text-xs"
                    >
                      {transaction.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

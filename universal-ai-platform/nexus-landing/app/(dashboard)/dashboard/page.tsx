"use client"

import { useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Zap, 
  CreditCard, 
  Key, 
  Activity, 
  Users, 
  MessageSquare, 
  TrendingUp,
  Settings,
  LogOut,
  Copy,
  Plus
} from "lucide-react"

export default function DashboardPage() {
  const [user] = useState({
    name: "John Doe",
    email: "john@company.com",
    credits: 847,
    plan: "Developer"
  })

  const [stats] = useState({
    totalCalls: 1247,
    thisMonth: 324,
    activeSessions: 12,
    successRate: 98.5
  })

  const [apiKeys] = useState([
    { id: "1", name: "Production API", key: "nx_prod_***********", created: "2025-01-15", lastUsed: "2 hours ago" },
    { id: "2", name: "Development API", key: "nx_dev_***********", created: "2025-01-10", lastUsed: "5 minutes ago" }
  ])

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
          <div className="flex items-center space-x-4">
            <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
              {user.credits} Credits
            </Badge>
            <Button size="sm" className="bg-gradient-to-r from-purple-500 to-pink-500">
              <Plus className="w-4 h-4 mr-2" />
              Buy Credits
            </Button>
            <Button variant="ghost" size="sm" className="text-slate-300">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button variant="ghost" size="sm" className="text-slate-300">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome back, {user.name}!</h1>
          <p className="text-slate-300">Here's what's happening with your NexusAI account today.</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Total API Calls</CardTitle>
              <Activity className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalCalls.toLocaleString()}</div>
              <p className="text-xs text-slate-400">+20.1% from last month</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">This Month</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.thisMonth}</div>
              <p className="text-xs text-slate-400">+12% from last month</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Active Sessions</CardTitle>
              <Users className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.activeSessions}</div>
              <p className="text-xs text-slate-400">Currently active</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Success Rate</CardTitle>
              <MessageSquare className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.successRate}%</div>
              <p className="text-xs text-slate-400">+2.5% from last month</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50 border-slate-700">
            <TabsTrigger value="overview" className="text-slate-300 data-[state=active]:text-white">Overview</TabsTrigger>
            <TabsTrigger value="api-keys" className="text-slate-300 data-[state=active]:text-white">API Keys</TabsTrigger>
            <TabsTrigger value="billing" className="text-slate-300 data-[state=active]:text-white">Credits & Billing</TabsTrigger>
            <TabsTrigger value="usage" className="text-slate-300 data-[state=active]:text-white">Usage Analytics</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Quick Start</CardTitle>
                  <CardDescription className="text-slate-300">
                    Get started with the NexusAI SDK
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-slate-900/50 p-4 rounded-lg">
                    <code className="text-green-400 text-sm">
                      npm install nexusai-sdk
                    </code>
                  </div>
                  <Button asChild className="w-full bg-gradient-to-r from-purple-500 to-pink-500">
                    <Link href="https://nexusai-docs-5vsitmy23-cruso003s-projects.vercel.app" target="_blank">
                      View Documentation
                    </Link>
                  </Button>
                </CardContent>
              </Card>
              
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Recent Activity</CardTitle>
                  <CardDescription className="text-slate-300">
                    Your latest API calls and sessions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-300">Language Learning Agent</span>
                      <span className="text-slate-400">2 min ago</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-300">Emergency Services Bot</span>
                      <span className="text-slate-400">15 min ago</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-300">Customer Service Agent</span>
                      <span className="text-slate-400">1 hour ago</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="api-keys" className="space-y-4">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-white">API Keys</CardTitle>
                    <CardDescription className="text-slate-300">
                      Manage your API keys for different environments
                    </CardDescription>
                  </div>
                  <Button className="bg-gradient-to-r from-purple-500 to-pink-500">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Key
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {apiKeys.map((key) => (
                    <div key={key.id} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-white">{key.name}</h4>
                        <p className="text-sm text-slate-400">Created: {key.created} • Last used: {key.lastUsed}</p>
                        <div className="flex items-center space-x-2 mt-2">
                          <code className="text-xs bg-slate-800 px-2 py-1 rounded text-green-400">
                            {key.key}
                          </code>
                          <Button size="sm" variant="ghost" className="text-slate-400 h-6 w-6 p-0">
                            <Copy className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      <Button variant="outline" size="sm" className="border-slate-300 text-slate-100 bg-slate-800/30 hover:bg-slate-700 hover:text-white hover:border-slate-200">
                        Regenerate
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="billing" className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <CreditCard className="w-5 h-5 mr-2" />
                    Current Balance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-white mb-2">{user.credits} Credits</div>
                  <p className="text-slate-300 mb-4">≈ ${(user.credits * 0.001).toFixed(2)} USD worth</p>
                  <Button className="w-full bg-gradient-to-r from-purple-500 to-pink-500">
                    Buy More Credits
                  </Button>
                </CardContent>
              </Card>
              
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Credit Packages</CardTitle>
                  <CardDescription className="text-slate-300">
                    Choose the right package for your needs
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <div>
                      <div className="font-medium text-white">1,000 Credits</div>
                      <div className="text-sm text-slate-400">$1.00 USD</div>
                    </div>
                    <Button size="sm" variant="outline" className="border-slate-300 text-slate-100 bg-slate-800/30 hover:bg-slate-700 hover:text-white hover:border-slate-200">Buy</Button>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <div>
                      <div className="font-medium text-white">10,000 Credits</div>
                      <div className="text-sm text-slate-400">$9.00 USD</div>
                      <Badge className="bg-green-500/20 text-green-300 text-xs">10% Bonus</Badge>
                    </div>
                    <Button size="sm" variant="outline" className="border-slate-300 text-slate-100 bg-slate-800/30 hover:bg-slate-700 hover:text-white hover:border-slate-200">Buy</Button>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <div>
                      <div className="font-medium text-white">100,000 Credits</div>
                      <div className="text-sm text-slate-400">$80.00 USD</div>
                      <Badge className="bg-green-500/20 text-green-300 text-xs">20% Bonus</Badge>
                    </div>
                    <Button size="sm" variant="outline" className="border-slate-300 text-slate-100 bg-slate-800/30 hover:bg-slate-700 hover:text-white hover:border-slate-200">Buy</Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="usage" className="space-y-4">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Usage Analytics</CardTitle>
                <CardDescription className="text-slate-300">
                  Track your API usage and spending patterns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium text-white mb-3">This Month's Usage</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">Text Messages</span>
                        <span className="text-white">289 calls</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">Voice Processing</span>
                        <span className="text-white">24 calls</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">Image Analysis</span>
                        <span className="text-white">11 calls</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-white mb-3">Credits Spent</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">This Month</span>
                        <span className="text-white">153 credits</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">Average per day</span>
                        <span className="text-white">5.2 credits</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

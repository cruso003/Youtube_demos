import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"
import { redirect } from "next/navigation"
import { TopBar } from "@/components/dashboard/topbar"
import { Sidebar } from "@/components/dashboard/sidebar"

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect("/login")
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <TopBar user={session.user} />
      <div className="flex">
        <Sidebar user={session.user} />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

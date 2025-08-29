import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"
import { redirect } from "next/navigation"
import { ApiKeyManager } from "@/components/dashboard/api-key-manager"

export default async function ApiKeysPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect("/login")
  }

  return <ApiKeyManager />
}

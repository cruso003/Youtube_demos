import { getServerSession } from "next-auth"
import { authOptions } from "./auth"
import { prisma } from "./prisma"
import { UserRole } from "@prisma/client"

export async function getCurrentUser() {
  const session = await getServerSession(authOptions)
  
  if (!session?.user?.email) {
    return null
  }

  const user = await prisma.user.findUnique({
    where: { email: session.user.email },
    select: {
      id: true,
      name: true,
      email: true,
      role: true,
      credits: true,
      plan: true,
      isActive: true,
      createdAt: true,
    },
  })

  return user
}

export async function requireAuth() {
  const user = await getCurrentUser()
  
  if (!user) {
    throw new Error("Authentication required")
  }

  if (!user.isActive) {
    throw new Error("Account is deactivated")
  }

  return user
}

export async function requireRole(requiredRole: UserRole) {
  const user = await requireAuth()
  
  const roleHierarchy: Record<UserRole, number> = {
    USER: 1,
    ADMIN: 2,
    SUPER_ADMIN: 3,
  }

  if (roleHierarchy[user.role] < roleHierarchy[requiredRole]) {
    throw new Error("Insufficient permissions")
  }

  return user
}

export async function requireAdmin() {
  return requireRole(UserRole.ADMIN)
}

export async function requireSuperAdmin() {
  return requireRole(UserRole.SUPER_ADMIN)
}

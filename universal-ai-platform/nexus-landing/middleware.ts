import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server"

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token
    const isAuth = !!token
    const isAuthPage = req.nextUrl.pathname.startsWith('/login') || 
                      req.nextUrl.pathname.startsWith('/signup')
    const isDashboard = req.nextUrl.pathname.startsWith('/dashboard')
    const isAdmin = req.nextUrl.pathname.startsWith('/admin')

    // Redirect authenticated users away from auth pages
    if (isAuthPage && isAuth) {
      return NextResponse.redirect(new URL('/dashboard', req.url))
    }

    // Protect dashboard routes
    if (isDashboard && !isAuth) {
      return NextResponse.redirect(new URL('/login', req.url))
    }

    // Protect admin routes
    if (isAdmin && (!isAuth || (token.role !== 'ADMIN' && token.role !== 'SUPER_ADMIN'))) {
      return NextResponse.redirect(new URL('/dashboard', req.url))
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => true // Let the middleware function handle authorization
    },
  }
)

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/admin/:path*',
    '/login',
    '/signup'
  ]
}

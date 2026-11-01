import { createFileRoute, redirect } from '@tanstack/react-router'
import { isLoggedIn } from '../hooks/useAuth'

export const Route = createFileRoute('/')({
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: '/login' })
    }
    else {
        throw redirect({ to: '/home' })
    }
  },
})
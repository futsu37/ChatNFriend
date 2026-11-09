import { HeadContent, Outlet, createRootRoute } from '@tanstack/react-router'
import WorkspaceSidebar from '../components/WorkspaceSidebar'
import { useIsLoggedIn } from '../hooks/useAuth'

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  const loggedIn = useIsLoggedIn()

  return (
    <>
      <HeadContent />
      {loggedIn ? (
        <div className="mx-auto flex min-h-screen w-full max-w-[1440px]">
          <WorkspaceSidebar />
          <div className="min-w-0 flex-1">
            <Outlet />
          </div>
        </div>
      ) : (
        <Outlet />
      )}
    </>
  )
}

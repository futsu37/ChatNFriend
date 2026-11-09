import { Link, useRouterState } from '@tanstack/react-router'

const navItems = [
  { to: '/home', label: 'Overview', icon: '◫' },
  { to: '/friendships', label: 'Friendships', icon: '♡' },
  { to: '/posts', label: 'My posts', icon: '✎' },
  { to: '/rooms', label: 'Chat rooms', icon: '◷' },
] as const

export default function WorkspaceSidebar() {
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  })

  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-slate-200/80 bg-white px-6 py-7 lg:flex">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-700 text-lg font-bold text-white shadow-lg shadow-violet-900/20">
          C
        </div>
        <div>
          <p className="font-semibold tracking-tight text-slate-950">ChatNFriend</p>
          <p className="text-xs text-slate-500">A place for your people</p>
        </div>
      </div>

      <p className="mb-3 mt-12 px-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
        Workspace
      </p>
      <nav aria-label="Workspace">
        {navItems.map(({ to, label, icon }) => {
          const isActive =
            to === '/rooms'
              ? pathname === to || pathname.startsWith('/rooms/')
              : pathname === to

          return (
            <Link
              key={to}
              to={to}
              className={`mt-2 flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition first:mt-0 ${
                isActive
                  ? 'bg-violet-50 font-semibold text-violet-800'
                  : 'font-medium text-slate-600 hover:bg-slate-50 hover:text-violet-800'
              }`}
            >
              <span
                className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                  isActive
                    ? 'bg-white text-violet-700 shadow-sm'
                    : 'bg-slate-100 text-violet-700'
                }`}
              >
                {icon}
              </span>
              {label}
            </Link>
          )
        })}
      </nav>

      <div className="mt-auto rounded-2xl bg-gradient-to-br from-[#322267] to-[#6754b5] p-5 text-white">
        <p className="text-sm font-semibold">Good conversations start with a hello.</p>
        <p className="mt-2 text-xs leading-5 text-violet-100/80">
          Your rooms and friends will show up here as you connect.
        </p>
      </div>
    </aside>
  )
}

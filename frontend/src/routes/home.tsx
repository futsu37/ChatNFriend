import { createFileRoute, redirect } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import {
  getFriendshipsApiV1FriendshipsGet,
  readRoomsApiV1RoomsGet,
  readUserMeApiV1UsersMeGet,
} from '../client'
import useAuth, { isLoggedIn } from '../hooks/useAuth'

export const Route = createFileRoute('/home')({
  component: RouteComponent,
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: '/login' })
    }
  },
})

function RouteComponent() {
  const { logout } = useAuth()
  const currentUser = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () =>
      (await readUserMeApiV1UsersMeGet({ throwOnError: true })).data,
  })
  const rooms = useQuery({
    queryKey: ['rooms'],
    queryFn: async () =>
      (
        await readRoomsApiV1RoomsGet({
          query: { limit: 100, offset: 0 },
          throwOnError: true,
        })
      ).data,
  })
  const friendships = useQuery({
    queryKey: ['friendships'],
    queryFn: async () =>
      (
        await getFriendshipsApiV1FriendshipsGet({
          query: { limit: 100, offset: 0 },
          throwOnError: true,
        })
      ).data,
  })

  const username = currentUser.data?.username
  const myRooms =
    rooms.data?.data.filter((room) =>
      room.users_in.some((roomUser) => roomUser.user_id === currentUser.data?.id),
    ) ?? []
  const acceptedFriendships =
    friendships.data?.data.filter((friendship) => friendship.status === 'ACCEPTED') ?? []
  const incomingRequests =
    friendships.data?.data.filter(
      (friendship) =>
        friendship.status === 'PENDING' &&
        friendship.receiver_id === currentUser.data?.id,
    ) ?? []

  return (
    <main className="min-h-screen bg-[#f5f6fb] text-left text-slate-900">
      <div className="mx-auto flex min-h-screen w-full max-w-[1440px]">
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
          <div className="flex items-center gap-3 rounded-xl bg-violet-50 px-3 py-3 text-sm font-semibold text-violet-800">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-violet-700 shadow-sm">
              ◫
            </span>
            Overview
          </div>

          <div className="mt-auto rounded-2xl bg-gradient-to-br from-[#322267] to-[#6754b5] p-5 text-white">
            <p className="text-sm font-semibold">Good conversations start with a hello.</p>
            <p className="mt-2 text-xs leading-5 text-violet-100/80">
              Your rooms and friends will show up here as you connect.
            </p>
          </div>
        </aside>

        <section className="min-w-0 flex-1 px-5 py-6 sm:px-8 sm:py-8 lg:px-12 lg:py-10">
          <header className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-700 font-bold text-white">
                C
              </div>
              <span className="font-semibold tracking-tight">ChatNFriend</span>
            </div>
            <div className="hidden lg:block">
              <p className="text-sm text-slate-500">Your space</p>
              <p className="mt-1 text-sm font-medium text-slate-700">Overview</p>
            </div>
            <button
              type="button"
              onClick={logout}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-violet-200 hover:text-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-100"
            >
              Log out
            </button>
          </header>

          <div className="mt-9 flex flex-col justify-between gap-5 sm:mt-12 sm:flex-row sm:items-end">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-violet-700">
                Your dashboard
              </p>
              <h1 className="!my-2 !text-3xl !font-semibold !leading-tight !tracking-tight !text-slate-950 sm:!text-4xl">
                {currentUser.isLoading
                  ? 'Welcome'
                  : `Welcome${username ? `, ${username}` : ''}`}
              </h1>
              <p className="text-base text-slate-500">
                Here&apos;s a little snapshot of your ChatNFriend space.
              </p>
            </div>
            <div className="rounded-2xl border border-violet-100 bg-white px-4 py-3 shadow-sm">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Account
              </p>
              <p className="mt-1 text-sm font-semibold text-slate-700">
                {currentUser.data?.is_active ? 'Active' : 'Getting things ready'}
              </p>
            </div>
          </div>

          {currentUser.isError && (
            <div role="alert" className="mt-8 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
              Could not load your profile. Please refresh and try again.
            </div>
          )}

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <StatCard
              label="Chat rooms"
              value={rooms.isLoading || currentUser.isLoading ? '…' : String(myRooms.length)}
              detail="Rooms you belong to"
              icon="◷"
            />
            <StatCard
              label="Friends"
              value={friendships.isLoading ? '…' : String(acceptedFriendships.length)}
              detail="Accepted connections"
              icon="♡"
            />
            <StatCard
              label="Friend requests"
              value={friendships.isLoading ? '…' : String(incomingRequests.length)}
              detail="Waiting for your response"
              icon="＋"
            />
          </div>

          <div className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
            <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="!mb-1 !text-xl !font-semibold !tracking-tight !text-slate-950">
                    Your chat rooms
                  </h2>
                  <p className="text-sm text-slate-500">
                    Rooms you&apos;re currently a member of.
                  </p>
                </div>
                <span className="rounded-full bg-violet-50 px-3 py-1 text-xs font-semibold text-violet-800">
                  {rooms.isLoading || currentUser.isLoading ? 'Loading' : `${myRooms.length} total`}
                </span>
              </div>

              {rooms.isError && (
                <p role="alert" className="mt-6 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
                  Could not load your rooms. Please try again later.
                </p>
              )}
              {(rooms.isLoading || currentUser.isLoading) && (
                <p className="mt-6 text-sm text-slate-500">Loading your rooms…</p>
              )}
              {rooms.isSuccess && currentUser.isSuccess && myRooms.length === 0 && (
                <div className="mt-6 rounded-xl border border-dashed border-slate-200 bg-slate-50/70 px-5 py-8 text-center">
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-100 text-xl text-violet-700">
                    ◷
                  </div>
                  <p className="mt-4 font-semibold text-slate-800">No rooms yet</p>
                  <p className="mt-1 text-sm text-slate-500">
                    When you join a room, it will appear here.
                  </p>
                </div>
              )}
              {rooms.isSuccess && currentUser.isSuccess && myRooms.length > 0 && (
                <ul className="mt-6 divide-y divide-slate-100">
                  {myRooms.map((room) => (
                    <li key={room.id} className="flex items-center gap-4 py-4 first:pt-0 last:pb-0">
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-violet-50 font-semibold text-violet-800">
                        {room.name.slice(0, 1).toUpperCase()}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-semibold text-slate-800">{room.name}</p>
                        <p className="mt-1 text-sm text-slate-500">
                          {room.users_in.length} {room.users_in.length === 1 ? 'member' : 'members'}
                        </p>
                      </div>
                      <span className="h-2.5 w-2.5 shrink-0 rounded-full bg-emerald-400" aria-label="Room available" />
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-lg text-indigo-700">
                ♡
              </div>
              <h2 className="!mb-1 !mt-5 !text-xl !font-semibold !tracking-tight !text-slate-950">
                Your connections
              </h2>
              <p className="text-sm leading-6 text-slate-500">
                Your friendships and incoming requests, all in one place.
              </p>

              {friendships.isError && (
                <p role="alert" className="mt-5 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
                  Could not load your connections. Please try again later.
                </p>
              )}
              {friendships.isLoading && (
                <p className="mt-5 text-sm text-slate-500">Loading your connections…</p>
              )}
              {friendships.isSuccess && (
                <div className="mt-6 space-y-3">
                  <div className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                    <span className="text-sm text-slate-600">Accepted friendships</span>
                    <span className="font-semibold text-slate-900">{acceptedFriendships.length}</span>
                  </div>
                  <div className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                    <span className="text-sm text-slate-600">Incoming requests</span>
                    <span className="font-semibold text-slate-900">{incomingRequests.length}</span>
                  </div>
                </div>
              )}
              <p className="mt-5 border-t border-slate-100 pt-4 text-xs leading-5 text-slate-400">
                Friend management will live here as you build out those features.
              </p>
            </section>
          </div>
        </section>
      </div>
    </main>
  )
}

function StatCard({
  label,
  value,
  detail,
  icon,
}: {
  label: string
  value: string
  detail: string
  icon: string
}) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
        </div>
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-50 text-lg text-violet-700">
          {icon}
        </span>
      </div>
      <p className="mt-3 text-xs text-slate-400">{detail}</p>
    </div>
  )
}

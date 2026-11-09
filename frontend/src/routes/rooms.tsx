import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute, Link, redirect } from '@tanstack/react-router'
import {
  createRoomApiV1RoomsPost,
  joinRoomApiV1RoomsJoinIdRoomIdPost,
  leaveRoomApiV1RoomsLeaveIdRoomIdDelete,
  readRoomsApiV1RoomsGet,
  readUserMeApiV1UsersMeGet,
  type RoomPublic,
} from '../client'
import { isLoggedIn } from '../hooks/useAuth'

export const Route = createFileRoute('/rooms')({
  component: RoomsPage,
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: '/login' })
    }
  },
})

const pageSize = 100

function RoomsPage() {
  const queryClient = useQueryClient()
  const [roomName, setRoomName] = useState('')
  const [roomId, setRoomId] = useState('')
  const [search, setSearch] = useState('')
  const currentUser = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () =>
      (await readUserMeApiV1UsersMeGet({ throwOnError: true })).data,
  })
  const rooms = useQuery({
    queryKey: ['rooms', 'all'],
    queryFn: async () => {
      const allRooms: RoomPublic[] = []
      let offset = 0

      while (true) {
        const page = await readRoomsApiV1RoomsGet({
          query: { limit: pageSize, offset },
          throwOnError: true,
        })
        allRooms.push(...page.data.data)

        if (page.data.data.length < pageSize) {
          return allRooms
        }

        offset += pageSize
      }
    },
  })
  const createRoom = useMutation({
    mutationFn: async (name: string) =>
      (
        await createRoomApiV1RoomsPost({
          body: { name },
          throwOnError: true,
        })
      ).data,
    onSuccess: async () => {
      setRoomName('')
      await queryClient.invalidateQueries({ queryKey: ['rooms'] })
    },
  })
  const membershipAction = useMutation({
    mutationFn: async ({
      id,
      action,
    }: {
      id: string
      action: 'join' | 'leave'
    }) => {
      if (action === 'join') {
        await joinRoomApiV1RoomsJoinIdRoomIdPost({
          path: { room_id: id },
          throwOnError: true,
        })
      } else {
        await leaveRoomApiV1RoomsLeaveIdRoomIdDelete({
          path: { room_id: id },
          throwOnError: true,
        })
      }
      return { id, action }
    },
    onSuccess: async () => {
      setRoomId('')
      await queryClient.invalidateQueries({ queryKey: ['rooms'] })
    },
  })

  const memberRoomIds = useMemo(
    () =>
      new Set(
        rooms.data
          ?.filter((room) =>
            room.users_in.some((member) => member.user_id === currentUser.data?.id),
          )
          .map((room) => room.id) ?? [],
      ),
    [rooms.data, currentUser.data?.id],
  )
  const visibleRooms =
    rooms.data?.filter((room) => {
      const query = search.trim().toLocaleLowerCase()
      return (
        !query ||
        room.name.toLocaleLowerCase().includes(query) ||
        room.id.toLocaleLowerCase().includes(query)
      )
    }) ?? []

  return (
    <main className="min-h-screen bg-[#f5f6fb] text-left text-slate-900">
      <div className="mx-auto w-full max-w-[1120px] px-5 py-6 sm:px-8 sm:py-10">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-700 text-lg font-bold text-white shadow-lg shadow-violet-900/20">
              C
            </div>
            <div>
              <p className="font-semibold tracking-tight text-slate-950">ChatNFriend</p>
              <p className="text-xs text-slate-500">Rooms</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link
              to="/posts"
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-violet-200 hover:text-violet-800"
            >
              My posts
            </Link>
            <Link
              to="/home"
              className="rounded-xl bg-violet-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-800"
            >
              Dashboard
            </Link>
          </div>
        </header>

        <section className="mt-10 sm:mt-14">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-violet-700">
            Find your conversation
          </p>
          <h1 className="!my-2 !text-3xl !font-semibold !leading-tight !tracking-tight !text-slate-950 sm:!text-4xl">
            Chat rooms
          </h1>
          <p className="text-base text-slate-500">
            Create a room, join one by ID, or browse rooms other people have created.
          </p>
        </section>

        <div className="mt-8 grid gap-5 lg:grid-cols-2">
          <form
            className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7"
            onSubmit={(event) => {
              event.preventDefault()
              const trimmedName = roomName.trim()
              if (trimmedName && !createRoom.isPending) {
                createRoom.mutate(trimmedName)
              }
            }}
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-50 text-lg text-violet-700">
                +
              </span>
              <div>
                <h2 className="font-semibold text-slate-900">Create a room</h2>
                <p className="text-sm text-slate-500">You’ll be added as a member.</p>
              </div>
            </div>
            <label htmlFor="room-name" className="mb-2 block text-sm font-medium text-slate-700">
              Room name
            </label>
            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                id="room-name"
                value={roomName}
                onChange={(event) => {
                  setRoomName(event.target.value)
                  createRoom.reset()
                }}
                maxLength={127}
                required
                placeholder="e.g. Weekend plans"
                className="min-w-0 flex-1 rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
              />
              <button
                type="submit"
                disabled={!roomName.trim() || createRoom.isPending}
                className="rounded-xl bg-violet-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {createRoom.isPending ? 'Creating…' : 'Create room'}
              </button>
            </div>
            {createRoom.isError && (
              <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {getErrorMessage(createRoom.error, 'Could not create the room. Please try again.')}
              </p>
            )}
            {createRoom.isSuccess && (
              <p role="status" className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                Room “{createRoom.data.name}” created. You’re a member now.
              </p>
            )}
          </form>

          <form
            className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7"
            onSubmit={(event) => {
              event.preventDefault()
              const trimmedId = roomId.trim()
              if (trimmedId && !membershipAction.isPending) {
                membershipAction.mutate({ id: trimmedId, action: 'join' })
              }
            }}
          >
            <div className="mb-5 flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-lg text-indigo-700">
                ↗
              </span>
              <div>
                <h2 className="font-semibold text-slate-900">Join by room ID</h2>
                <p className="text-sm text-slate-500">Paste a room ID someone shared with you.</p>
              </div>
            </div>
            <label htmlFor="room-id" className="mb-2 block text-sm font-medium text-slate-700">
              Room ID
            </label>
            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                id="room-id"
                value={roomId}
                onChange={(event) => {
                  setRoomId(event.target.value)
                  membershipAction.reset()
                }}
                required
                placeholder="Paste the room UUID"
                className="min-w-0 flex-1 rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
              />
              <button
                type="submit"
                disabled={!roomId.trim() || membershipAction.isPending}
                className="rounded-xl border border-violet-200 bg-violet-50 px-5 py-3 text-sm font-semibold text-violet-800 transition hover:bg-violet-100 focus:outline-none focus:ring-4 focus:ring-violet-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {membershipAction.isPending &&
                membershipAction.variables?.action === 'join'
                  ? 'Joining…'
                  : 'Join room'}
              </button>
            </div>
            {membershipAction.isError && (
              <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {getErrorMessage(membershipAction.error, 'Could not join this room. Check the ID and try again.')}
              </p>
            )}
            {membershipAction.isSuccess &&
              membershipAction.data.action === 'join' && (
                <p role="status" className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                  You joined the room.
                </p>
              )}
          </form>
        </div>

        <section className="mt-9 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <h2 className="!mb-1 !text-xl !font-semibold !tracking-tight !text-slate-950">
                Browse rooms
              </h2>
              <p className="text-sm text-slate-500">
                {rooms.isSuccess
                  ? `${visibleRooms.length} of ${rooms.data.length} rooms`
                  : 'Find a room to join'}
              </p>
            </div>
            <label className="block sm:w-72">
              <span className="sr-only">Search rooms</span>
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search name or room ID"
                className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
              />
            </label>
          </div>

          {rooms.isLoading && (
            <p className="mt-6 text-sm text-slate-500">Loading rooms…</p>
          )}
          {rooms.isError && (
            <p role="alert" className="mt-6 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
              Could not load rooms. Please refresh and try again.
            </p>
          )}
          {rooms.isSuccess && visibleRooms.length === 0 && (
            <p className="mt-6 rounded-xl border border-dashed border-slate-200 bg-slate-50/70 px-5 py-8 text-center text-sm text-slate-500">
              {rooms.data.length === 0
                ? 'No rooms have been created yet. You can start one above.'
                : 'No rooms match your search.'}
            </p>
          )}
          {rooms.isSuccess && visibleRooms.length > 0 && (
            <ul className="mt-5 divide-y divide-slate-100">
              {visibleRooms.map((room) => {
                const isMember = memberRoomIds.has(room.id)
                const isJoiningThisRoom =
                  membershipAction.isPending &&
                  membershipAction.variables?.id === room.id &&
                  membershipAction.variables.action === 'join'
                const isLeavingThisRoom =
                  membershipAction.isPending &&
                  membershipAction.variables?.id === room.id &&
                  membershipAction.variables.action === 'leave'

                return (
                  <li
                    key={room.id}
                    className="flex flex-col gap-4 py-5 first:pt-1 last:pb-1 sm:flex-row sm:items-center"
                  >
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-100 to-indigo-100 font-semibold text-violet-800">
                      <Link
                        to="/rooms/$roomId"
                        params={{ roomId: room.id }}
                        aria-label={`Open ${room.name}`}
                        className="flex h-full w-full items-center justify-center"
                      >
                        {room.name.slice(0, 1).toUpperCase()}
                      </Link>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-semibold text-slate-900">
                          <Link
                            to="/rooms/$roomId"
                            params={{ roomId: room.id }}
                            className="transition hover:text-violet-800"
                          >
                            {room.name}
                          </Link>
                        </h3>
                        {isMember && (
                          <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                            Joined
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-slate-500">
                        {room.users_in.length}{' '}
                        {room.users_in.length === 1 ? 'member' : 'members'}
                      </p>
                      <p className="mt-1 break-all font-mono text-xs text-slate-400">
                        ID: {room.id}
                      </p>
                    </div>
                    <button
                      type="button"
                      disabled={membershipAction.isPending || !currentUser.data}
                      onClick={() =>
                        membershipAction.mutate({
                          id: room.id,
                          action: isMember ? 'leave' : 'join',
                        })
                      }
                      className={`shrink-0 rounded-xl px-4 py-2.5 text-sm font-semibold transition focus:outline-none focus:ring-4 disabled:cursor-not-allowed disabled:opacity-60 ${
                        isMember
                          ? 'border border-slate-200 bg-white text-slate-600 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700 focus:ring-rose-100'
                          : 'bg-violet-700 text-white hover:bg-violet-800 focus:ring-violet-200'
                      }`}
                    >
                      {isJoiningThisRoom
                        ? 'Joining…'
                        : isLeavingThisRoom
                          ? 'Leaving…'
                          : isMember
                            ? 'Leave room'
                            : 'Join room'}
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
          {membershipAction.isError && (
            <p role="alert" className="mt-5 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {getErrorMessage(membershipAction.error, 'Could not update room membership. Please try again.')}
            </p>
          )}
        </section>
      </div>
    </main>
  )
}

function getErrorMessage(error: unknown, fallback: string) {
  if (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    typeof error.detail === 'string'
  ) {
    return error.detail
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}

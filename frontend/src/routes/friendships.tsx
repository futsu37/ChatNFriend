import { useState } from 'react'
import { useMutation, useQuery, useQueries, useQueryClient } from '@tanstack/react-query'
import { createFileRoute, Link, redirect } from '@tanstack/react-router'
import {
  acceptFriendshipApiV1FriendshipsAcceptIdFriendshipIdPatch,
  findUserByIdApiV1UsersIdUserIdGet,
  findUserByUsernameApiV1UsersUsernameUsernameGet,
  getFriendshipsApiV1FriendshipsGet,
  readUserMeApiV1UsersMeGet,
  removeFriendshipApiV1FriendshipsRemoveIdFriendshipIdDelete,
  sendFriendRequestApiV1FriendshipsSendIdReceiverIdPost,
  type FriendshipPublic,
} from '../client'
import { isLoggedIn } from '../hooks/useAuth'

export const Route = createFileRoute('/friendships')({
  component: FriendshipsPage,
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: '/login' })
    }
  },
})

const pageSize = 100

function FriendshipsPage() {
  const queryClient = useQueryClient()
  const [username, setUsername] = useState('')
  const currentUser = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () =>
      (await readUserMeApiV1UsersMeGet({ throwOnError: true })).data,
  })
  const userId = currentUser.data?.id
  const friendships = useQuery({
  queryKey: ['friendships', userId],
  queryFn: async () => {
    const allFriendships: FriendshipPublic[] = []
    let offset = 0

    while (true) {
      const page = await getFriendshipsApiV1FriendshipsGet({
        query: { limit: pageSize, offset },
        throwOnError: true,
      })

      allFriendships.push(...page.data.data)

      if (page.data.data.length < pageSize) {
        return allFriendships
      }

      offset += pageSize
    }
  },
  enabled: !!userId,
})
  const mutation = useMutation({
    mutationFn: async ({
      friendshipId,
      action,
    }: {
      friendshipId: string
      action: 'accept' | 'remove'
    }) => {
      if (action === 'accept') {
        return acceptFriendshipApiV1FriendshipsAcceptIdFriendshipIdPatch({
          path: { friendship_id: friendshipId },
          throwOnError: true,
        })
      }

      return removeFriendshipApiV1FriendshipsRemoveIdFriendshipIdDelete({
        path: { friendship_id: friendshipId },
        throwOnError: true,
      })
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['friendships'] }),
  })
  const sendRequest = useMutation({
    mutationFn: async (targetUsername: string) => {
      const target = await findUserByUsernameApiV1UsersUsernameUsernameGet({
        path: { username: targetUsername },
        throwOnError: true,
      })

      if (target.data.id === userId) {
        throw new Error('You cannot send a friend request to yourself.')
      }

      await sendFriendRequestApiV1FriendshipsSendIdReceiverIdPost({
        path: { receiver_id: target.data.id },
        throwOnError: true,
      })

      return target.data.username
    },
    onSuccess: async () => {
      setUsername('')
      await queryClient.invalidateQueries({ queryKey: ['friendships'] })
    },
  })
  const relationships =
    friendships.data?.filter(
      (item) => item.receiver_id === userId || item.requestor_id === userId,
    ) ?? []
  const accepted = relationships.filter((item) => item.status === 'ACCEPTED')
  const sent = relationships.filter(
    (item) => item.status === 'PENDING' && item.requestor_id === userId,
  )
  const received = relationships.filter(
    (item) => item.status === 'PENDING' && item.receiver_id === userId,
  )
  const personIds = [
    ...new Set(
      relationships.map((item) =>
        item.requestor_id === userId ? item.receiver_id : item.requestor_id,
      ),
    ),
  ]
  const people = useQueries({
    queries: personIds.map((personId) => ({
      queryKey: ['user', personId],
      queryFn: async () =>
        (
          await findUserByIdApiV1UsersIdUserIdGet({
            path: { user_id: personId },
            throwOnError: true,
          })
        ).data,
    })),
  })
  const usersById = new Map(
    personIds.map((personId, index) => [
      personId,
      {
        username: people[index]?.data?.username,
        failed: people[index]?.isError ?? false,
      },
    ]),
  )

  const otherUserId = (friendship: FriendshipPublic) =>
    friendship.requestor_id === userId
      ? friendship.receiver_id
      : friendship.requestor_id

  return (
    <main className="min-h-screen bg-[#f5f6fb] text-left text-slate-900">
      <div className="mx-auto min-h-screen w-full max-w-[1120px] px-5 py-6 sm:px-8 sm:py-10">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-700 text-lg font-bold text-white shadow-lg shadow-violet-900/20">
              C
            </div>
            <div>
              <p className="font-semibold tracking-tight text-slate-950">ChatNFriend</p>
              <p className="text-xs text-slate-500">Your connections</p>
            </div>
          </div>
          <Link
            to="/home"
            className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-violet-200 hover:text-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-100"
          >
            Back to dashboard
          </Link>
        </header>

        <section className="mt-10 sm:mt-14">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-violet-700">
            Friendship management
          </p>
          <h1 className="!my-2 !text-3xl !font-semibold !leading-tight !tracking-tight !text-slate-950 sm:!text-4xl">
            Your connections
          </h1>
          <p className="text-base text-slate-500">
            Manage friends, sent requests, and requests waiting for you.
          </p>
        </section>

        <form
          className="mt-8 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7"
          onSubmit={(event) => {
            event.preventDefault()
            const trimmedUsername = username.trim()
            if (trimmedUsername && !sendRequest.isPending) {
              sendRequest.mutate(trimmedUsername)
            }
          }}
        >
          <div className="flex flex-col gap-5 sm:flex-row sm:items-end">
            <div className="min-w-0 flex-1">
              <label
                htmlFor="friend-username"
                className="mb-2 block text-sm font-semibold text-slate-800"
              >
                Add a friend
              </label>
              <p className="mb-3 text-sm text-slate-500">
                Enter their username to send them a request.
              </p>
              <input
                id="friend-username"
                type="text"
                autoComplete="off"
                value={username}
                disabled={sendRequest.isPending}
                onChange={(event) => {
                  setUsername(event.target.value)
                  sendRequest.reset()
                }}
                placeholder="Username"
                className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
              />
            </div>
            <button
              type="submit"
              disabled={!userId || !username.trim() || sendRequest.isPending}
              className="shrink-0 rounded-xl bg-violet-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {sendRequest.isPending ? 'Sending…' : 'Send request'}
            </button>
          </div>
          {sendRequest.isError && (
            <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {getRequestErrorMessage(sendRequest.error)}
            </p>
          )}
          {sendRequest.isSuccess && (
            <p role="status" className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
              Friend request sent to {sendRequest.data}.
            </p>
          )}
        </form>

        {(currentUser.isError || friendships.isError) && (
          <div
            role="alert"
            className="mt-8 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700"
          >
            Could not load your friendship information. Please refresh and try again.
          </div>
        )}
        {mutation.isError && (
          <div
            role="alert"
            className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700"
          >
            That action could not be completed. Please try again.
          </div>
        )}

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <CountCard label="Friends" count={accepted.length} icon="♡" />
          <CountCard label="Sent requests" count={sent.length} icon="↗" />
          <CountCard label="Incoming requests" count={received.length} icon="＋" />
        </div>

        {friendships.isLoading || currentUser.isLoading ? (
          <p className="mt-8 rounded-2xl border border-slate-200/80 bg-white px-6 py-8 text-sm text-slate-500 shadow-sm">
            Loading your connections…
          </p>
        ) : friendships.isSuccess && currentUser.isSuccess ? (
          <div className="mt-8 space-y-6">
            <RelationshipSection
              title="Friend requests for you"
              description="Accept a request to become friends, or reject it."
              emptyText="No incoming requests right now."
              items={received}
              otherUserId={otherUserId}
              usersById={usersById}
              pendingAction={mutation.isPending}
              onAccept={(friendshipId) =>
                mutation.mutate({ friendshipId, action: 'accept' })
              }
              onRemove={(friendshipId) =>
                mutation.mutate({ friendshipId, action: 'remove' })
              }
              primaryAction="Accept"
              removeAction="Reject"
              variant="incoming"
            />

            <RelationshipSection
              title="Friends"
              description="People you have accepted as friends."
              emptyText="You haven't added any friends yet."
              items={accepted}
              otherUserId={otherUserId}
              usersById={usersById}
              pendingAction={mutation.isPending}
              onRemove={(friendshipId) =>
                mutation.mutate({ friendshipId, action: 'remove' })
              }
              removeAction="Remove"
              variant="friend"
            />

            <RelationshipSection
              title="Requests you sent"
              description="These requests are waiting for the other person."
              emptyText="You don't have any pending sent requests."
              items={sent}
              otherUserId={otherUserId}
              usersById={usersById}
              pendingAction={mutation.isPending}
              onRemove={(friendshipId) =>
                mutation.mutate({ friendshipId, action: 'remove' })
              }
              removeAction="Cancel request"
              variant="sent"
            />
          </div>
        ) : null}
      </div>
    </main>
  )
}

function getRequestErrorMessage(error: unknown) {
  if (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    typeof error.detail === 'string'
  ) {
    return error.detail
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'Could not send the friend request. Please try again.'
}

function CountCard({
  label,
  count,
  icon,
}: {
  label: string
  count: number
  icon: string
}) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-50 text-lg text-violet-700">
          {icon}
        </span>
      </div>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{count}</p>
    </div>
  )
}

function RelationshipSection({
  title,
  description,
  emptyText,
  items,
  otherUserId,
  usersById,
  pendingAction,
  onAccept,
  onRemove,
  primaryAction,
  removeAction,
  variant,
}: {
  title: string
  description: string
  emptyText: string
  items: FriendshipPublic[]
  otherUserId: (friendship: FriendshipPublic) => string
  usersById: Map<string, { username?: string; failed: boolean }>
  pendingAction: boolean
  onAccept?: (friendshipId: string) => void
  onRemove: (friendshipId: string) => void
  primaryAction?: string
  removeAction: string
  variant: 'incoming' | 'friend' | 'sent'
}) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7">
      <div className="mb-5">
        <h2 className="!mb-1 !text-xl !font-semibold !tracking-tight !text-slate-950">
          {title}
          <span className="ml-2 rounded-full bg-violet-50 px-2.5 py-1 align-middle text-xs font-semibold text-violet-800">
            {items.length}
          </span>
        </h2>
        <p className="text-sm text-slate-500">{description}</p>
      </div>

      {items.length === 0 ? (
        <p className="rounded-xl border border-dashed border-slate-200 bg-slate-50/70 px-4 py-6 text-center text-sm text-slate-500">
          {emptyText}
        </p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {items.map((friendship) => {
            const personId = otherUserId(friendship)
            const person = usersById.get(personId)
            const username =
              person?.username ??
              (person?.failed ? 'Profile unavailable' : 'Loading profile…')

            return (
              <li
                key={friendship.id}
                className="flex flex-col gap-4 py-4 first:pt-0 last:pb-0 sm:flex-row sm:items-center"
              >
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-100 to-indigo-100 font-semibold text-violet-800">
                    {person?.username ? username.slice(0, 1).toUpperCase() : '…'}
                  </div>
                  <div className="min-w-0">
                    {variant === 'friend' && person?.username ? (
                      <Link
                        to="/profile/$userId"
                        params={{ userId: personId }}
                        className="truncate font-semibold text-slate-800 transition hover:text-violet-800"
                      >
                        {username}
                      </Link>
                    ) : (
                      <p className="truncate font-semibold text-slate-800">{username}</p>
                    )}
                    <p className="mt-1 text-xs text-slate-400">
                      {variant === 'incoming'
                        ? 'Sent you a friend request'
                        : variant === 'sent'
                          ? 'Friend request sent'
                          : 'Friend'}
                    </p>
                  </div>
                </div>
                <div className="flex shrink-0 gap-2">
                  {onAccept && primaryAction && (
                    <button
                      type="button"
                      disabled={pendingAction}
                      onClick={() => onAccept(friendship.id)}
                      className="rounded-lg bg-violet-700 px-3.5 py-2 text-sm font-semibold text-white transition hover:bg-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {primaryAction}
                    </button>
                  )}
                  <button
                    type="button"
                    disabled={pendingAction}
                    onClick={() => onRemove(friendship.id)}
                    className="rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-semibold text-slate-600 transition hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {removeAction}
                  </button>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}

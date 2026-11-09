import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute, Link, redirect } from '@tanstack/react-router'
import {
  findUserByIdApiV1UsersIdUserIdGet,
  getRoomMessagesApiV1RoomsMessagesIdRoomIdGet,
  joinRoomApiV1RoomsJoinIdRoomIdPost,
  deleteMessageApiV1MessagesIdMessageIdDelete,
  redactMessageApiV1MessagesIdMessageIdPatch,
  readRoomByIdApiV1RoomsIdRoomIdGet,
  readUserMeApiV1UsersMeGet,
  type MessagePublic,
  type RoomMessagePublic,
  type RoomMessagesPublic,
} from '../client'
import { client } from '../client/client.gen'
import { isLoggedIn } from '../hooks/useAuth'

export const Route = createFileRoute('/rooms_/$roomId')({
  component: RoomPage,
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: '/login' })
    }
  },
})

const previewLimit = 50

function RoomPage() {
  const { roomId } = Route.useParams()
  const queryClient = useQueryClient()
  const socketRef = useRef<WebSocket | null>(null)
  const [messageContent, setMessageContent] = useState('')
  const [openMessageMenuId, setOpenMessageMenuId] = useState<string | null>(null)
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null)
  const [editedMessageContent, setEditedMessageContent] = useState('')
  const [connectionStatus, setConnectionStatus] = useState<
    'connecting' | 'connected' | 'disconnected' | 'error'
  >('connecting')
  const [connectionError, setConnectionError] = useState('')
  const [sendError, setSendError] = useState('')
  const currentUser = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () =>
      (await readUserMeApiV1UsersMeGet({ throwOnError: true })).data,
  })
  const room = useQuery({
    queryKey: ['room', roomId],
    queryFn: async () =>
      (
        await readRoomByIdApiV1RoomsIdRoomIdGet({
          path: { room_id: roomId },
          throwOnError: true,
        })
      ).data,
  })
  const messages = useQuery({
    queryKey: ['roomMessages', roomId],
    queryFn: async () =>
      (
        await getRoomMessagesApiV1RoomsMessagesIdRoomIdGet({
          path: { room_id: roomId },
          query: { limit: previewLimit, offset: 0 },
          throwOnError: true,
        })
      ).data,
  })
  const joinRoom = useMutation({
    mutationFn: async () =>
      joinRoomApiV1RoomsJoinIdRoomIdPost({
        path: { room_id: roomId },
        throwOnError: true,
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['room', roomId] }),
        queryClient.invalidateQueries({ queryKey: ['rooms'] }),
      ])
    },
  })
  const redactMessage = useMutation({
    mutationFn: async ({
      messageId,
      content,
    }: {
      messageId: string
      content: string
    }) =>
      (
        await redactMessageApiV1MessagesIdMessageIdPatch({
          path: { message_id: messageId },
          body: { content },
          throwOnError: true,
        })
      ).data,
    onSuccess: (updatedMessage) => {
      queryClient.setQueryData<RoomMessagesPublic>(
        ['roomMessages', roomId],
        (existing) =>
          existing
            ? {
                ...existing,
                data: existing.data.map((message) =>
                  message.id === updatedMessage.id
                    ? { ...message, content: updatedMessage.content }
                    : message,
                ),
              }
            : existing,
      )
      setEditingMessageId(null)
      setOpenMessageMenuId(null)
      setEditedMessageContent('')
    },
  })
  const deleteMessage = useMutation({
    mutationFn: async (messageId: string) => {
      await deleteMessageApiV1MessagesIdMessageIdDelete({
        path: { message_id: messageId },
        throwOnError: true,
      })
      return messageId
    },
    onSuccess: (deletedMessageId) => {
      queryClient.setQueryData<RoomMessagesPublic>(
        ['roomMessages', roomId],
        (existing) =>
          {
            if (!existing) return existing
            const nextData = existing.data.filter(
              (message) => message.id !== deletedMessageId,
            )
            if (nextData.length === existing.data.length) return existing

            return {
              data: nextData,
              count: Math.max(0, existing.count - 1),
            }
          },
      )
      setOpenMessageMenuId(null)
      if (editingMessageId === deletedMessageId) {
        setEditingMessageId(null)
        setEditedMessageContent('')
      }
    },
  })

  const isMember =
    room.data?.users_in.some((member) => member.user_id === currentUser.data?.id) ?? false
  const accessToken = localStorage.getItem('access_token')

  useEffect(() => {
    if (!isMember || !messages.isSuccess || !accessToken) return

    let active = true
    let socket: WebSocket | null = null

    void Promise.resolve().then(() => {
      if (!active) return

      try {
        const apiBaseUrl = client.getConfig().baseUrl || window.location.origin
        const socketUrl = new URL(
          `/api/v1/ws/room/id/${roomId}/`,
          apiBaseUrl,
        )
        socketUrl.protocol = socketUrl.protocol === 'https:' ? 'wss:' : 'ws:'
        socket = new WebSocket(socketUrl, ['chat', `access_token.${accessToken}`])
      } catch (error) {
        setConnectionStatus('error')
        setConnectionError(
          error instanceof Error ? error.message : 'Could not connect to room chat.',
        )
        return
      }

      const roomSocket = socket
      socketRef.current = roomSocket
      roomSocket.addEventListener('open', () => {
        if (active) {
          setConnectionStatus('connected')
          setConnectionError('')
        }
      })
      roomSocket.addEventListener('message', (event: MessageEvent<string>) => {
        if (!active) return

        let received: unknown
        try {
          received = JSON.parse(event.data)
        } catch {
          setConnectionError('Received an invalid message from the room.')
          return
        }

        if (isMessageUpdatedEvent(received)) {
          if (received.message.room_id !== roomId) {
            setConnectionError('Received a message update for another room.')
            return
          }

          queryClient.setQueryData<RoomMessagesPublic>(
            ['roomMessages', roomId],
            (existing) =>
              existing
                ? {
                    ...existing,
                    data: existing.data.map((message) =>
                      message.id === received.message.id
                        ? { ...message, content: received.message.content }
                        : message,
                    ),
                  }
                : existing,
          )
          return
        }

        if (isMessageDeletedEvent(received)) {
          if (received.room_id !== roomId) {
            setConnectionError('Received a message deletion for another room.')
            return
          }

          queryClient.setQueryData<RoomMessagesPublic>(
            ['roomMessages', roomId],
            (existing) => {
              if (!existing) return existing
              const nextData = existing.data.filter(
                (message) => message.id !== received.message_id,
              )
              if (nextData.length === existing.data.length) return existing

              return {
                data: nextData,
                count: Math.max(0, existing.count - 1),
              }
            },
          )
          return
        }

        if (!isMessagePublic(received) || received.room_id !== roomId) {
          setConnectionError('Received an invalid message from the room.')
          return
        }

        const roomMessage: RoomMessagePublic = {
          id: received.id,
          content: received.content,
          sender_id: received.sender_id,
          created_at: received.created_at,
        }
        const queryKey = ['roomMessages', roomId]
        queryClient.setQueryData<RoomMessagesPublic>(queryKey, (existing) => {
          if (!existing || existing.data.some((message) => message.id === roomMessage.id)) {
            return existing
          }

          return {
            data: [roomMessage, ...existing.data].slice(0, previewLimit),
            count: Math.min(existing.count + 1, previewLimit),
          }
        })
      })
      roomSocket.addEventListener('error', () => {
        if (!active) return
        setConnectionStatus('error')
        setConnectionError('Could not connect to room chat. Please try again.')
      })
      roomSocket.addEventListener('close', (event) => {
        if (!active) return
        setConnectionStatus('disconnected')
        if (event.code === 1008) {
          setConnectionError('Your room membership or session is no longer valid.')
        }
      })
    })

    return () => {
      active = false
      if (socketRef.current === socket) socketRef.current = null
      socket?.close()
    }
  }, [accessToken, isMember, messages.isSuccess, queryClient, roomId])

  const visibleConnectionStatus = !isMember
    ? 'disconnected'
    : !accessToken
      ? 'error'
      : connectionStatus
  const visibleConnectionError =
    isMember && !accessToken
      ? 'Your session has expired. Please sign in again.'
      : connectionError

  const senderIds = useMemo(
    () =>
      [
        ...new Set(
          (messages.data?.data ?? [])
            .map((message) => message.sender_id)
            .filter((senderId): senderId is string => senderId !== null),
        ),
      ],
    [messages.data?.data],
  )
  const senders = useQueries({
    queries: senderIds.map((senderId) => ({
      queryKey: ['user', senderId],
      queryFn: async () =>
        (
          await findUserByIdApiV1UsersIdUserIdGet({
            path: { user_id: senderId },
            throwOnError: true,
          })
        ).data,
      enabled: senderId !== currentUser.data?.id,
    })),
  })
  const senderNames = new Map(
    senderIds.map((senderId, index) => [
      senderId,
      senderId === currentUser.data?.id
        ? currentUser.data.username
        : senders[index]?.data?.username ??
          (senders[index]?.isError ? 'Unknown user' : 'Loading…'),
    ]),
  )
  const chronologicalMessages = [...(messages.data?.data ?? [])].reverse()

  return (
    <main className="min-h-screen bg-[#f5f6fb] text-left text-slate-900">
      <div className="mx-auto w-full max-w-230 px-5 py-6 sm:px-8 sm:py-10">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-700 text-lg font-bold text-white shadow-lg shadow-violet-900/20">
              C
            </div>
            <div>
              <p className="font-semibold tracking-tight text-slate-950">ChatNFriend</p>
              <p className="text-xs text-slate-500">Room preview</p>
            </div>
          </div>
          <Link
            to="/rooms"
            className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-violet-200 hover:text-violet-800"
          >
            Back to rooms
          </Link>
        </header>

        {room.isLoading && (
          <p className="mt-10 rounded-2xl border border-slate-200/80 bg-white px-6 py-8 text-sm text-slate-500 shadow-sm">
            Loading room…
          </p>
        )}
        {room.isError && (
          <p role="alert" className="mt-10 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
            Could not load this room. It may no longer exist.
          </p>
        )}
        {room.isSuccess && (
          <>
            <section className="mt-6 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm sm:p-5">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-linear-to-br from-violet-100 to-indigo-100 text-xl font-semibold text-violet-800">
                  {room.data.name.slice(0, 1).toUpperCase()}
                </div>
                <div className="min-w-0 flex-1">
                  <h1 className="my-0! wrap-break-word text-2xl! font-semibold! leading-tight! tracking-tight! text-slate-950!">
                    {room.data.name}
                  </h1>
                  <p className="mt-1 text-xs text-slate-500">
                    ID <span className="break-all font-mono">{room.data.id}</span>
                    <span className="mx-2 text-slate-300">·</span>
                    {room.data.users_in.length}{' '}
                    {room.data.users_in.length === 1 ? 'member' : 'members'}
                  </p>
                </div>
                {!isMember && (
                  <button
                    type="button"
                    disabled={joinRoom.isPending || !currentUser.data}
                    onClick={() => joinRoom.mutate()}
                    className="shrink-0 rounded-xl bg-violet-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {joinRoom.isPending ? 'Joining…' : 'Join room'}
                  </button>
                )}
                {isMember && (
                  <span className="shrink-0 rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-semibold text-emerald-700">
                    You&apos;re a member
                  </span>
                )}
              </div>
            </section>

            {joinRoom.isError && (
              <p role="alert" className="mt-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {getErrorMessage(joinRoom.error)}
              </p>
            )}
            {joinRoom.isSuccess && (
              <p role="status" className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                You joined the room.
              </p>
            )}

            <section className="mt-5 rounded-2xl border border-violet-100 bg-white p-5 shadow-sm sm:p-7">
              <div className="flex items-end justify-between gap-4">
                <div>
                  <h2 className="mb-1! text-xl! font-semibold! tracking-tight! text-slate-950!">
                    Room chat
                  </h2>
                  <p className="text-sm text-slate-500">
                    Latest {previewLimit} messages.
                  </p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    visibleConnectionStatus === 'connected'
                      ? 'bg-emerald-50 text-emerald-700'
                      : visibleConnectionStatus === 'connecting'
                        ? 'bg-amber-50 text-amber-700'
                        : visibleConnectionStatus === 'error'
                          ? 'bg-rose-50 text-rose-700'
                          : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {visibleConnectionStatus === 'connected'
                    ? 'Live'
                    : visibleConnectionStatus === 'connecting'
                      ? 'Connecting…'
                      : visibleConnectionStatus === 'error'
                        ? 'Offline'
                        : 'Disconnected'}
                </span>
                {messages.isSuccess && (
                  <span className="rounded-full bg-violet-50 px-3 py-1 text-xs font-semibold text-violet-800">
                    {messages.data.count} shown
                  </span>
                )}
              </div>

              {visibleConnectionError && (
                <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
                  {visibleConnectionError}
                </p>
              )}
              {messages.isLoading && (
                <p className="mt-6 text-sm text-slate-500">Loading messages…</p>
              )}
              {messages.isError && (
                <p role="alert" className="mt-6 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
                  Could not load messages for this room. Please try again later.
                </p>
              )}
              {messages.isSuccess && chronologicalMessages.length === 0 && (
                <p className="mt-6 rounded-xl border border-dashed border-slate-200 bg-slate-50/70 px-5 py-8 text-center text-sm text-slate-500">
                  There are no messages in this room yet.
                </p>
              )}
              {messages.isSuccess && chronologicalMessages.length > 0 && (
                <ol className="mt-6 max-h-[60vh] space-y-3 overflow-y-auto">
                  {chronologicalMessages.map((message) => {
                    const senderName = message.sender_id
                      ? senderNames.get(message.sender_id) ?? 'Loading…'
                      : 'Former user'
                    const canManageMessage =
                      currentUser.data?.is_superuser === true ||
                      message.sender_id === currentUser.data?.id
                    const isEditing = editingMessageId === message.id

                    return (
                      <li key={message.id} className="rounded-xl border border-violet-100 bg-violet-50/60 px-4 py-3.5">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex min-w-0 flex-wrap items-baseline gap-x-4 gap-y-1">
                            {message.sender_id ? (
                              <Link
                                to="/profile/$userId"
                                params={{ userId: message.sender_id }}
                                className="text-sm font-semibold text-violet-950 transition hover:text-violet-700 hover:underline"
                              >
                                {senderName}
                              </Link>
                            ) : (
                              <span className="text-sm font-semibold text-violet-950">
                                {senderName}
                              </span>
                            )}
                            <time
                              dateTime={message.created_at}
                              className="text-xs text-slate-400"
                            >
                              {new Date(message.created_at).toLocaleString()}
                            </time>
                          </div>
                          {canManageMessage && (
                            <div className="relative -mr-1 -mt-1 shrink-0">
                              <button
                                type="button"
                                aria-label="Message options"
                                aria-expanded={openMessageMenuId === message.id}
                                onClick={() =>
                                  setOpenMessageMenuId((openId) =>
                                    openId === message.id ? null : message.id,
                                  )
                                }
                                className="flex h-8 w-8 items-center justify-center rounded-full text-lg leading-none text-slate-500 transition hover:bg-violet-100 hover:text-slate-800 focus:outline-none focus:ring-4 focus:ring-violet-100"
                              >
                                ⋯
                              </button>
                              {openMessageMenuId === message.id && (
                                <div className="absolute right-0 top-9 z-10 w-40 rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl">
                                  <button
                                    type="button"
                                    onClick={() => {
                                      setEditedMessageContent(message.content)
                                      setEditingMessageId(message.id)
                                      setOpenMessageMenuId(null)
                                      redactMessage.reset()
                                      deleteMessage.reset()
                                    }}
                                    className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-violet-50 hover:text-violet-800"
                                  >
                                    Redact message
                                  </button>
                                  <button
                                    type="button"
                                    disabled={deleteMessage.isPending}
                                    onClick={() => {
                                      if (
                                        window.confirm(
                                          'Delete this message? This cannot be undone.',
                                        )
                                      ) {
                                        deleteMessage.mutate(message.id)
                                        setOpenMessageMenuId(null)
                                      }
                                    }}
                                    className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-rose-600 transition hover:bg-rose-50 disabled:opacity-60"
                                  >
                                    {deleteMessage.isPending
                                      ? 'Deleting…'
                                      : 'Delete message'}
                                  </button>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                        {isEditing ? (
                          <form
                            className="mt-3"
                            onSubmit={(event) => {
                              event.preventDefault()
                              const content = editedMessageContent.trim()
                              if (content && !redactMessage.isPending) {
                                redactMessage.mutate({
                                  messageId: message.id,
                                  content,
                                })
                              }
                            }}
                          >
                            <label
                              htmlFor={`edit-message-${message.id}`}
                              className="sr-only"
                            >
                              Redact message
                            </label>
                            <textarea
                              id={`edit-message-${message.id}`}
                              value={editedMessageContent}
                              onChange={(event) =>
                                setEditedMessageContent(event.currentTarget.value)
                              }
                              maxLength={1027}
                              required
                              rows={3}
                              className="w-full resize-y rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none focus:border-violet-500 focus:ring-4 focus:ring-violet-100"
                            />
                            <div className="mt-2 flex flex-wrap gap-2">
                              <button
                                type="submit"
                                disabled={
                                  !editedMessageContent.trim() ||
                                  redactMessage.isPending
                                }
                                className="rounded-lg bg-violet-700 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-violet-800 disabled:cursor-not-allowed disabled:opacity-60"
                              >
                                {redactMessage.isPending ? 'Saving…' : 'Save'}
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  setEditingMessageId(null)
                                  setEditedMessageContent('')
                                  redactMessage.reset()
                                }}
                                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-100"
                              >
                                Cancel
                              </button>
                            </div>
                            {redactMessage.isError && (
                              <p role="alert" className="mt-2 text-xs text-rose-700">
                                {getErrorMessage(
                                  redactMessage.error,
                                  'Could not redact this message. Please try again.',
                                )}
                              </p>
                            )}
                          </form>
                        ) : (
                          <p className="mt-2 whitespace-pre-wrap wrap-break-word text-base leading-7 text-slate-800">
                            {message.content}
                          </p>
                        )}
                        {deleteMessage.isError &&
                          deleteMessage.variables === message.id && (
                          <p role="alert" className="mt-2 text-xs text-rose-700">
                            {getErrorMessage(
                              deleteMessage.error,
                              'Could not delete this message. Please try again.',
                            )}
                          </p>
                          )}
                      </li>
                    )
                  })}
                </ol>
              )}
              {isMember ? (
                <>
                  {sendError && (
                    <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
                      {sendError}
                    </p>
                  )}
                  <form
                    className="mt-6 border-t border-slate-100 pt-5"
                    onSubmit={(event) => {
                      event.preventDefault()
                      const content = messageContent.trim()
                      const socket = socketRef.current
                      if (!content || !socket || socket.readyState !== WebSocket.OPEN) {
                        setSendError('The live connection is not ready yet.')
                        return
                      }

                      try {
                        socket.send(content)
                        setMessageContent('')
                        setSendError('')
                      } catch (error) {
                        setSendError(
                          error instanceof Error
                            ? error.message
                            : 'Could not send your message.',
                        )
                      }
                    }}
                  >
                    <label
                      htmlFor="room-message"
                      className="mb-2 block text-sm font-semibold text-slate-700"
                    >
                      Send a message
                    </label>
                    <div className="flex flex-col gap-3 sm:flex-row">
                      <textarea
                        id="room-message"
                        value={messageContent}
                        onChange={(event) => setMessageContent(event.currentTarget.value)}
                        maxLength={1027}
                        rows={2}
                        placeholder="Write something to the room…"
                        className="min-h-12 flex-1 resize-y rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-violet-400 focus:ring-4 focus:ring-violet-100 disabled:bg-slate-50"
                        disabled={visibleConnectionStatus !== 'connected'}
                      />
                      <button
                        type="submit"
                        disabled={
                          visibleConnectionStatus !== 'connected' ||
                          messageContent.trim().length === 0
                        }
                        className="shrink-0 rounded-xl bg-violet-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Send
                      </button>
                    </div>
                    <p className="mt-2 text-xs text-slate-400">
                      Messages are sent live to everyone currently in the room.
                    </p>
                  </form>
                </>
              ) : (
                <p className="mt-6 rounded-xl bg-violet-50 px-4 py-3 text-sm text-violet-800">
                  Join this room to send messages.
                </p>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  )
}

function isMessagePublic(value: unknown): value is MessagePublic {
  if (typeof value !== 'object' || value === null) return false

  const message = value as Record<string, unknown>
  return (
    typeof message.id === 'string' &&
    typeof message.content === 'string' &&
    typeof message.room_id === 'string' &&
    (typeof message.sender_id === 'string' || message.sender_id === null) &&
    typeof message.created_at === 'string'
  )
}

function isMessageUpdatedEvent(
  value: unknown,
): value is { event: 'message_updated'; message: MessagePublic } {
  if (typeof value !== 'object' || value === null || !('event' in value)) {
    return false
  }

  const event = value as { event: unknown; message?: unknown }
  return event.event === 'message_updated' && isMessagePublic(event.message)
}

function isMessageDeletedEvent(
  value: unknown,
): value is { event: 'message_deleted'; room_id: string; message_id: string } {
  if (typeof value !== 'object' || value === null || !('event' in value)) {
    return false
  }

  const event = value as {
    event: unknown
    room_id?: unknown
    message_id?: unknown
  }
  return (
    event.event === 'message_deleted' &&
    typeof event.room_id === 'string' &&
    typeof event.message_id === 'string'
  )
}

function getErrorMessage(
  error: unknown,
  fallback = 'Could not join this room. Please try again.',
) {
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

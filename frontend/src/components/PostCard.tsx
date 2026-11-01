import { useMemo, useState } from 'react'
import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import {
  createCommentApiV1PostsIdCommentPostIdPost,
  deletePostApiV1PostsIdPostIdDelete,
  findUserByIdApiV1UsersIdUserIdGet,
  type PostPublic,
  updatePostApiV1PostsIdPostIdPatch,
  updatePostMeApiV1PostsMeIdPostIdPatch,
} from '../client'

export function PostCard({
  post,
  currentUserId,
  currentUsername,
  isSuperuser = false,
}: {
  post: PostPublic
  currentUserId?: string
  currentUsername?: string
  isSuperuser?: boolean
}) {
  const queryClient = useQueryClient()
  const [content, setContent] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(post.title)
  const [description, setDescription] = useState(post.description)
  const [ownerId, setOwnerId] = useState(post.owner_id)
  const postAuthor = useQuery({
    queryKey: ['user', post.owner_id],
    queryFn: async () =>
      (
        await findUserByIdApiV1UsersIdUserIdGet({
          path: { user_id: post.owner_id },
          throwOnError: true,
        })
      ).data,
    enabled: post.owner_id !== currentUserId,
  })
  const authorName =
    post.owner_id === currentUserId
      ? currentUsername ?? 'You'
      : postAuthor.data?.username ?? (postAuthor.isError ? 'Unknown user' : 'Loading…')
  const canManage = isSuperuser || post.owner_id === currentUserId
  const updatePost = useMutation({
    mutationFn: async () => {
      if (isSuperuser) {
        return updatePostApiV1PostsIdPostIdPatch({
          path: { post_id: post.id },
          body: { title: title.trim(), description: description.trim(), owner_id: ownerId },
          throwOnError: true,
        })
      }

      return updatePostMeApiV1PostsMeIdPostIdPatch({
        path: { post_id: post.id },
        body: { title: title.trim(), description: description.trim() },
        throwOnError: true,
      })
    },
    onSuccess: async () => {
      setEditing(false)
      setMenuOpen(false)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['myPosts'] }),
        queryClient.invalidateQueries({ queryKey: ['posts'] }),
        queryClient.invalidateQueries({ queryKey: ['post'] }),
        queryClient.invalidateQueries({ queryKey: ['user'] }),
      ])
    },
  })
  const deletePost = useMutation({
    mutationFn: async () =>
      deletePostApiV1PostsIdPostIdDelete({
        path: { post_id: post.id },
        throwOnError: true,
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['myPosts'] }),
        queryClient.invalidateQueries({ queryKey: ['posts'] }),
        queryClient.invalidateQueries({ queryKey: ['post'] }),
        queryClient.invalidateQueries({ queryKey: ['user'] }),
      ])
    },
  })
  const authorIds = useMemo(
    () => [...new Set(post.comments.map((comment) => comment.owner_id))],
    [post.comments],
  )
  const commentAuthors = useQueries({
    queries: authorIds.map((userId) => ({
      queryKey: ['user', userId],
      queryFn: async () =>
        (
          await findUserByIdApiV1UsersIdUserIdGet({
            path: { user_id: userId },
            throwOnError: true,
          })
        ).data,
      enabled: userId !== currentUserId,
    })),
  })
  const authorNames = new Map(
    authorIds.map((userId, index) => [
      userId,
      userId === currentUserId
        ? currentUsername
        : commentAuthors[index]?.data?.username,
    ]),
  )
  const commentMutation = useMutation({
    mutationFn: async (commentContent: string) =>
      createCommentApiV1PostsIdCommentPostIdPost({
        path: { post_id: post.id },
        body: { content: commentContent },
        throwOnError: true,
      }),
    onSuccess: async () => {
      setContent('')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['post', post.id] }),
        queryClient.invalidateQueries({ queryKey: ['myPosts'] }),
        queryClient.invalidateQueries({ queryKey: ['posts'] }),
      ])
    },
  })

  return (
    <article className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7">
      <header className="flex items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-100 to-indigo-100 font-semibold text-violet-800">
          {authorName === 'Loading…' || authorName === 'Unknown user'
            ? '…'
            : authorName.slice(0, 1).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <Link
            to="/profile/$userId"
            params={{ userId: post.owner_id }}
            className="font-semibold text-slate-800 transition hover:text-violet-800"
          >
            {authorName}
          </Link>
          <p className="mt-1 text-xs text-slate-400">
            {new Date(post.created_at).toLocaleString()}
          </p>
        </div>
        {canManage && (
          <div className="relative">
            <button
              type="button"
              aria-label="Post options"
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((open) => !open)}
              className="flex h-9 w-9 items-center justify-center rounded-full text-xl leading-none text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 focus:outline-none focus:ring-4 focus:ring-violet-100"
            >
              ⋯
            </button>
            {menuOpen && (
              <div className="absolute right-0 top-11 z-10 w-40 rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl">
                <button
                  type="button"
                  onClick={() => {
                    setTitle(post.title)
                    setDescription(post.description)
                    setOwnerId(post.owner_id)
                    setEditing(true)
                    setMenuOpen(false)
                    updatePost.reset()
                  }}
                  className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-violet-50 hover:text-violet-800"
                >
                  Edit post
                </button>
                <button
                  type="button"
                  disabled={deletePost.isPending}
                  onClick={() => {
                    if (window.confirm('Delete this post? This cannot be undone.')) {
                      deletePost.mutate()
                      setMenuOpen(false)
                    }
                  }}
                  className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-rose-600 transition hover:bg-rose-50 disabled:opacity-60"
                >
                  {deletePost.isPending ? 'Deleting…' : 'Delete post'}
                </button>
              </div>
            )}
          </div>
        )}
      </header>

      {editing ? (
        <form
          className="mt-5 space-y-4 rounded-xl border border-violet-100 bg-violet-50/40 p-4"
          onSubmit={(event) => {
            event.preventDefault()
            if (title.trim() && description.trim() && !updatePost.isPending) {
              updatePost.mutate()
            }
          }}
        >
          <div>
            <label htmlFor={`edit-title-${post.id}`} className="mb-1.5 block text-sm font-medium text-slate-700">
              Title
            </label>
            <input
              id={`edit-title-${post.id}`}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={255}
              required
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-violet-500 focus:ring-4 focus:ring-violet-100"
            />
          </div>
          <div>
            <label htmlFor={`edit-description-${post.id}`} className="mb-1.5 block text-sm font-medium text-slate-700">
              Description
            </label>
            <textarea
              id={`edit-description-${post.id}`}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              maxLength={511}
              required
              rows={4}
              className="w-full resize-y rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-violet-500 focus:ring-4 focus:ring-violet-100"
            />
          </div>
          {isSuperuser && (
            <div>
              <label htmlFor={`edit-owner-${post.id}`} className="mb-1.5 block text-sm font-medium text-slate-700">
                Author user ID
              </label>
              <input
                id={`edit-owner-${post.id}`}
                value={ownerId}
                onChange={(event) => setOwnerId(event.target.value)}
                required
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-violet-500 focus:ring-4 focus:ring-violet-100"
              />
              <p className="mt-1.5 text-xs text-slate-500">
                Superuser edit can also reassign the post to another user by ID.
              </p>
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            <button
              type="submit"
              disabled={!title.trim() || !description.trim() || updatePost.isPending}
              className="rounded-lg bg-violet-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {updatePost.isPending ? 'Saving…' : 'Save changes'}
            </button>
            <button
              type="button"
              onClick={() => {
                setEditing(false)
                setTitle(post.title)
                setDescription(post.description)
                setOwnerId(post.owner_id)
                updatePost.reset()
              }}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50"
            >
              Cancel
            </button>
          </div>
          {updatePost.isError && (
            <p role="alert" className="text-sm text-rose-700">
              Could not save these changes. Check the author ID and try again.
            </p>
          )}
        </form>
      ) : (
        <div className="mt-5">
          <h2 className="!mb-2 !text-xl !font-semibold !tracking-tight !text-slate-950">
            {post.title}
          </h2>
          <p className="whitespace-pre-wrap break-words text-sm leading-6 text-slate-600">
            {post.description}
          </p>
        </div>
      )}
      {deletePost.isError && (
        <p role="alert" className="mt-4 text-sm text-rose-700">
          Could not delete this post. Please try again.
        </p>
      )}

      <section className="mt-6 border-t border-slate-100 pt-5">
        <h3 className="text-sm font-semibold text-slate-800">
          Comments <span className="text-slate-400">({post.comments.length})</span>
        </h3>
        {post.comments.length > 0 ? (
          <ul className="mt-3 space-y-3">
            {post.comments.map((comment) => {
              const name =
                authorNames.get(comment.owner_id) ??
                (commentAuthors[authorIds.indexOf(comment.owner_id)]?.isError
                  ? 'Unknown user'
                  : 'Loading…')

              return (
                <li key={comment.id} className="rounded-xl bg-slate-50 px-4 py-3">
                  <p className="text-sm leading-6 text-slate-700">{comment.content}</p>
                  <p className="mt-2 text-xs text-slate-400">
                    <Link
                      to="/profile/$userId"
                      params={{ userId: comment.owner_id }}
                      className="font-medium text-slate-500 hover:text-violet-800"
                    >
                      {name}
                    </Link>
                    <span> · {new Date(comment.created_at).toLocaleString()}</span>
                  </p>
                </li>
              )
            })}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-slate-400">No comments yet. Start the conversation.</p>
        )}

        <form
          className="mt-4 flex flex-col gap-2 sm:flex-row"
          onSubmit={(event) => {
            event.preventDefault()
            const trimmedContent = content.trim()
            if (trimmedContent && !commentMutation.isPending) {
              commentMutation.mutate(trimmedContent)
            }
          }}
        >
          <label htmlFor={`comment-${post.id}`} className="sr-only">
            Write a comment
          </label>
          <input
            id={`comment-${post.id}`}
            value={content}
            onChange={(event) => {
              setContent(event.target.value)
              commentMutation.reset()
            }}
            maxLength={511}
            placeholder="Write a comment…"
            className="min-w-0 flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:ring-4 focus:ring-violet-100"
          />
          <button
            type="submit"
            disabled={!content.trim() || commentMutation.isPending}
            className="rounded-xl bg-violet-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {commentMutation.isPending ? 'Posting…' : 'Comment'}
          </button>
        </form>
        {commentMutation.isError && (
          <p role="alert" className="mt-3 text-sm text-rose-700">
            Could not post your comment. Please try again.
          </p>
        )}
      </section>
    </article>
  )
}

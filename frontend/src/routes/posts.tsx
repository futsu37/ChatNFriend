import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute, Link, redirect } from '@tanstack/react-router'
import {
  createPostApiV1PostsPost,
  readPostsApiV1PostsGet,
  readUserMeApiV1UsersMeGet,
  type PostPublic,
} from '../client'
import { PostCard } from '../components/PostCard'
import { isLoggedIn } from '../hooks/useAuth'

export const Route = createFileRoute('/posts')({
  component: MyPostsPage,
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: '/login' })
    }
  },
})

const pageSize = 100

function MyPostsPage() {
  const queryClient = useQueryClient()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [postFilter, setPostFilter] = useState<'all' | 'mine' | 'others'>('all')
  const currentUser = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () =>
      (await readUserMeApiV1UsersMeGet({ throwOnError: true })).data,
  })
  const posts = useQuery({
    queryKey: ['posts', currentUser.data?.id],
    enabled: !!currentUser.data?.id,
    queryFn: async () => {
      const allPosts: PostPublic[] = []
      let offset = 0

      while (true) {
        const page = await readPostsApiV1PostsGet({
          query: { limit: pageSize, offset },
          throwOnError: true,
        })
        allPosts.push(...page.data.data)

        if (page.data.data.length < pageSize) {
          return allPosts
        }

        offset += pageSize
      }
    },
  })
  const createPost = useMutation({
    mutationFn: async () =>
      createPostApiV1PostsPost({
        body: { title: title.trim(), description: description.trim() },
        throwOnError: true,
      }),
    onSuccess: async () => {
      setTitle('')
      setDescription('')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['myPosts'] }),
        queryClient.invalidateQueries({ queryKey: ['posts'] }),
      ])
    },
  })
  const visiblePosts =
    posts.data?.filter((post) => {
      if (!currentUser.data?.is_superuser || postFilter === 'all') return true
      return postFilter === 'mine'
        ? post.owner_id === currentUser.data.id
        : post.owner_id !== currentUser.data.id
    }) ?? []

  return (
    <main className="min-h-screen bg-[#f5f6fb] text-left text-slate-900">
      <div className="mx-auto w-full max-w-[920px] px-5 py-6 sm:px-8 sm:py-10">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-700 text-lg font-bold text-white shadow-lg shadow-violet-900/20">
              C
            </div>
            <div>
              <p className="font-semibold tracking-tight text-slate-950">ChatNFriend</p>
              <p className="text-xs text-slate-500">Your posts</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link
              to="/friendships"
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-violet-200 hover:text-violet-800"
            >
              Friendships
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
            Your page
          </p>
          <h1 className="!my-2 !text-3xl !font-semibold !leading-tight !tracking-tight !text-slate-950 sm:!text-4xl">
            Share something
          </h1>
          <p className="text-base text-slate-500">
            {currentUser.data?.is_superuser
              ? 'Browse posts, share an update, and manage posts across the community.'
              : 'Post an update and keep up with what you’ve shared.'}
          </p>
        </section>

        <form
          className="mt-8 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm sm:p-7"
          onSubmit={(event) => {
            event.preventDefault()
            if (title.trim() && description.trim() && !createPost.isPending) {
              createPost.mutate()
            }
          }}
        >
          <h2 className="!mb-5 !text-xl !font-semibold !tracking-tight !text-slate-950">
            Create a post
          </h2>
          <label htmlFor="post-title" className="mb-2 block text-sm font-medium text-slate-700">
            Title
          </label>
          <input
            id="post-title"
            value={title}
            onChange={(event) => {
              setTitle(event.target.value)
              createPost.reset()
            }}
            maxLength={255}
            required
            placeholder="Give your post a title"
            className="mb-4 w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
          />
          <label htmlFor="post-description" className="mb-2 block text-sm font-medium text-slate-700">
            What&apos;s on your mind?
          </label>
          <textarea
            id="post-description"
            value={description}
            onChange={(event) => {
              setDescription(event.target.value)
              createPost.reset()
            }}
            maxLength={511}
            required
            rows={4}
            placeholder="Write something to share with your friends…"
            className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
          />
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs text-slate-400">
              {description.length}/511 characters
            </p>
            <button
              type="submit"
              disabled={!title.trim() || !description.trim() || createPost.isPending}
              className="rounded-xl bg-violet-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-800 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {createPost.isPending ? 'Publishing…' : 'Publish post'}
            </button>
          </div>
          {createPost.isError && (
            <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
              Could not publish your post. Please try again.
            </p>
          )}
          {createPost.isSuccess && (
            <p role="status" className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
              Your post was published.
            </p>
          )}
        </form>

        <section className="mt-10 space-y-5">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
            <h2 className="!mb-1 !text-xl !font-semibold !tracking-tight !text-slate-950">
              {currentUser.data?.is_superuser ? 'Community posts' : 'Your posts'}
            </h2>
            <p className="text-sm text-slate-500">
              {posts.isSuccess ? `${visiblePosts.length} posts` : 'Your recent updates'}
            </p>
            </div>
            {currentUser.data?.is_superuser && (
              <div
                className="flex flex-wrap gap-2"
                aria-label="Filter posts"
                role="group"
              >
                {([
                  ['all', 'All posts'],
                  ['mine', 'My posts'],
                  ['others', "Everyone else's"],
                ] as const).map(([value, label]) => (
                  <button
                    key={value}
                    type="button"
                    aria-pressed={postFilter === value}
                    onClick={() => setPostFilter(value)}
                    className={`rounded-xl px-3.5 py-2 text-sm font-semibold transition focus:outline-none focus:ring-4 focus:ring-violet-100 ${
                      postFilter === value
                        ? 'bg-violet-700 text-white'
                        : 'border border-slate-200 bg-white text-slate-600 hover:border-violet-200 hover:text-violet-800'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {(currentUser.isLoading || posts.isLoading) && (
            <p className="rounded-2xl border border-slate-200/80 bg-white px-5 py-7 text-sm text-slate-500 shadow-sm">
              Loading your posts…
            </p>
          )}
          {(currentUser.isError || posts.isError) && (
            <p role="alert" className="rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
              Could not load your posts. Please refresh and try again.
            </p>
          )}
          {posts.isSuccess && visiblePosts.length === 0 && (
            <p className="rounded-2xl border border-dashed border-slate-200 bg-white px-5 py-8 text-center text-sm text-slate-500">
              {currentUser.data?.is_superuser && postFilter === 'others'
                ? "No posts from other users yet."
                : postFilter === 'mine'
                  ? "You haven't posted anything yet. Your first post can start here."
                  : 'No posts yet.'}
            </p>
          )}
          {posts.isSuccess &&
            visiblePosts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                currentUserId={currentUser.data?.id}
                currentUsername={currentUser.data?.username}
                isSuperuser={currentUser.data?.is_superuser}
              />
            ))}
        </section>
      </div>
    </main>
  )
}

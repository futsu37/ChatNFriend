import { useQueries, useQuery } from '@tanstack/react-query'
import { createFileRoute, Link, redirect } from '@tanstack/react-router'
import {
  findUserByIdApiV1UsersIdUserIdGet,
  readPostApiV1PostsIdPostIdGet,
  readUserMeApiV1UsersMeGet,
} from '../client'
import { PostCard } from '../components/PostCard'
import { isLoggedIn } from '../hooks/useAuth'

export const Route = createFileRoute('/profile/$userId')({
  component: UserProfilePage,
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: '/login' })
    }
  },
})

function UserProfilePage() {
  const { userId } = Route.useParams()
  const currentUser = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () =>
      (await readUserMeApiV1UsersMeGet({ throwOnError: true })).data,
  })
  const profile = useQuery({
    queryKey: ['user', userId],
    queryFn: async () =>
      (
        await findUserByIdApiV1UsersIdUserIdGet({
          path: { user_id: userId },
          throwOnError: true,
        })
      ).data,
  })
  const postIds =
    profile.data?.posts
      .map((post) => post.id)
      .filter((postId): postId is string => postId !== undefined) ?? []
  const postQueries = useQueries({
    queries: postIds.map((postId) => ({
      queryKey: ['post', postId],
      queryFn: async () =>
        (
          await readPostApiV1PostsIdPostIdGet({
            path: { post_id: postId },
            throwOnError: true,
          })
        ).data,
    })),
  })
  const posts = postQueries
    .map((query) => query.data)
    .filter((post) => post !== undefined)
    .sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))
  const isLoadingPosts =
    profile.isLoading || postQueries.some((query) => query.isLoading)
  const hasPostError = postQueries.some((query) => query.isError)

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
              <p className="text-xs text-slate-500">User profile</p>
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

        {profile.isLoading && (
          <p className="mt-10 rounded-2xl border border-slate-200/80 bg-white px-6 py-8 text-sm text-slate-500 shadow-sm">
            Loading profile…
          </p>
        )}
        {profile.isError && (
          <p role="alert" className="mt-10 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
            Could not load this profile. The user may no longer exist.
          </p>
        )}
        {profile.isSuccess && (
          <>
            <section className="mt-10 rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm sm:mt-14 sm:p-8">
              <div className="flex items-center gap-4">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-100 to-indigo-100 text-2xl font-semibold text-violet-800">
                  {profile.data.username.slice(0, 1).toUpperCase()}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold uppercase tracking-[0.16em] text-violet-700">
                    {profile.data.id === currentUser.data?.id ? 'Your profile' : 'Public profile'}
                  </p>
                  <h1 className="!my-1 !text-3xl !font-semibold !leading-tight !tracking-tight !text-slate-950">
                    {profile.data.username}
                  </h1>
                  <p className="text-sm text-slate-500">
                    {profile.data.posts.length} {profile.data.posts.length === 1 ? 'post' : 'posts'}
                  </p>
                </div>
              </div>
            </section>

            <section className="mt-8 space-y-5">
              <div>
                <h2 className="!mb-1 !text-xl !font-semibold !tracking-tight !text-slate-950">
                  Posts by {profile.data.username}
                </h2>
                <p className="text-sm text-slate-500">
                  Read their updates and join the conversation.
                </p>
              </div>

              {isLoadingPosts && (
                <p className="rounded-2xl border border-slate-200/80 bg-white px-5 py-7 text-sm text-slate-500 shadow-sm">
                  Loading posts…
                </p>
              )}
              {hasPostError && (
                <p role="alert" className="rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
                  Some posts could not be loaded. Please refresh to try again.
                </p>
              )}
              {!isLoadingPosts && posts.length === 0 && !hasPostError && (
                <p className="rounded-2xl border border-dashed border-slate-200 bg-white px-5 py-8 text-center text-sm text-slate-500">
                  {profile.data.username} hasn&apos;t posted anything yet.
                </p>
              )}
              {posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  currentUserId={currentUser.data?.id}
                  currentUsername={currentUser.data?.username}
                  isSuperuser={currentUser.data?.is_superuser}
                />
              ))}
            </section>
          </>
        )}
      </div>
    </main>
  )
}

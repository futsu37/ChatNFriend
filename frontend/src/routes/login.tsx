import { createFileRoute, redirect } from '@tanstack/react-router'
import z from 'zod'
import type { BodyGetAccessTokenApiV1LoginAccessTokenPost as AccessToken } from '../client'
import useAuth, { isLoggedIn } from '../hooks/useAuth'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from '@tanstack/react-router'

const formSchema = z.object({
  username: z.string().min(1, {error: "Username is required"}),
  password: z
  .string()
  .min(1, {error: "Password is required"})
  .min(8, {error: "Password must be at least 8 characters"})
}) satisfies z.ZodType<AccessToken>

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if(isLoggedIn())
      throw redirect({
        to: "/",
      })
  },
  head: () => ({
    meta: [
      {
        title: "Log in",
      },
    ],
  }),
})


function Login() {
  const { loginMutation } = useAuth()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })
  
  const onSubmit = (data: FormData) => {
    if(loginMutation.isPending) return
    loginMutation.mutate(data)
  }

  return (
    <main className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-[#f5f6fb] px-4 py-8 text-left sm:px-6 lg:px-8">
      <div className="pointer-events-none absolute -left-32 -top-32 h-80 w-80 rounded-full bg-violet-200/50 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 -right-24 h-96 w-96 rounded-full bg-indigo-200/50 blur-3xl" />

      <div className="relative grid w-full max-w-5xl overflow-hidden rounded-4xl border border-white/80 bg-white shadow-[0_32px_100px_-40px_rgba(47,37,93,0.35)] md:min-h-155 md:grid-cols-[0.95fr_1.05fr]">
        <aside className="relative hidden flex-col justify-between overflow-hidden bg-linear-to-br from-[#322267] via-[#473389] to-[#6754b5] p-10 text-white md:flex lg:p-12">
          <div className="pointer-events-none absolute -right-20 top-24 h-64 w-64 rounded-full border border-white/10" />
          <div className="pointer-events-none absolute -right-8 top-36 h-48 w-48 rounded-full border border-white/10" />
          <div className="pointer-events-none absolute -bottom-24 -left-16 h-72 w-72 rounded-full bg-white/5 blur-2xl" />

          <div className="relative flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/15 text-lg font-bold ring-1 ring-white/20">
              C
            </div>
            <span className="text-lg font-semibold tracking-tight">ChatNFriend</span>
          </div>

          <div className="relative my-12">
            <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-violet-200">
              Your people, closer
            </p>
            <p className="max-w-sm text-4xl font-semibold leading-tight tracking-tight lg:text-5xl">
              Good conversations start here.
            </p>
            <p className="mt-5 max-w-sm text-base leading-7 text-violet-100/80">
              Catch up, share a thought, and keep the conversation going with your friends.
            </p>
          </div>

          <p className="relative text-sm text-violet-200/75">
            A little more connected, every day.
          </p>
        </aside>

        <section className="flex items-center justify-center px-6 py-10 sm:px-10 md:px-12 lg:px-16">
          <div className="w-full max-w-md">
            <div className="mb-9 md:mb-10">
              <div className="mb-8 flex items-center gap-3 md:hidden">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 text-base font-bold text-violet-800">
                  C
                </div>
                <span className="font-semibold tracking-tight text-slate-900">ChatNFriend</span>
              </div>
              <p className="mb-3 text-sm font-semibold uppercase tracking-[0.16em] text-violet-700">
                Welcome back
              </p>
              <h1 className="my-0! text-3xl! font-semibold! leading-tight! tracking-tight! text-slate-950! sm:text-4xl!">
                Log in to your account
              </h1>
              <p className="mt-3 text-base text-slate-500">
                Pick up right where you left off.
              </p>
            </div>

            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
              <div>
                <label
                  htmlFor="username"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  autoComplete="name"
                  placeholder="Andry"
                  {...form.register("username")}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
                />
                {form.formState.errors.username && (
                  <p className="mt-2 text-sm text-rose-600">
                    {form.formState.errors.username.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  {...form.register("password")}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-[15px] text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-violet-500 focus:bg-white focus:ring-4 focus:ring-violet-100"
                />
                {form.formState.errors.password && (
                  <p className="mt-2 text-sm text-rose-600">
                    {form.formState.errors.password.message}
                  </p>
                )}
              </div>

              {loginMutation.isError && (
                <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3">
                  <p className="text-sm text-rose-700">
                    Invalid email or password.
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={loginMutation.isPending}
                className="w-full rounded-xl bg-violet-700 px-4 py-3.5 text-sm font-semibold text-white shadow-lg shadow-violet-900/15 transition hover:-translate-y-0.5 hover:bg-violet-800 hover:shadow-xl hover:shadow-violet-900/20 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              >
                {loginMutation.isPending ? "Logging in..." : "Log in"}
              </button>

              <p className="pt-2 text-center text-sm text-slate-500">
                Don&apos;t have an account?{' '}
                <Link
                  to="/register"
                  className="font-semibold text-violet-700 transition hover:text-violet-900"
                >
                  Create one
                </Link>
              </p>
            </form>
          </div>
        </section>
      </div>
    </main>
  )
}

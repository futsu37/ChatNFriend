import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useSyncExternalStore } from "react"
import { getAccessTokenApiV1LoginAccessTokenPost, readUserMeApiV1UsersMeGet, registerApiV1UsersSignupPost, type UserPublic, type UserRegister } from "../client"
import type {BodyGetAccessTokenApiV1LoginAccessTokenPost as AccessToken } from "../client"

const authStateChangeEvent = "auth-state-change"

const isLoggedIn = 
() => {
    return localStorage.getItem("access_token") !== null
}

const subscribeToAuthState = (onChange: () => void) => {
    window.addEventListener(authStateChangeEvent, onChange)
    window.addEventListener("storage", onChange)

    return () => {
        window.removeEventListener(authStateChangeEvent, onChange)
        window.removeEventListener("storage", onChange)
    }
}

const useIsLoggedIn = () =>
    useSyncExternalStore(
        subscribeToAuthState,
        isLoggedIn,
        () => false,
    )

const setAccessToken = (token: string) => {
    localStorage.setItem("access_token", token)
    window.dispatchEvent(new Event(authStateChangeEvent))
}

const clearAccessToken = () => {
    localStorage.removeItem("access_token")
    window.dispatchEvent(new Event(authStateChangeEvent))
}

const useAuth = () => {
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data: user } = useQuery<UserPublic | null, Error>({
        queryKey: ["currentUser"],
        queryFn: async () => {
            const response = await readUserMeApiV1UsersMeGet({throwOnError: true})
            return response.data ?? null
        },
        enabled: isLoggedIn(),
    })

    const signUpMutation = useMutation({
        mutationFn: (data: UserRegister) => registerApiV1UsersSignupPost({body: data, throwOnError: true}),
        onSuccess: () => {
            navigate({to: "/login"})
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["users"]})
        },
        onError: () => {console.error("Sign up mutation error")}
    })
    const login = async (data: AccessToken) => {
        const response = await getAccessTokenApiV1LoginAccessTokenPost({body:data, throwOnError: true})
        if (response.data?.access_token !== undefined)
            setAccessToken(response.data.access_token)
        
    }
    const loginMutation = useMutation({
        mutationFn: login,
        onSuccess: () => {
            navigate({to: "/"})
        },
        onError: () => {console.error("Login mutation Error")}
    })
    const logout = () => {
        clearAccessToken()
        navigate({to: "/login"})
    }
    return {
        signUpMutation,
        loginMutation,
        logout,
        user,
    }
}
export { clearAccessToken, isLoggedIn, useIsLoggedIn }
export default useAuth
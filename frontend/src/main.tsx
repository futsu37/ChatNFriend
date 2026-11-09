import { StrictMode} from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createRouter, RouterProvider } from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'
import { client } from './client/client.gen'
import { clearAccessToken } from './hooks/useAuth'



const handleApiError = (error: Error) => {
  console.log(error)
    if("detail" in error 
      && 
      (
        error["detail"] === "Not authenticated"
      || error["detail"] === "Could not validate credentials"
    )) {
      clearAccessToken()
      window.location.href = "/login"
    }
  }
  client.setConfig({auth: () => localStorage.getItem("access_token") ?? ""})
  const queryClient = new QueryClient({
    queryCache: new QueryCache({
      onError: handleApiError,
    }),
    mutationCache: new MutationCache({
      onError: handleApiError,
    }),
  })
  

  const router = createRouter({ routeTree })
  declare module "@tanstack/react-router" {
    interface Register {
      router: typeof router
    }
  }
ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router}/>
    </QueryClientProvider>
  </StrictMode>,
)

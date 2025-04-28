import { useAppStore } from "@/store/store"
import { ChatMode } from "@/types"
import { useMemo } from "react"

type RouterProps = {
  router: {
    [key in ChatMode]: React.FC
  }
}

export function useAppRouter({router}: RouterProps) {
  const {mode} = useAppStore()

  const App = useMemo(() => {
    return router[mode]
  }, [mode, router])

  return {
    App
  }
}
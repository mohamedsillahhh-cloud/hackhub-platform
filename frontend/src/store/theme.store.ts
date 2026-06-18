import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'system'

interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
  getEffectiveTheme: () => 'light' | 'dark'
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      setTheme: (theme: Theme) => {
        set({ theme })
        if (typeof window !== 'undefined') {
          const root = document.documentElement
          if (theme === 'system') {
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
            root.classList.toggle('dark', systemPrefersDark)
          } else {
            root.classList.toggle('dark', theme === 'dark')
          }
        }
      },
      getEffectiveTheme: () => {
        const { theme } = get()
        if (theme === 'system' && typeof window !== 'undefined') {
          return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        }
        return theme as 'light' | 'dark'
      },
    }),
    {
      name: 'theme-storage',
    }
  )
)

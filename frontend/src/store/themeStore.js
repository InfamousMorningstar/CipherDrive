import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useThemeStore = create(
  persist(
    (set, get) => ({
      isDark: false,
      
      toggleTheme: () => {
        set((state) => ({ isDark: !state.isDark }))
      },
      
      setTheme: (isDark) => {
        set({ isDark })
      },
    }),
    {
      name: 'theme-storage',
    }
  )
)

export { useThemeStore }
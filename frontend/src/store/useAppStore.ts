
import { create } from 'zustand'
import api, { StudentProfile, ApplicationStats } from '../services/api'

interface AppState {
    profile: StudentProfile | null
    stats: ApplicationStats | null
    isLoading: boolean
    error: string | null

    // Onboarding
    hasProfile: boolean
    hasAppliedOnce: boolean
    hasSavedJob: boolean

    // Actions
    fetchInitialData: () => Promise<void>
    setProfile: (profile: StudentProfile | null) => void
}

export const useAppStore = create<AppState>((set) => ({
    profile: null,
    stats: null,
    isLoading: false,
    error: null,

    hasProfile: false,
    hasAppliedOnce: false,
    hasSavedJob: false, // Could be derived from stats or job list

    setProfile: (profile) => set({
        profile,
        hasProfile: !!profile
    }),

    fetchInitialData: async () => {
        set({ isLoading: true, error: null })
        try {
            // Parallel fetch
            const [profileRes, statsRes] = await Promise.allSettled([
                api.getProfile(),
                api.getApplicationStats()
            ])

            let profile = null
            let hasProfile = false
            if (profileRes.status === 'fulfilled' && profileRes.value.data) {
                profile = profileRes.value.data
                hasProfile = true
            }

            let stats = null
            let hasAppliedOnce = false
            if (statsRes.status === 'fulfilled' && statsRes.value.data) {
                stats = statsRes.value.data
                hasAppliedOnce = stats.total > 0
            }

            set({
                profile,
                hasProfile,
                stats,
                hasAppliedOnce,
                isLoading: false
            })

        } catch (err: any) {
            set({ error: err.message || 'Failed to initialize app', isLoading: false })
        }
    }
}))

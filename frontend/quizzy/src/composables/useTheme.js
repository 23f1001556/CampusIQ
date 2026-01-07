import { ref, onMounted, watch } from 'vue'

export function useTheme() {
    // Options: 'light', 'dark', 'auto'
    const theme = ref(localStorage.getItem('theme') || 'dark')
    
    const applyTheme = (newTheme) => {
        const root = document.documentElement
        if (newTheme === 'dark' || (newTheme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            root.classList.add('dark')
        } else {
            root.classList.remove('dark')
        }
    }

    watch(theme, (newTheme) => {
        localStorage.setItem('theme', newTheme)
        applyTheme(newTheme)
    })

    onMounted(() => {
        applyTheme(theme.value)
        
        // Listen for system changes if in auto mode
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (theme.value === 'auto') {
                applyTheme('auto')
            }
        })
    })

    const toggleTheme = () => {
        if (theme.value === 'light') theme.value = 'dark'
        else if (theme.value === 'dark') theme.value = 'auto'
        else theme.value = 'light'
    }

    const setTheme = (val) => {
        theme.value = val
    }

    return {
        theme,
        toggleTheme,
        setTheme
    }
}

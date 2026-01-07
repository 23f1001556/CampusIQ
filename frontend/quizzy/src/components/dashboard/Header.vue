<template>
    <header class="header">
        <div class="header-content">
            <div class="left-section">
                <button class="toggle-btn" @click="$emit('toggle-sidebar')" aria-label="Toggle Sidebar">
                    <span class="icon">☰</span>
                </button>
                <h2 class="page-title">{{ title }}</h2>
            </div>

            <div class="right-section">
                <button class="theme-toggle" @click="toggleTheme" title="Toggle Theme">
                    <span class="icon" v-if="theme === 'light'">☀️</span>
                    <span class="icon" v-else-if="theme === 'dark'">🌙</span>
                    <span class="icon" v-else>🌗</span>
                </button>

                <div class="user-profile">
                    <div class="avatar">
                        <span>{{ userInitials }}</span>
                    </div>
                </div>
            </div>
        </div>
    </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'

const route = useRoute()
const { theme, toggleTheme } = useTheme()

const props = defineProps({
    user: {
        type: Object,
        default: () => ({ username: 'Guest' })
    }
})

defineEmits(['toggle-sidebar'])

const title = computed(() => {
    return route.name || 'Dashboard'
})

const userInitials = computed(() => {
    return (props.user?.username || 'G').substring(0, 2).toUpperCase()
})
</script>

<style scoped>
.header {
    height: 70px;
    width: 100%;
    position: sticky;
    top: 0;
    z-index: 40;
    background: rgba(255, 255, 255, 0.85);
    /* Fallback */
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--glass-border);
    transition: all 0.3s ease;
}

:root.dark .header {
    background: rgba(15, 23, 42, 0.85);
}

.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;
    padding: 0 2rem;
    max-width: 1600px;
    margin: 0 auto;
}

.left-section {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.toggle-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-secondary);
    padding: 0.5rem;
    border-radius: 8px;
    transition: all 0.2s;
    display: none;
    /* Hidden by default (Desktop) */
    align-items: center;
    justify-content: center;
}

.toggle-btn:hover {
    background: var(--bg-accent);
    color: var(--primary-color);
}

.page-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    color: var(--text-primary);
    opacity: 0;
    animation: fadeIn 0.4s ease forwards;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(4px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.right-section {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.theme-toggle {
    background: var(--bg-accent);
    border: 1px solid transparent;
    width: 40px;
    height: 40px;
    border-radius: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    color: var(--text-primary);
}

.theme-toggle:hover {
    transform: translateY(-2px);
    border-color: var(--border-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.user-profile {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
}

.avatar {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    color: white;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
    transition: transform 0.2s;
}

.user-profile:hover .avatar {
    transform: scale(1.05);
}

@media (max-width: 1024px) {
    .toggle-btn {
        display: flex;
    }

    .header-content {
        padding: 0 1rem;
    }

    .page-title {
        font-size: 1.1rem;
    }
}
</style>

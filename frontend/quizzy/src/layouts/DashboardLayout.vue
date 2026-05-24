<template>
    <div class="dashboard-layout">
        <!-- Overlay for Mobile -->
        <transition name="fade">
            <div v-if="isMobile && isSidebarOpen" class="overlay" @click="closeSidebar"></div>
        </transition>

        <!-- Sidebar Component -->
        <Sidebar v-if="!isFullScreen" :is-collapsed="!isMobile && isSidebarCollapsed" :is-mobile="isMobile"
            :is-open="isSidebarOpen" :user="user" class="layout-sidebar" @logout="handleLogout"
            @toggle-sidebar="handleSidebarToggle" />

        <!-- Main Content Wrapper -->
        <div class="main-wrapper"
            :class="{ 'sidebar-collapsed': isSidebarCollapsed && !isMobile, 'full-screen': isFullScreen }">
            <Header v-if="!isFullScreen" :user="user" @toggle-sidebar="handleSidebarToggle" />

            <!-- Page Content -->
            <main class="content-area">
                <router-view v-slot="{ Component }">
                    <transition name="fade-slide" mode="out-in">
                        <component :is="Component" />
                    </transition>
                </router-view>
            </main>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Sidebar from '@/components/dashboard/Sidebar.vue'
import Header from '@/components/dashboard/Header.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const isFullScreen = computed(() => route.meta.fullScreen)

// State
const isSidebarCollapsed = ref(false)
const isSidebarOpen = ref(false)
const isMobile = ref(false)
const user = ref({ username: 'Guest' })

// Methods
const checkScreen = () => {
    isMobile.value = window.innerWidth < 1024 // Increased breakpoint for tablet friendliness
    if (!isMobile.value) {
        isSidebarOpen.value = false
    } else {
        isSidebarCollapsed.value = false // Reset collapsed state on mobile
    }
}

const handleSidebarToggle = () => {
    if (isMobile.value) {
        isSidebarOpen.value = !isSidebarOpen.value
    } else {
        isSidebarCollapsed.value = !isSidebarCollapsed.value
    }
}

const closeSidebar = () => {
    isSidebarOpen.value = false
}

const loadUser = () => {
    try {
        const stored = localStorage.getItem('user')
        if (stored) user.value = JSON.parse(stored)
    } catch (e) {
        console.error('Failed to load user', e)
    }
}

const handleLogout = async () => {
    try {
        await api.post('/auth/logout')
    } catch (error) {
        console.error("Logout error", error)
    } finally {
        localStorage.clear()
        router.push('/login')
    }
}

// Lifecycle
onMounted(() => {
    checkScreen()
    loadUser()
    window.addEventListener('resize', checkScreen)
})

onUnmounted(() => {
    window.removeEventListener('resize', checkScreen)
})
</script>

<style scoped>
.dashboard-layout {
    min-height: 100vh;
    background-color: var(--bg-primary);
    overflow-x: hidden;
    position: relative;
}

.overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    z-index: 45;
    transition: opacity 0.3s ease;
}

.main-wrapper {
    display: flex;
    flex-direction: column;
    min-width: 0;
    margin-left: 220px;
    min-height: 100vh;
    transition: margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-wrapper.sidebar-collapsed {
    margin-left: 80px;
}

.content-area {
    padding: 2rem;
    flex: 1;
    max-width: 1600px;
    margin: 0 auto;
    width: 100%;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: all 0.3s ease;
}

.fade-slide-enter-from {
    opacity: 0;
    transform: translateY(10px);
}

.fade-slide-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

@media (max-width: 1024px) {
    .content-area {
        padding: 1rem;
    }

    .main-wrapper {
        margin-left: 0;
    }
}

.main-wrapper.full-screen {
    margin-left: 0;
}
</style>

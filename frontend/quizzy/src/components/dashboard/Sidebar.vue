<template>
    <aside class="sidebar" :class="{ collapsed: isCollapsed, mobile: isMobile, open: isOpen }">
        <div class="sidebar-header">
            <button v-if="!isMobile" class="attr-toggle-btn" @click="$emit('toggle-sidebar')"
                :title="isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'">
                <span class="toggle-icon">{{ isCollapsed ? '☰' : '✕' }}</span>
            </button>
            <div class="logo-container">
                <div class="logo-icon">Q</div>
                <h1 v-if="!isCollapsed" class="logo-text">Quizzy</h1>
            </div>
        </div>

        <nav class="sidebar-nav">
            <router-link v-for="link in links" :key="link.path" :to="link.path" class="nav-item"
                :active-class="link.exact ? '' : 'active'" :exact-active-class="link.exact ? 'active' : ''"
                :title="isCollapsed ? link.text : ''" @click="handleNavClick">
                <span class="icon">{{ link.icon }}</span>
                <span class="text">{{ link.text }}</span>
                <div class="active-indicator"></div>
            </router-link>
        </nav>

        <div class="sidebar-footer">
            <button class="logout-btn" @click="$emit('logout')" title="Logout">
                <span class="icon">🚪</span>
                <span v-if="!isCollapsed" class="text">Logout</span>
            </button>
        </div>
    </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    isCollapsed: {
        type: Boolean,
        default: false
    },
    isMobile: {
        type: Boolean,
        default: false
    },
    isOpen: {
        type: Boolean,
        default: false
    },
    user: {
        type: Object,
        default: () => ({})
    }
})

const emit = defineEmits(['logout', 'toggle-sidebar'])

const handleNavClick = () => {
    if (props.isMobile) {
        emit('toggle-sidebar')
    }
}

const links = computed(() => {
    const isStaff = props.user?.role === 'admin' || props.user?.role === 'manager'
    const isAdmin = props.user?.role === 'admin' || props.user?.is_admin || props.user?.isadmin

    const allLinks = [
        {
            path: isAdmin ? '/dashboard/admin' : (props.user?.role === 'manager' ? '/dashboard/manager' : '/dashboard'),
            text: 'Dashboard',
            icon: '📊',
            exact: true
        },
        { path: '/dashboard/profile', text: 'Profile', icon: '👤' },
        { path: '/dashboard/subjects', text: 'Subjects', icon: '📚' },
        { path: '/dashboard/leaderboard', text: 'Leaderboard', icon: '🏆' },
        { path: '/dashboard/mock-quizzes', text: 'Graded Quizzes', icon: '🎯' },
        { path: '/dashboard/institute', text: 'Institute', icon: '🏛️' },
        { path: '/dashboard/ai-hub', text: 'AI Hub', icon: '🤖' }
    ]

    let filteredLinks = allLinks

    if (isAdmin) {
        // Rename 'Subjects' to 'Files' for Admins
        filteredLinks = filteredLinks.map(l => l.text === 'Subjects' ? { ...l, text: 'Files' } : l)
    }
    
    if (props.user?.role === 'manager') {
        filteredLinks = filteredLinks.filter(l => l.text !== 'Institute')
    }

    return filteredLinks
})
</script>

<style scoped>
.sidebar {
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1.5rem 1rem;
    width: 220px;
    z-index: 50;
    width: 220px;
    z-index: 50;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02);
    overflow-y: auto;
    /* Allow scroll if needed */
    scrollbar-width: none;
    /* Firefox: hide scrollbar */
    position: fixed;
    left: 0;
    top: 0;
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar::-webkit-scrollbar {
    display: none;
    /* Chrome/Safari: hide scrollbar */
}

.sidebar.collapsed {
    width: 80px;
}

.sidebar.collapsed .logo-container {
    justify-content: center;
}

/* Removed collapsed styles as feature is removed */
.sidebar-header {
    margin-bottom: 2rem;
    padding: 0 0.5rem;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
}

.sidebar.collapsed .sidebar-header {
    align-items: center;
}

.attr-toggle-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 1.25rem;
    transition: all 0.3s ease;
    flex-shrink: 0;
}

.attr-toggle-btn:hover {
    background: var(--bg-accent);
    color: var(--primary-color);
}

.toggle-icon {
    line-height: 1;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    overflow: hidden;
    white-space: nowrap;
}

.logo-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    color: white;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.25rem;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
}

.logo-text {
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(to right, var(--text-primary), var(--primary-color));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

/* Toggle Button */
/* Toggle Button Removed */


.sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    /* Reduced gap */
    padding: 0.75rem 0.875rem;
    /* Reduced padding */
    border-radius: 12px;
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    /* Slightly smaller font */
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
    white-space: nowrap;
}

.nav-item:hover {
    background: var(--bg-accent);
    color: var(--primary-color);
    transform: translateX(4px);
}

.nav-item.active {
    background: linear-gradient(to right, var(--bg-accent), transparent);
    color: var(--primary-color);
    font-weight: 600;
}

.nav-item .icon {
    font-size: 1.25rem;
    flex-shrink: 0;
    width: 24px;
    text-align: center;
    transition: transform 0.2s;
}

.nav-item:hover .icon {
    transform: scale(1.1);
}

.nav-item .text {
    flex: 1;
    opacity: 1;
    transition: opacity 0.3s;
}

.sidebar.collapsed .text {
    opacity: 0;
    width: 0;
    margin: 0;
    pointer-events: none;
}

.sidebar.collapsed .nav-item {
    justify-content: center;
    padding: 0.75rem;
}

.sidebar.collapsed .nav-item .icon {
    font-size: 1.5rem;
}

.active-indicator {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%) scaleY(0);
    width: 3px;
    height: 60%;
    background: var(--primary-color);
    border-radius: 0 4px 4px 0;
    transition: transform 0.2s;
}

.nav-item.active .active-indicator {
    transform: translateY(-50%) scaleY(1);
}

.sidebar-footer {
    border-top: 1px solid var(--border-color);
    padding-top: 1.5rem;
    margin-top: auto;
}

.sidebar.collapsed .logout-btn .text {
    display: none;
}

.logout-btn {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.875rem 1rem;
    background: transparent;
    border: 1px solid var(--danger-color);
    color: var(--danger-color);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 0.95rem;
    white-space: nowrap;
    text-decoration: underline;
}

.logout-btn:hover {
    background: var(--danger-color);
    color: white;
    text-decoration: none;
}

.logout-btn .icon {
    font-size: 1.2rem;
    flex-shrink: 0;
}

/* Mobile Styles */
.sidebar.mobile {
    position: fixed;
    border-right: none;
    top: 0;
    left: 0;
    bottom: 0;
    transform: translateX(-100%);
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.1);
}

.sidebar.mobile.open {
    transform: translateX(0);
}
</style>

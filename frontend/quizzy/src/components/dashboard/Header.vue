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

                <button class="icon-btn" @click="openSettings" title="Settings">
                    <span class="icon">⚙️</span>
                </button>
            </div>
        </div>

        <!-- Settings Modal -->
        <Teleport to="body">
            <div v-if="showSettings" class="modal-backdrop" @click.self="closeSettings">
                <div class="modal-card">
                    <div class="modal-header">
                        <h3>Settings</h3>
                        <button class="close-btn" @click="closeSettings">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="setting-section">
                            <h4>AI Configuration</h4>
                            <p class="section-desc">Configure your Gemini API Key to enable AI features.</p>

                            <div class="form-group">
                                <label>Gemini API Key</label>
                                <div class="input-wrapper">
                                    <input :type="showKey ? 'text' : 'password'" v-model="geminiKey"
                                        placeholder="Enter your API Key" class="api-input">
                                    <button class="toggle-visibility" @click="showKey = !showKey">
                                        {{ showKey ? '🙈' : '👁️' }}
                                    </button>
                                </div>
                                <small class="help-text">Leave blank to use system default.</small>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-cancel" @click="closeSettings">Cancel</button>
                        <button class="btn-save" @click="saveSettings" :disabled="saving">
                            {{ saving ? 'Saving...' : 'Save Changes' }}
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>
    </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import api from '@/services/api'

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

// Settings Logic
const showSettings = ref(false)
const geminiKey = ref('')
const showKey = ref(false)
const saving = ref(false)

const openSettings = async () => {
    showSettings.value = true
    try {
        // Fetch current key
        const res = await api.get('/users/profile')
        geminiKey.value = res.data.user.gemini_api_key || ''
    } catch (e) {
        console.error("Failed to fetch settings", e)
    }
}

const closeSettings = () => {
    showSettings.value = false
    geminiKey.value = ''
    showKey.value = false
}

const saveSettings = async () => {
    saving.value = true
    try {
        await api.put('/users/profile', {
            gemini_api_key: geminiKey.value
        })
        closeSettings()
        alert('Settings saved successfully')
    } catch (e) {
        console.error("Failed to save settings", e)
        alert('Failed to save settings')
    } finally {
        saving.value = false
    }
}
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
    gap: 1rem;
}

.theme-toggle,
.icon-btn {
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
    font-size: 1.2rem;
}

.theme-toggle:hover,
.icon-btn:hover {
    transform: translateY(-2px);
    border-color: var(--border-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.user-profile {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    margin-left: 0.5rem;
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

/* Modal Styles */
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-card {
    background: var(--bg-secondary);
    border-radius: 16px;
    width: 90%;
    max-width: 500px;
    border: 1px solid var(--border-color);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

.modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: var(--text-primary);
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: var(--text-secondary);
    cursor: pointer;
}

.modal-body {
    padding: 1.5rem;
}

.setting-section h4 {
    margin: 0 0 0.5rem 0;
    color: var(--text-primary);
}

.section-desc {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-primary);
    font-size: 0.9rem;
}

.input-wrapper {
    display: flex;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-primary);
    overflow: hidden;
    transition: border-color 0.2s;
}

.input-wrapper:focus-within {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.api-input {
    flex: 1;
    border: none;
    padding: 0.75rem 1rem;
    background: transparent;
    color: var(--text-primary);
    font-family: monospace;
    font-size: 0.9rem;
}

.api-input:focus {
    outline: none;
}

.toggle-visibility {
    background: transparent;
    border: none;
    padding: 0 1rem;
    cursor: pointer;
    font-size: 1.2rem;
}

.help-text {
    display: block;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    background: var(--bg-primary);
}

.btn-cancel {
    padding: 0.6rem 1.2rem;
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-secondary);
    cursor: pointer;
    font-weight: 500;
}

.btn-save {
    padding: 0.6rem 1.2rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: opacity 0.2s;
}

.btn-save:hover {
    opacity: 0.9;
}

.btn-save:disabled {
    opacity: 0.7;
    cursor: default;
}
</style>

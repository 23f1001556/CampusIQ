<template>
    <div class="history-container">
        <div class="header-actions">
            <h3 class="section-title">Activity Log</h3>
            <button v-if="history.length > 0" class="btn-clear" @click="clearHistory" :disabled="clearing">
                {{ clearing ? 'Clearing...' : 'Clear History' }}
            </button>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
        </div>
        
        <div v-else-if="history.length === 0" class="empty-state">
            <span>📜</span>
            <p>No history found</p>
        </div>

        <div v-else class="history-grid">
            <div v-for="item in history" :key="item.id" class="history-card">
                <div class="card-header">
                    <span class="badge" :class="item.action">{{ formatAction(item.action) }}</span>
                    <span class="date">{{ formatDate(item.created_at) }}</span>
                </div>
                <div class="card-body">
                    <p class="prompt-text" v-if="shouldShowPrompt(item.prompt)">
                        {{ formatPrompt(item.prompt) }}
                    </p>
                    <div class="response-preview" :title="item.response">
                        {{ truncate(item.response) }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const history = ref([])
const loading = ref(true)
const clearing = ref(false)

const fetchHistory = async () => {
    try {
        const res = await api.get('/ai/history')
        history.value = res.data.history
    } catch (error) {
        console.error("History error", error)
    } finally {
        loading.value = false
    }
}

const clearHistory = async () => {
    if(!confirm("Are you sure you want to clear your entire history?")) return
    
    clearing.value = true
    try {
        await api.delete('/ai/history')
        history.value = []
    } catch (error) {
        alert("Failed to clear history")
    } finally {
        clearing.value = false
    }
}

const formatDate = (iso) => {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'})
}

const formatAction = (action) => {
    return action.replace('pdf_', '').replace('_', ' ')
}

const shouldShowPrompt = (prompt) => {
    if (!prompt) return false
    if (prompt.includes('Query: None') && prompt.length < 20) return false
    return true
}

const formatPrompt = (prompt) => {
    // Backend also cleans this now, but extra safety
    return prompt.replace(', Query: None', '')
}

const truncate = (text) => {
    if (!text) return ''
    return text.length > 120 ? text.substring(0, 120) + '...' : text
}

onMounted(() => {
    fetchHistory()
})
</script>

<style scoped>
.header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-title {
    margin: 0;
    font-size: 1.25rem;
    color: var(--text-primary);
}

.btn-clear {
    background: transparent;
    border: 1px solid var(--border-color);
    color: #ef4444;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-clear:hover {
    background: #fef2f2;
    border-color: #ef4444;
}

.history-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
}

.history-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
}

.history-card:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.badge {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    background: var(--bg-secondary);
    font-weight: 600;
    text-transform: uppercase;
}

.date {
    font-size: 0.75rem;
    color: var(--text-secondary);
}

.card-body {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.prompt-text {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.response-preview {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.4;
    margin-top: auto;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
}

.loading-state {
    display: flex;
    justify-content: center;
    padding: 2rem;
}

.spinner {
    width: 30px;
    height: 30px;
    border: 3px solid rgba(0,0,0,0.1);
    border-left-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>

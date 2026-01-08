<template>
    <div class="saved-content-container">
        <header class="page-header">
            <button @click="$router.push('/dashboard/institute')" class="back-link">← Back to Institute</button>
            <h1>Saved AI Content</h1>
            <p class="subtitle">Your history of summaries and generated quizzes</p>
        </header>

        <div v-if="loading" class="loading-state">
            <div class="loader"></div>
            <p>Fetching your saved items...</p>
        </div>

        <div v-else-if="savedItems.length === 0" class="empty-state">
            <div class="empty-icon">🔖</div>
            <h3>Nothing saved yet</h3>
            <p>Items will appear here once you use the AI tools in any course.</p>
        </div>

        <div v-else class="saved-list">
            <div v-for="item in savedItems" :key="item.id" class="saved-card">
                <div class="card-header">
                    <span class="badge" :class="item.content_type">{{ item.content_type.toUpperCase() }}</span>
                    <span class="date">{{ formatDate(item.created_at) }}</span>
                </div>
                <div class="card-body">
                    <p class="source-hint">Source: {{ item.source_type }}</p>
                    <div class="content-preview">
                        {{ item.content }}
                    </div>
                </div>
                <div class="card-actions">
                    <button @click="viewFull(item)" class="view-btn">Full View</button>
                </div>
            </div>
        </div>

        <!-- Viewer Modal -->
        <div v-if="showViewer" class="modal-overlay" @click.self="showViewer = false">
            <div class="modal-content large-modal">
                <div class="modal-header">
                    <h3>AI {{ selectedItem.content_type === 'summary' ? 'Summary' : 'Quiz' }}</h3>
                    <button @click="showViewer = false" class="close-btn">✕</button>
                </div>
                <div class="modal-body">
                    <pre>{{ selectedItem.content }}</pre>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../../services/api'

const savedItems = ref([])
const loading = ref(true)
const showViewer = ref(false)
const selectedItem = ref({})

const fetchSavedItems = async () => {
    try {
        loading.value = true
        const response = await api.get('/institute/ai/saved')
        savedItems.value = response.data
    } catch (error) {
        console.error('Failed to fetch saved content')
    } finally {
        loading.value = false
    }
}

const viewFull = (item) => {
    selectedItem.value = item
    showViewer.value = true
}

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString()
}

onMounted(fetchSavedItems)
</script>

<style scoped>
.saved-content-container {
    padding: 2rem;
    max-width: 900px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 2.5rem;
}

.back-link {
    background: transparent;
    border: none;
    color: var(--primary-color);
    cursor: pointer;
    margin-bottom: 1rem;
    padding: 0;
}

.subtitle {
    color: var(--text-secondary);
}

.saved-list {
    display: grid;
    gap: 1.5rem;
}

.saved-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.2s;
}

.card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.badge {
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
}

.badge.summary {
    background: rgba(99, 102, 241, 0.2);
    color: #818cf8;
}

.badge.quiz {
    background: rgba(168, 85, 247, 0.2);
    color: #c084fc;
}

.date {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.source-hint {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    italic: true;
}

.content-preview {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.5;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.view-btn {
    background: transparent;
    border: 1px solid var(--primary-color);
    color: var(--primary-color);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.modal-content {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 2rem;
    width: 90%;
    max-width: 700px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: var(--text-secondary);
    cursor: pointer;
}

.modal-body pre {
    white-space: pre-wrap;
    background: var(--bg-main);
    padding: 1.5rem;
    border-radius: 12px;
    max-height: 500px;
    overflow-y: auto;
}

.loading-state,
.empty-state {
    text-align: center;
    padding: 4rem;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}
</style>

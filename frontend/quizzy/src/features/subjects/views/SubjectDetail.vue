<template>
    <div class="subject-detail-container">
        <!-- Header -->
        <div class="page-header" v-if="subject">
            <div class="breadcrumb">
                <router-link to="/dashboard/subjects" class="breadcrumb-item">My Subjects</router-link>
                <span class="separator">/</span>
                <span class="current">{{ subject.name }}</span>
            </div>

            <div class="header-main">
                <div class="header-info">
                    <h1>{{ subject.name }}</h1>
                    <p>{{ subject.description || 'No description provided.' }}</p>
                    <div class="stats-row">
                        <span class="stat-badge">{{ filteredChapters.length }} Chapters</span>
                        <span class="stat-badge secondary">{{ totalQuizzes }} Quizzes</span>
                    </div>
                </div>
                <div class="header-actions">
                    <div class="search-wrapper">
                        <span class="search-icon">🔍</span>
                        <input v-model="searchQuery" type="text" placeholder="Search chapters..." class="search-input">
                    </div>
                    <button class="btn-primary" @click="openCreateModal">
                        <span class="btn-icon">+</span> New Chapter
                    </button>
                </div>
            </div>
        </div>

        <div v-if="loading" class="chapters-grid">
            <div v-for="n in 3" :key="n" class="skeleton-card"></div>
        </div>

        <div v-else-if="filteredChapters.length === 0" class="empty-state">
            <div class="empty-icon">📖</div>
            <h3>No chapters found</h3>
            <p v-if="searchQuery">No matches for "{{ searchQuery }}".</p>
            <p v-else>Start building this subject by adding your first chapter.</p>
            <button v-if="!searchQuery" class="btn-primary" @click="openCreateModal">Add Chapter</button>
        </div>

        <div v-else class="chapters-grid">
            <div v-for="chapter in filteredChapters" :key="chapter.id" class="chapter-card"
                @click="goToQuizzes(chapter.id)">
                <div class="card-header" :style="{ background: getGradient(chapter.id) }">
                    <div class="card-options" @click.stop>
                        <button class="options-btn" @click="toggleMenu(chapter.id)">⋮</button>
                        <div v-if="activeMenu === chapter.id" class="dropdown-menu" v-click-outside="closeMenu">
                            <button @click="openEditModal(chapter)">Edit Title</button>
                            <button class="delete" @click="confirmDelete(chapter)">Delete</button>
                        </div>
                    </div>
                    <div class="chapter-number">
                        <span>{{ chapter.name.charAt(0).toUpperCase() }}</span>
                    </div>
                </div>

                <div class="card-body">
                    <h3>{{ chapter.name }}</h3>
                    <p>{{ chapter.description || 'No description provided.' }}</p>
                </div>

                <div class="card-footer">
                    <div class="footer-stats">
                        <span class="quiz-count">{{ chapter.quiz_count || 0 }} Quizzes</span>
                    </div>
                    <button class="btn-view">
                        View Quizzes →
                    </button>
                </div>
            </div>
        </div>

        <!-- Create/Edit Modal -->
        <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h2>{{ isEditing ? 'Edit Chapter' : 'Add New Chapter' }}</h2>
                    <button class="close-btn" @click="closeModal">×</button>
                </div>
                <form @submit.prevent="handleSubmit">
                    <div class="form-group">
                        <label>Chapter Name</label>
                        <input v-model="form.name" type="text" required placeholder="e.g. Algebra Basics"
                            class="modern-input">
                    </div>
                    <div class="form-group">
                        <label>Description (Optional)</label>
                        <textarea v-model="form.description" placeholder="Topics covered in this chapter..."
                            class="modern-textarea"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-ghost" @click="closeModal">Cancel</button>
                        <button type="submit" class="btn-primary" :disabled="submitting">
                            {{ submitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Chapter') }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const subjectId = route.params.id
const subject = ref(null)
const chapters = ref([])
const loading = ref(true)
const searchQuery = ref('')
const activeMenu = ref(null)

// Modal State
const showModal = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const currentId = ref(null)
const form = ref({ name: '', description: '' })

const filteredChapters = computed(() => {
    if (!searchQuery.value) return chapters.value
    const lower = searchQuery.value.toLowerCase()
    return chapters.value.filter(c =>
        c.name.toLowerCase().includes(lower) ||
        (c.description && c.description.toLowerCase().includes(lower))
    )
})

const totalQuizzes = computed(() => {
    return chapters.value.reduce((acc, curr) => acc + (curr.quiz_count || 0), 0)
})

const fetchDetails = async () => {
    loading.value = true
    try {
        const subRes = await api.get(`/subjects/getsubject/${subjectId}`)
        subject.value = subRes.data.subject

        const chapRes = await api.get('/chapters/getchapters')
        chapters.value = chapRes.data.chapters.filter(c => c.subject_id == subjectId)
    } catch (error) {
        console.error("Failed to fetch details", error)
    } finally {
        loading.value = false
    }
}

const getGradient = (id) => {
    // Different palette than subjects to distinguish hierarchy
    const gradients = [
        'linear-gradient(135deg, #f97316, #fb923c)', // Orange
        'linear-gradient(135deg, #06b6d4, #22d3ee)', // Cyan
        'linear-gradient(135deg, #8b5cf6, #a78bfa)', // Violet
        'linear-gradient(135deg, #14b8a6, #2dd4bf)', // Teal
        'linear-gradient(135deg, #f43f5e, #fb7185)'  // Rose
    ]
    return gradients[id % gradients.length]
}

const toggleMenu = (id) => {
    activeMenu.value = activeMenu.value === id ? null : id
}

const closeMenu = () => {
    activeMenu.value = null
}

const vClickOutside = {
    mounted(el, binding) {
        el.clickOutsideEvent = (event) => {
            if (!(el === event.target || el.contains(event.target))) {
                binding.value(event)
            }
        }
        document.body.addEventListener('click', el.clickOutsideEvent)
    },
    unmounted(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent)
    }
}

const openCreateModal = () => {
    isEditing.value = false
    currentId.value = null
    form.value = { name: '', description: '' }
    showModal.value = true
}

const openEditModal = (chapter) => {
    isEditing.value = true
    currentId.value = chapter.id
    form.value = { name: chapter.name, description: chapter.description }
    showModal.value = true
    closeMenu()
}

const closeModal = () => {
    showModal.value = false
}

const handleSubmit = async () => {
    submitting.value = true
    try {
        if (isEditing.value) {
            await api.put(`/chapters/updatechapter/${currentId.value}`, {
                chapter_name: form.value.name,
                description: form.value.description
            })
        } else {
            await api.post('/chapters/createchapter', {
                chapter_name: form.value.name,
                description: form.value.description,
                subject_id: subjectId
            })
        }
        await fetchDetails()
        closeModal()
    } catch (error) {
        alert(error.response?.data?.message || 'Operation failed')
    } finally {
        submitting.value = false
    }
}

const confirmDelete = async (chapter) => {
    if (!confirm(`Are you sure you want to delete "${chapter.name}"?`)) return

    try {
        await api.delete(`/chapters/deletechapter/${chapter.id}`)
        fetchDetails()
    } catch (error) {
        alert(error.response?.data?.message || 'Delete failed')
    }
    closeMenu()
}

const goToQuizzes = (chapterId) => {
    router.push(`/dashboard/subjects/${subjectId}/chapters/${chapterId}/quizzes`)
}

onMounted(() => {
    fetchDetails()
})
</script>

<style scoped>
.subject-detail-container {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

/* Header Styles */
.page-header {
    margin-bottom: 2.5rem;
}

.breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.breadcrumb-item {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color 0.2s;
}

.breadcrumb-item:hover {
    color: var(--primary-color);
}

.separator {
    color: var(--border-color);
}

.current {
    color: var(--text-primary);
    font-weight: 500;
}

.header-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.header-info h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
}

.header-info p {
    color: var(--text-secondary);
    margin: 0 0 1rem 0;
    max-width: 600px;
}

.stats-row {
    display: flex;
    gap: 0.75rem;
}

.stat-badge {
    background: rgba(99, 102, 241, 0.1);
    color: var(--primary-color);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.stat-badge.secondary {
    background: var(--bg-accent);
    color: var(--text-secondary);
}

.header-actions {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.search-wrapper {
    position: relative;
    width: 250px;
}

.search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.search-input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 0.95rem;
    transition: all 0.2s;
}

.search-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn-primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary:hover {
    background: var(--primary-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Grid & Cards */
.chapters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
}

.chapter-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    min-height: 200px;
    cursor: pointer;
}

.chapter-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.card-header {
    height: 80px;
    position: relative;
    padding: 1rem;
    display: flex;
    justify-content: flex-end;
}

.card-options {
    position: relative;
    z-index: 10;
}

.options-btn {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}

.options-btn:hover {
    background: rgba(255, 255, 255, 0.4);
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    min-width: 120px;
    overflow: hidden;
    margin-top: 0.5rem;
    z-index: 20;
}

.dropdown-menu button {
    display: block;
    width: 100%;
    text-align: left;
    padding: 0.75rem 1rem;
    background: transparent;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    font-size: 0.9rem;
}

.dropdown-menu button:hover {
    background: var(--bg-accent);
}

.dropdown-menu button.delete {
    color: #ef4444;
}

.chapter-number {
    position: absolute;
    bottom: -24px;
    left: 1.5rem;
    background: var(--bg-secondary);
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.2rem;
    color: var(--text-primary);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.card-body {
    padding: 2.5rem 1.5rem 1.5rem;
    flex: 1;
}

.card-body h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
    color: var(--text-primary);
}

.card-body p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.5;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.card-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-accent);
}

.quiz-count {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.btn-view {
    background: transparent;
    border: none;
    color: var(--primary-color);
    font-weight: 600;
    cursor: pointer;
    font-size: 0.9rem;
    padding: 0;
}

.btn-view:hover {
    text-decoration: underline;
}

/* Skeleton & Empty States */
.skeleton-card {
    height: 200px;
    background: var(--bg-secondary);
    border-radius: 20px;
    border: 1px solid var(--border-color);
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        opacity: 1;
    }

    50% {
        opacity: 0.5;
    }

    100% {
        opacity: 1;
    }
}

.empty-state {
    text-align: center;
    padding: 4rem 1rem;
    background: var(--bg-secondary);
    border-radius: 24px;
    border: 2px dashed var(--border-color);
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

/* Modal Styles */
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    backdrop-filter: blur(4px);
}

.modal-card {
    background: var(--bg-secondary);
    width: 100%;
    max-width: 500px;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        transform: translateY(20px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.modal-header h2 {
    margin: 0;
    font-size: 1.5rem;
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: var(--text-secondary);
    cursor: pointer;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-secondary);
}

.modern-input,
.modern-textarea {
    width: 100%;
    padding: 0.875rem 1rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 1rem;
    transition: all 0.2s;
}

.modern-textarea {
    min-height: 100px;
    resize: vertical;
}

.modern-input:focus,
.modern-textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
}

.btn-ghost {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-weight: 500;
    padding: 0.75rem 1.5rem;
}
</style>

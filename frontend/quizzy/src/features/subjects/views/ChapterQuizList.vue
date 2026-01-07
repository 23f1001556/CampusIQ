<template>
    <div class="chapter-quiz-list">
        <!-- Header -->
        <div class="page-header">
            <div class="breadcrumb">
                <router-link :to="`/dashboard/subjects/${subjectId}`" class="breadcrumb-item">← Back to
                    Chapter</router-link>
            </div>
            <div class="header-main">
                <div class="header-info">
                    <h1>{{ chapterName || 'Chapter Quizzes' }}</h1>
                    <div class="stats-row">
                        <span class="stat-badge">{{ quizzes.length }} Quizzes</span>
                    </div>
                </div>
                <div class="header-actions">
                    <!-- Creation buttons removed -->
                </div>
            </div>
        </div>

        <div class="tabs">
            <button :class="{ active: activeTab === 'quizzes' }" @click="activeTab = 'quizzes'">Quizzes</button>
            <button :class="{ active: activeTab === 'materials' }" @click="activeTab = 'materials'">Study
                Materials</button>
        </div>

        <div v-if="activeTab === 'quizzes'">
            <div v-if="loading" class="quizzes-grid">
                <div v-for="n in 3" :key="n" class="skeleton-card"></div>
            </div>

            <div v-else class="quizzes-grid">
                <div v-if="quizzes.length === 0" class="empty-state">
                    <div class="empty-icon">📝</div>
                    <h3>No quizzes yet</h3>
                    <p>Go to AI Hub to generate new quizzes for this chapter.</p>
                </div>

                <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-card">
                    <div class="card-header" :style="{ background: getGradient(quiz.id) }">
                        <div class="card-options" @click.stop>
                            <button class="options-btn" @click="toggleMenu(quiz.id)">⋮</button>
                            <div v-if="activeMenu === quiz.id" class="dropdown-menu" v-click-outside="closeMenu">
                                <button @click="openEditModal(quiz)">Edit Quiz</button>
                                <button @click="openPublishModal(quiz)" v-if="isAdmin && !quiz.is_published">Publish
                                    Quiz</button>
                                <button @click="confirmUnpublish(quiz)"
                                    v-if="isAdmin && quiz.is_published">Unpublish</button>
                                <button @click="releaseResults(quiz)"
                                    v-if="isAdmin && quiz.is_published && !quiz.scores_released">Release
                                    Results</button>
                                <button class="delete" @click="confirmDelete(quiz)">Delete</button>
                            </div>
                        </div>
                        <div class="quiz-icon">📝</div>
                    </div>

                    <div class="card-body">
                        <h3>{{ quiz.name }}</h3>
                        <p>{{ quiz.remarks || 'No description provided.' }}</p>

                        <div class="quiz-meta-grid">
                            <div class="meta-item">
                                <span class="label">Questions</span>
                                <span class="value">{{ quiz.question_count || 0 }}</span>
                            </div>
                            <div class="meta-item">
                                <span class="label">Duration</span>
                                <span class="value">{{ quiz.time_duration }} mins</span>
                            </div>
                            <div class="meta-item">
                                <span class="label">Attempts</span>
                                <span class="value">{{ quiz.attempt_count || 0 }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="card-footer">
                        <div v-if="quiz.attempt_count > 0" class="action-buttons">
                            <button class="btn-outline" @click="$router.push(`/dashboard/quiz/${quiz.id}/attempt`)">
                                Attempt Again
                            </button>
                            <button class="btn-primary" @click="evaluateResult(quiz)">
                                Result
                            </button>
                        </div>
                        <button v-else class="btn-primary full-width"
                            @click="$router.push(`/dashboard/quiz/${quiz.id}/attempt`)">
                            Start Quiz
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="materials-view">
            <div class="search-bar-container">
                <input v-model="searchQuery" type="text" placeholder="Search saved materials..." class="search-input">
                <select v-model="selectedQuizFilter" class="search-select">
                    <option value="">All Quizzes</option>
                    <option v-for="name in uniqueQuizNames" :key="name" :value="name">{{ name }}</option>
                </select>
            </div>

            <div v-if="filteredMaterials.length === 0" class="empty-state">
                <div class="empty-icon">📚</div>
                <h3>No study materials found</h3>
                <p>Try a different search term or generate new guides.</p>
            </div>
            <div v-else class="materials-list">
                <div v-for="mat in filteredMaterials" :key="mat.id" class="mat-card">
                    <div class="mat-header" @click="toggleMaterial(mat.id)">
                        <div class="mat-title-group">
                            <h4>{{ mat.title }}</h4>
                            <span class="mat-quiz-ref" v-if="mat.quiz_name">Based on: {{ mat.quiz_name }}</span>
                        </div>
                        <div class="mat-actions-row">
                            <span class="mat-date">{{ mat.created_at }}</span>
                            <button class="delete-icon" @click.stop="confirmDeleteMaterial(mat)">🗑️</button>
                        </div>
                    </div>
                    <div v-if="currMatId === mat.id" class="mat-content markdown-body">
                        {{ mat.content }}
                    </div>
                </div>
            </div>
        </div>

        <!-- Create/Edit Quiz Modal -->
        <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h3>{{ isEditing ? 'Edit Quiz' : 'Add New Quiz' }}</h3>
                    <button class="close-btn" @click="closeModal">×</button>
                </div>
                <form @submit.prevent="handleSubmit">
                    <div class="form-group">
                        <label>Quiz Name</label>
                        <input v-model="form.name" type="text" required placeholder="e.g. Algebra Basics"
                            class="modern-input">
                    </div>
                    <div class="form-group">
                        <label>Duration (Minutes)</label>
                        <input v-model="form.time_duration" type="number" required placeholder="e.g. 15"
                            class="modern-input">
                    </div>
                    <div class="form-group">
                        <label>Remarks (Optional)</label>
                        <textarea v-model="form.remarks" placeholder="Notes..." class="modern-textarea"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-text" @click="closeModal">Cancel</button>
                        <button type="submit" class="btn-primary" :disabled="submitting">
                            {{ submitting ? 'Saving...' : (isEditing ? 'Update' : 'Create') }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- AI Generation Modal -->
        <div v-if="showAIModal" class="modal-backdrop" @click.self="closeAIModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h3>Generate Quiz with AI</h3>
                    <button class="close-btn" @click="closeAIModal">×</button>
                </div>
                <form @submit.prevent="handleGenerate">
                    <div class="form-group">
                        <label>Topic</label>
                        <input v-model="aiForm.topic" type="text" required placeholder="e.g. Calculus Derivatives"
                            class="modern-input">
                    </div>
                    <div class="form-group">
                        <label>Number of Questions</label>
                        <input v-model="aiForm.count" type="number" min="1" max="20" required class="modern-input">
                    </div>

                    <div v-if="aiLoading" class="ai-status">
                        <div class="spinner"></div>
                        <p>Generating questions... This may take a moment.</p>
                    </div>

                    <div class="modal-footer" v-if="!aiLoading">
                        <button type="button" class="btn-text" @click="closeAIModal">Cancel</button>
                        <button type="submit" class="btn-primary">Generate & Save</button>
                    </div>
                </form>
            </div>
        </div>
        <!-- Warning Modal -->
        <div v-if="showWarningModal" class="modal-backdrop" @click.self="closeWarningModal">
            <div class="modal-card warning-card">
                <div class="warning-icon">⚠️</div>
                <h3>Ready to start?</h3>
                <p>Once started, you cannot go back. You must submit the quiz to exit.</p>
                <div class="modal-footer center-footer">
                    <button class="btn-text" @click="closeWarningModal">Cancel</button>
                    <button class="btn-primary" @click="confirmStartQuiz">Start Quiz</button>
                </div>
            </div>
        </div>
        <!-- Publish Modal -->
        <div v-if="showPublishModal" class="modal-backdrop" @click.self="closePublishModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h3>Publish Quiz</h3>
                    <button class="close-btn" @click="closePublishModal">×</button>
                </div>
                <form @submit.prevent="handlePublish">
                    <p class="modal-desc">Set the time window for this quiz to be live in "Mock Quizzes".</p>

                    <div class="form-group">
                        <label>Start Time</label>
                        <input v-model="publishForm.start_time" type="datetime-local" required class="modern-input">
                    </div>

                    <div class="form-group">
                        <label>End Time</label>
                        <input v-model="publishForm.end_time" type="datetime-local" required class="modern-input">
                    </div>

                    <div class="modal-footer">
                        <button type="button" class="btn-text" @click="closePublishModal">Cancel</button>
                        <button type="submit" class="btn-primary" :disabled="publishing">
                            {{ publishing ? 'Publishing...' : 'Publish Now' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
        <div v-if="showConfirmModal" class="modal-backdrop" @click.self="closeConfirmModal">
            <div class="modal-card warning-card">
                <div class="warning-icon">⚠️</div>
                <h3>Are you sure?</h3>
                <p>{{ confirmMessage }}</p>

                <div v-if="requiresPassword" class="password-confirm">
                    <input type="password" v-model="confirmPassword" placeholder="Enter your password to confirm"
                        class="modern-input">
                </div>

                <div class="modal-footer center-footer">
                    <button class="btn-text" @click="closeConfirmModal">Cancel</button>
                    <button class="btn-primary" @click="executeConfirmAction" :disabled="processingAction">
                        {{ processingAction ? 'Processing...' : 'Confirm' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const subjectId = route.params.subjectId
const chapterId = route.params.chapterId
const chapterName = ref('')
const quizzes = ref([])
const loading = ref(true)
const activeMenu = ref(null)
const aiLoading = ref(false)
const showAIModal = ref(false)
const aiForm = ref({ topic: '', count: 5 })

// Modal State
const showModal = ref(false)
const showWarningModal = ref(false)
const selectedQuizId = ref(null)
const isEditing = ref(false)
const submitting = ref(false)
const publishing = ref(false)
const showPublishModal = ref(false)
const publishForm = ref({ start_time: '', end_time: '' })
const currentId = ref(null)
const isAdmin = ref(false)
const form = ref({ name: '', time_duration: 10, date_of_quiz: '', remarks: '' })

// Confirmation Modal State
const showConfirmModal = ref(false)
const confirmMessage = ref('')
const confirmAction = ref(null)
const processingAction = ref(false)


const activeTab = ref('quizzes')
const materials = ref([])
const currMatId = ref(null)
const searchQuery = ref('')
const selectedQuizFilter = ref('')

import { computed } from 'vue'

const uniqueQuizNames = computed(() => {
    const names = new Set(materials.value.map(m => m.quiz_name).filter(Boolean))
    return Array.from(names)
})

const filteredMaterials = computed(() => {
    let result = materials.value

    if (selectedQuizFilter.value) {
        result = result.filter(m => m.quiz_name === selectedQuizFilter.value)
    }

    if (searchQuery.value) {
        const lower = searchQuery.value.toLowerCase()
        result = result.filter(m =>
            m.title.toLowerCase().includes(lower) ||
            (m.quiz_name && m.quiz_name.toLowerCase().includes(lower))
        )
    }

    return result
})

// Secure Delete Logic
const requiresPassword = ref(false)
const confirmPassword = ref('')

const confirmDeleteMaterial = (mat) => {
    confirmMessage.value = `Delete study material "${mat.title}"? This action cannot be undone.`
    requiresPassword.value = true
    confirmPassword.value = ''

    confirmAction.value = async () => {
        if (!confirmPassword.value) {
            alert("Password is required")
            return
        }
        await api.delete(`/ai/delete_study_material/${mat.id}`, {
            data: { password: confirmPassword.value } // Send password in body
        })
        fetchMaterials()
    }
    showConfirmModal.value = true
}

const fetchMaterials = async () => {
    try {
        const res = await api.get(`/ai/get_study_materials?chapter_id=${chapterId}`)
        materials.value = res.data.materials
    } catch (e) {
        console.error("Failed to fetch materials", e)
    }
}

const toggleMaterial = (id) => {
    currMatId.value = currMatId.value === id ? null : id
}

const fetchQuizzes = async () => {
    loading.value = true
    try {
        await Promise.all([
            api.get(`/quiz/getquizzes?chapter_id=${chapterId}`).then(res => {
                quizzes.value = res.data.quizzes
            }),
            fetchMaterials()
        ])
    } catch (error) {
        console.error("Failed to fetch data", error)
    } finally {
        loading.value = false
    }
}

const fetchChapterDetails = async () => {
    try {
        const chapRes = await api.get('/chapters/getchapters')
        const chap = chapRes.data.chapters.find(c => c.id == chapterId)
        if (chap) chapterName.value = chap.name
    } catch (e) {
        console.error("Failed to fetch chapter name", e)
    }
}

const getGradient = (id) => {
    const gradients = [
        'linear-gradient(135deg, #3b82f6, #60a5fa)',
        'linear-gradient(135deg, #10b981, #34d399)',
        'linear-gradient(135deg, #f59e0b, #fbbf24)',
        'linear-gradient(135deg, #ec4899, #f472b6)',
        'linear-gradient(135deg, #6366f1, #818cf8)'
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
    form.value = { name: '', time_duration: 10, date_of_quiz: '', remarks: '' }
    showModal.value = true
}

const openEditModal = (quiz) => {
    isEditing.value = true
    currentId.value = quiz.id
    form.value = {
        name: quiz.name,
        time_duration: quiz.time_duration,
        date_of_quiz: quiz.date_of_quiz || '',
        remarks: quiz.remarks
    }
    showModal.value = true
    closeMenu()
}

const closeModal = () => {
    showModal.value = false
}

const openAIModal = () => {
    aiForm.value = { topic: '', count: 5 }
    showAIModal.value = true
}

const closeAIModal = () => {
    showAIModal.value = false
}

const handleSubmit = async () => {
    submitting.value = true
    try {
        const payload = {
            name: form.value.name,
            time_duration: parseInt(form.value.time_duration),
            remarks: form.value.remarks,
            chapter_id: chapterId,
            ...(form.value.date_of_quiz ? { date_of_quiz: form.value.date_of_quiz } : {})
        }

        if (isEditing.value) {
            await api.put(`/quiz/updatequiz/${currentId.value}`, payload)
        } else {
            await api.post('/quiz/createquiz', payload)
        }
        await fetchQuizzes()
        closeModal()
    } catch (error) {
        alert(error.response?.data?.message || 'Operation failed')
    } finally {
        submitting.value = false
    }
}



const initiateStartQuiz = (quiz) => {
    selectedQuizId.value = quiz.id
    showWarningModal.value = true
}

const closeWarningModal = () => {
    showWarningModal.value = false
    selectedQuizId.value = null
}

const confirmStartQuiz = () => {
    if (selectedQuizId.value) {
        router.push(`/dashboard/quiz/${selectedQuizId.value}/attempt`)
    }
    closeWarningModal()
}

const confirmDelete = (quiz) => {
    confirmMessage.value = `Are you sure you want to delete "${quiz.name}"?`
    confirmAction.value = async () => {
        await api.delete(`/quiz/deletequiz/${quiz.id}`)
        fetchQuizzes()
    }
    showConfirmModal.value = true
    closeMenu()
}

const openPublishModal = (quiz) => {
    currentId.value = quiz.id
    // Set default times (Now to Now+1hr)
    const now = new Date()
    const oneHour = new Date(now.getTime() + 60 * 60 * 1000)

    // Format for datetime-local: YYYY-MM-DDTHH:MM
    // Note: ISOString is UTC, we might want local time for input.
    // Simple trick for local ISO string:
    const toLocalISO = (d) => {
        const offset = d.getTimezoneOffset() * 60000
        return new Date(d.getTime() - offset).toISOString().slice(0, 16)
    }

    publishForm.value = {
        start_time: toLocalISO(now),
        end_time: toLocalISO(oneHour)
    }
    showPublishModal.value = true
    closeMenu()
}

const closePublishModal = () => {
    showPublishModal.value = false
}

const handlePublish = async () => {
    publishing.value = true
    try {
        await api.post(`/quiz/publish_quiz/${currentId.value}`, {
            start_time: new Date(publishForm.value.start_time).toISOString(),
            end_time: new Date(publishForm.value.end_time).toISOString()
        })
        alert("Quiz published successfully!")
        closePublishModal()
        await fetchQuizzes()
    } catch (error) {
        alert(error.response?.data?.message || 'Publish failed')
    } finally {
        publishing.value = false
    }
}

const confirmUnpublish = (quiz) => {
    confirmMessage.value = `Are you sure you want to unpublish "${quiz.name}"? This will hide it from users.`
    confirmAction.value = async () => {
        await api.post(`/quiz/publish_quiz/${quiz.id}`, {
            is_published: false
        })
        fetchQuizzes()
    }
    showConfirmModal.value = true
    closeMenu()
}

const releaseResults = (quiz) => {
    confirmMessage.value = `Release results for "${quiz.name}"? Scores will be visible to all users.`
    confirmAction.value = async () => {
        await api.post(`/quiz/release_results/${quiz.id}`)
        fetchQuizzes()
    }
    showConfirmModal.value = true
    closeMenu()
}

const closeConfirmModal = () => {
    showConfirmModal.value = false
    confirmAction.value = null
    requiresPassword.value = false
    confirmPassword.value = ''
}

const executeConfirmAction = async () => {
    if (!confirmAction.value) return

    processingAction.value = true
    try {
        await confirmAction.value()
        closeConfirmModal()
    } catch (error) {
        // Log error instead of alert
        console.error(error)
    } finally {
        processingAction.value = false
    }
}

onMounted(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    isAdmin.value = !!user.isadmin
    fetchQuizzes()
    fetchChapterDetails()
})
</script>

<style scoped>
.chapter-quiz-list {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

/* Tabs */
.tabs {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
}

.tabs button {
    background: transparent;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-secondary);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
}

.tabs button.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

.tabs button:hover:not(.active) {
    color: var(--text-primary);
}

/* Materials */
.search-bar-container {
    margin-bottom: 2rem;
    display: flex;
    gap: 1rem;
}

.search-input {
    width: 100%;
    padding: 1rem;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    border-radius: 12px;
    color: var(--text-primary);
    font-size: 1rem;
    outline: none;
    transition: all 0.2s;
}

.search-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-select {
    padding: 1rem;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    border-radius: 12px;
    color: var(--text-primary);
    font-size: 1rem;
    outline: none;
    min-width: 200px;
    cursor: pointer;
}

.search-select:focus {
    border-color: var(--primary-color);
}

.materials-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.mat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
}

.mat-header {
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    background: rgba(79, 70, 229, 0.05);
}

.mat-header:hover {
    background: rgba(79, 70, 229, 0.1);
}

.mat-title-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.mat-title-group h4 {
    margin: 0;
    color: var(--text-primary);
}

.mat-quiz-ref {
    font-size: 0.8rem;
    color: var(--primary-color);
    font-weight: 500;
}

.mat-actions-row {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.mat-date {
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.delete-icon {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 1.1rem;
    padding: 0.25rem;
    border-radius: 50%;
    transition: background 0.2s;
}

.delete-icon:hover {
    background: rgba(239, 68, 68, 0.1);
}

.mat-content {
    padding: 1.5rem;
    border-top: 1px solid var(--border-color);
    white-space: pre-wrap;
    line-height: 1.6;
}

.password-confirm {
    margin: 1.5rem 0;
}

/* Header */
.page-header {
    margin-bottom: 2.5rem;
}

.breadcrumb-item {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    display: inline-block;
}

.breadcrumb-item:hover {
    color: var(--primary-color);
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

.stat-badge {
    background: rgba(99, 102, 241, 0.1);
    color: var(--primary-color);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.header-actions {
    display: flex;
    gap: 1rem;
}

.btn-primary {
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

.btn-secondary {
    background: var(--bg-accent);
    color: var(--text-primary);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-secondary:hover {
    background: var(--border-color);
}

/* Grid */
.quizzes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 2rem;
}

.quiz-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    border: 1px solid var(--border-color);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
}

.quiz-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.card-header {
    height: 100px;
    padding: 1.5rem;
    position: relative;
    display: flex;
    justify-content: flex-end;
}

.quiz-icon {
    width: 50px;
    height: 50px;
    background: var(--bg-secondary);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    position: absolute;
    bottom: -25px;
    left: 1.5rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
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

.card-body {
    padding: 2.5rem 1.5rem 1.5rem;
    flex: 1;
}

.card-body h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    color: var(--text-primary);
}

.card-body p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.quiz-meta-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
    background: var(--bg-primary);
    padding: 1rem;
    border-radius: 12px;
}

.meta-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.meta-item .label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}

.meta-item .value {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.9rem;
}

.card-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-color);
    background: var(--bg-accent);
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.btn-outline {
    flex: 1;
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.75rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-outline:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.full-width {
    width: 100%;
}

.btn-primary {
    flex: 1;
}

/* Modal Styles - Reuse or Global Logic */
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

.warning-card {
    text-align: center;
    max-width: 400px;
}

.warning-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}


.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
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
}

.modern-textarea {
    min-height: 100px;
    resize: vertical;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
}

.center-footer {
    justify-content: center;
}


.btn-text {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    font-weight: 500;
    padding: 0.75rem 1.5rem;
}

.ai-status {
    text-align: center;
    padding: 2rem;
}

.spinner {
    border: 3px solid rgba(0, 0, 0, 0.1);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}
</style>

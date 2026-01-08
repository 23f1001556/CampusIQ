<template>
    <div class="course-detail-container">
        <header class="course-header">
            <button @click="$router.push('/dashboard/institute')" class="back-btn">← Back to Courses</button>
            <h1>{{ course.title }}</h1>
            <p class="course-desc">{{ course.description }}</p>
        </header>

        <div class="tabs">
            <button :class="{ active: activeTab === 'papers' }" @click="activeTab = 'papers'">Question Papers</button>
            <button :class="{ active: activeTab === 'lectures' }" @click="activeTab = 'lectures'">Lectures</button>
        </div>

        <div class="tab-content">
            <!-- Papers Section -->
            <div v-if="activeTab === 'papers'" class="materials-list">
                <div v-if="isManager" class="add-material">
                    <button @click="openAddModal('paper')" class="add-link">+ Add Question Paper</button>
                </div>
                <div v-if="papers.length === 0" class="empty-hint">No question papers uploaded yet.</div>
                <div v-for="paper in papers" :key="paper.id" class="material-card">
                    <div class="material-info">
                        <div class="title-row">
                            <h4>{{ paper.title }}</h4>
                            <div class="badges">
                                <span v-if="paper.file_path" class="badge pdf">📄 PDF</span>
                                <span v-if="paper.link_url" class="badge link">🔗 Link</span>
                                <span v-if="paper.content" class="badge note">📝 Note</span>
                            </div>
                        </div>
                        <div class="material-actions">
                            <button @click="viewContent(paper, 'paper')" class="btn-sm">View Item</button>
                            <button v-if="paper.file_path" @click="openFile(paper.file_path)" class="btn-sm">Open
                                PDF</button>
                            <button v-if="paper.link_url" @click="openLink(paper.link_url)" class="btn-sm">Open
                                Link</button>

                            <template v-if="isManager">
                                <button @click="openEditModal(paper, 'paper')" class="btn-sm edit-btn">✏️
                                    Rename</button>
                                <button @click="deleteItem(paper.id, 'paper')" class="btn-sm delete-btn">🗑️
                                    Delete</button>
                            </template>

                            <div class="ai-group">
                                <button @click="aiAction(paper, 'paper', 'summarize')" class="btn-sm ai-btn"
                                    :disabled="aiLoading">Summarize</button>
                                <button @click="aiAction(paper, 'paper', 'generate-quiz')" class="btn-sm ai-btn"
                                    :disabled="aiLoading">Gen
                                    Quiz</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Lectures Section -->
            <div v-if="activeTab === 'lectures'" class="materials-list">
                <div v-if="isManager" class="add-material">
                    <button @click="openAddModal('lecture')" class="add-link">+ Add Lecture</button>
                </div>
                <div v-if="lectures.length === 0" class="empty-hint">No lectures uploaded yet.</div>
                <div v-for="lecture in lectures" :key="lecture.id" class="material-card">
                    <div class="material-info">
                        <div class="title-row">
                            <h4>{{ lecture.title }}</h4>
                            <div class="badges">
                                <span v-if="lecture.file_path" class="badge pdf">📄 PDF</span>
                                <span v-if="lecture.video_url" class="badge video">📺 Video</span>
                                <span v-if="lecture.link_url" class="badge link">🔗 Link</span>
                                <span v-if="lecture.content" class="badge note">📝 Note</span>
                            </div>
                        </div>
                        <div class="material-actions">
                            <button @click="viewContent(lecture, 'lecture')" class="btn-sm">View Notes</button>
                            <button v-if="lecture.file_path" @click="openFile(lecture.file_path)" class="btn-sm">Open
                                PDF</button>
                            <button v-if="lecture.video_url" @click="openLink(lecture.video_url)" class="btn-sm">Watch
                                Video</button>
                            <button v-if="lecture.link_url" @click="openLink(lecture.link_url)" class="btn-sm">Open
                                Link</button>

                            <template v-if="isManager">
                                <button @click="openEditModal(lecture, 'lecture')" class="btn-sm edit-btn">✏️
                                    Rename</button>
                                <button @click="deleteItem(lecture.id, 'lecture')" class="btn-sm delete-btn">🗑️
                                    Delete</button>
                            </template>

                            <div class="ai-group">
                                <button @click="aiAction(lecture, 'lecture', 'summarize')" class="btn-sm ai-btn"
                                    :disabled="aiLoading">Summarize</button>
                                <button @click="aiAction(lecture, 'lecture', 'generate-quiz')" class="btn-sm ai-btn"
                                    :disabled="aiLoading">Gen Quiz</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Material Modal -->
        <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
            <div class="modal-content">
                <h2>Add {{ modalType === 'paper' ? 'Question Paper' : 'Lecture' }}</h2>
                <form @submit.prevent="handleAddMaterial">
                    <div class="form-group">
                        <label>Title</label>
                        <input v-model="newItem.title" type="text" placeholder="Enter title" required />
                    </div>
                    <div class="form-group">
                        <label>PDF File (Optional)</label>
                        <input type="file" @change="handleFileUpload" accept="application/pdf" class="file-input" />
                    </div>
                    <div class="form-group">
                        <label>Accompanying Text / Description</label>
                        <textarea v-model="newItem.content" placeholder="Paste text or add details..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>External Link / URL (Optional)</label>
                        <input v-model="newItem.link_url" type="url" placeholder="https://..." />
                    </div>
                    <div v-if="modalType === 'lecture'" class="form-group">
                        <label>Video URL (Optional)</label>
                        <input v-model="newItem.video_url" type="url" placeholder="YouTube link..." />
                    </div>
                    <div class="modal-actions">
                        <button type="button" @click="showAddModal = false" class="secondary-btn">Cancel</button>
                        <button type="submit" class="primary-btn" :disabled="submitting">
                            {{ submitting ? 'Uploading...' : 'Upload & Save' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Edit/Rename Modal -->
        <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
            <div class="modal-content">
                <h2>Edit Material</h2>
                <form @submit.prevent="handleEditMaterial">
                    <div class="form-group">
                        <label>Title</label>
                        <input v-model="editItem.title" type="text" required />
                    </div>
                    <div class="form-group">
                        <label>Text Content</label>
                        <textarea v-model="editItem.content"></textarea>
                    </div>
                    <div class="form-group">
                        <label>External Link</label>
                        <input v-model="editItem.link_url" type="url" />
                    </div>
                    <div v-if="editType === 'lecture'" class="form-group">
                        <label>Video URL</label>
                        <input v-model="editItem.video_url" type="url" />
                    </div>
                    <div class="modal-actions">
                        <button type="button" @click="showEditModal = false" class="secondary-btn">Cancel</button>
                        <button type="submit" class="primary-btn">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- AI Result Modal -->
        <div v-if="showAIResult" class="modal-overlay" @click.self="showAIResult = false">
            <div class="modal-content ai-modal">
                <div class="modal-header">
                    <h3>AI {{ aiResultType === 'summary' ? 'Summary' : 'Quiz' }}</h3>
                    <button @click="showAIResult = false" class="close-btn">✕</button>
                </div>
                <div class="ai-text-area">
                    <pre>{{ aiResult }}</pre>
                </div>
                <div class="modal-actions">
                    <button @click="showAIResult = false" class="primary-btn">Close</button>
                </div>
            </div>
        </div>

        <!-- Content Viewer Modal -->
        <div v-if="showViewer" class="modal-overlay" @click.self="showViewer = false">
            <div class="modal-content large-modal">
                <div class="modal-header">
                    <h2>{{ viewerTitle }}</h2>
                    <button @click="showViewer = false" class="close-btn">✕</button>
                </div>
                <div class="content-body">
                    <p class="content-text">{{ viewerContent }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../../services/api'

const route = useRoute()
const courseId = route.params.id
const course = ref({})
const papers = ref([])
const lectures = ref([])
const activeTab = ref('papers')
const loading = ref(true)
const submitting = ref(false)

// Modals
const showAddModal = ref(false)
const modalType = ref('paper')
const newItem = ref({ title: '', content: '', video_url: '', link_url: '' })
const selectedFile = ref(null)

const showEditModal = ref(false)
const editType = ref('paper')
const editItem = ref({})

const showAIResult = ref(false)
const aiResult = ref('')
const aiResultType = ref('summary')
const aiLoading = ref(false)

const showViewer = ref(false)
const viewerTitle = ref('')
const viewerContent = ref('')

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isManager = computed(() => user.role === 'manager' || user.role === 'admin')

const fetchData = async () => {
    try {
        loading.value = true
        const coursesRes = await api.get('/institute/courses')
        course.value = coursesRes.data.find(c => c.id == courseId) || {}
        const materialsRes = await api.get(`/institute/courses/${courseId}/materials`)
        papers.value = materialsRes.data.papers
        lectures.value = materialsRes.data.lectures
    } catch (error) {
        console.error('Failed to fetch materials')
    } finally {
        loading.value = false
    }
}

const openAddModal = (type) => {
    modalType.value = type
    newItem.value = { title: '', content: '', video_url: '', link_url: '' }
    selectedFile.value = null
    showAddModal.value = true
}

const handleFileUpload = (e) => {
    selectedFile.value = e.target.files[0]
}

const handleAddMaterial = async () => {
    try {
        submitting.value = true
        const formData = new FormData()
        formData.append('title', newItem.value.title)
        formData.append('content', newItem.value.content)
        formData.append('link_url', newItem.value.link_url)
        if (newItem.value.video_url) formData.append('video_url', newItem.value.video_url)
        if (selectedFile.value) formData.append('file', selectedFile.value)

        const endpoint = modalType.value === 'paper' ? `/institute/courses/${courseId}/paper` : `/institute/courses/${courseId}/lecture`
        await api.post(endpoint, formData)
        await fetchData()
        showAddModal.value = false
    } catch (error) {
        alert('Failed to upload material')
    } finally {
        submitting.value = false
    }
}

const openEditModal = (item, type) => {
    editType.value = type
    editItem.value = { ...item }
    showEditModal.value = true
}

const handleEditMaterial = async () => {
    try {
        const endpoint = editType.value === 'paper' ? `/institute/paper/${editItem.value.id}` : `/institute/lecture/${editItem.value.id}`
        await api.put(endpoint, editItem.value)
        await fetchData()
        showEditModal.value = false
    } catch (error) {
        alert('Failed to update material')
    }
}

const deleteItem = async (id, type) => {
    if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        try {
            const endpoint = type === 'paper' ? `/institute/paper/${id}` : `/institute/lecture/${id}`
            await api.delete(endpoint)
            await fetchData()
        } catch (error) {
            alert('Failed to delete item')
        }
    }
}

const aiAction = async (item, type, action) => {
    try {
        aiLoading.value = true
        const endpoint = action === 'summarize' ? '/institute/ai/summarize' : '/institute/ai/generate-quiz'
        const response = await api.post(endpoint, {
            id: item.id,
            type: type,
            title: item.title
        })
        aiResult.value = action === 'summarize' ? response.data.summary : response.data.quiz
        aiResultType.value = action === 'summarize' ? 'summary' : 'quiz'
        showAIResult.value = true
    } catch (error) {
        alert('AI processing failed')
    } finally {
        aiLoading.value = false
    }
}

const viewContent = (item, type) => {
    viewerTitle.value = item.title
    viewerContent.value = item.content || 'No text content available for this item.'
    showViewer.value = true
}

const openFile = (path) => {
    const baseUrl = api.defaults.baseURL.replace('/api', '')
    window.open(`${baseUrl}/institute/files/${path.split('/').pop()}`, '_blank')
}

const openLink = (url) => {
    window.open(url, '_blank')
}

onMounted(fetchData)
</script>

<style scoped>
.course-detail-container {
    padding: 2rem;
    max-width: 1100px;
    margin: 0 auto;
}

.course-header {
    margin-bottom: 2rem;
}

.back-btn {
    background: transparent;
    border: none;
    color: var(--primary-color);
    margin-bottom: 1rem;
    cursor: pointer;
    padding: 0;
    font-weight: 500;
}

.course-desc {
    color: var(--text-secondary);
    font-size: 1.1rem;
}

.tabs {
    display: flex;
    gap: 1rem;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 2rem;
}

.tabs button {
    padding: 0.75rem 1.5rem;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    position: relative;
    font-weight: 600;
}

.tabs button.active {
    color: var(--primary-color);
}

.tabs button.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--primary-color);
}

.materials-list {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.add-material {
    margin-bottom: 0.5rem;
}

.add-link {
    color: var(--primary-color);
    background: rgba(99, 102, 241, 0.05);
    border: 2px dashed var(--primary-color);
    padding: 0.75rem;
    border-radius: 12px;
    cursor: pointer;
    width: 100%;
    text-align: center;
    font-weight: 600;
    transition: all 0.2s;
}

.add-link:hover {
    background: rgba(99, 102, 241, 0.1);
}

.material-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    transition: transform 0.2s;
}

.material-card:hover {
    transform: translateX(4px);
    border-color: var(--primary-color);
}

.title-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.title-row h4 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--text-primary);
}

.badges {
    display: flex;
    gap: 0.5rem;
}

.badge {
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
}

.badge.pdf {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

.badge.link {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.badge.note {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.badge.video {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

.material-actions {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    align-items: center;
}

.ai-group {
    display: flex;
    gap: 0.4rem;
    border-left: 1px solid var(--border-color);
    padding-left: 0.6rem;
    margin-left: 0.4rem;
}

.btn-sm {
    padding: 0.45rem 0.9rem;
    font-size: 0.85rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-main);
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s;
}

.btn-sm:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.delete-btn:hover {
    color: var(--danger-color);
    border-color: var(--danger-color);
}

.ai-btn {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    color: white;
    border: none;
    font-weight: 600;
}

.ai-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

/* Modals */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(6px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 2rem;
    width: 90%;
    max-width: 550px;
}

.large-modal {
    max-width: 850px;
    max-height: 85vh;
    overflow-y: auto;
}

.form-group {
    margin-bottom: 1.25rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    background: var(--bg-main);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    color: white;
    font-family: inherit;
}

.file-input {
    padding: 0.5rem 0;
    border: none;
    background: transparent;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
}

.primary-btn {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
}

.secondary-btn {
    background: transparent;
    border: 1px solid var(--border-color);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    cursor: pointer;
}

.content-text {
    line-height: 1.7;
    white-space: pre-wrap;
    color: var(--text-primary);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 1rem;
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: var(--text-secondary);
    cursor: pointer;
}

.ai-text-area pre {
    white-space: pre-wrap;
    background: var(--bg-main);
    padding: 1.5rem;
    border-radius: 16px;
    line-height: 1.6;
    max-height: 450px;
    overflow-y: auto;
    font-family: 'Inter', sans-serif;
}

.empty-hint {
    text-align: center;
    color: var(--text-secondary);
    padding: 3rem;
    font-style: italic;
    opacity: 0.6;
}
</style>

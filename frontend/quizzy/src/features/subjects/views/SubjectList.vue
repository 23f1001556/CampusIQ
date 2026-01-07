<template>
    <div class="subjects-container">
        <!-- Header Section -->
        <div class="page-header">
            <div class="header-text">
                <h1>My Subjects</h1>
                <p>Manage your learning paths and quizzes</p>
            </div>
            <div class="header-actions">
                <div class="search-wrapper">
                    <span class="search-icon">🔍</span>
                    <input v-model="searchQuery" type="text" placeholder="Search subjects..." class="search-input">
                </div>
                <button class="btn-primary" @click="openCreateModal">
                    <span class="btn-icon">+</span> New Subject
                </button>
            </div>
        </div>

        <!-- content -->
        <div v-if="loading" class="subjects-grid">
            <div v-for="n in 6" :key="n" class="skeleton-card"></div>
        </div>

        <div v-else-if="filteredSubjects.length === 0" class="empty-state">
            <div class="empty-icon">📚</div>
            <h3>No subjects found</h3>
            <p v-if="searchQuery">No matches for "{{ searchQuery }}". Try a different term.</p>
            <p v-else>Get started by creating your first subject to organize your quizzes.</p>
            <button v-if="!searchQuery" class="btn-primary" @click="openCreateModal">Create Subject</button>
        </div>

        <div v-else class="subjects-grid">
            <div v-for="subject in filteredSubjects" :key="subject.id" class="subject-card"
                @click="goToSubject(subject.id)">
                <div class="card-header" :style="{ background: getGradient(subject.id) }">
                    <div class="card-options" @click.stop>
                        <button class="options-btn" @click="toggleMenu(subject.id)">⋮</button>
                        <div v-if="activeMenu === subject.id" class="dropdown-menu" v-click-outside="closeMenu">
                            <button @click="openEditModal(subject)">Edit</button>
                            <button class="delete" @click="confirmDelete(subject)">Delete</button>
                        </div>
                    </div>
                    <div class="subject-icon">{{ subject.name.charAt(0) }}</div>
                </div>
                <div class="card-body">
                    <h3>{{ subject.name }}</h3>
                    <p>{{ subject.description || 'No description provided.' }}</p>
                </div>
                <div class="card-footer">
                    <span class="meta-tag">{{ subject.chapter_count }} {{ subject.chapter_count === 1 ? 'Chapter' :
                        'Chapters' }}</span>
                    <span class="arrow-link">View →</span>
                </div>
            </div>
        </div>

        <!-- Create/Edit Modal -->
        <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
            <div class="modal-card">
                <div class="modal-header">
                    <h2>{{ isEditing ? 'Edit Subject' : 'Create Subject' }}</h2>
                    <button class="close-btn" @click="closeModal">×</button>
                </div>
                <form @submit.prevent="handleSubmit">
                    <div class="form-group">
                        <label>Subject Name</label>
                        <input v-model="form.name" type="text" required placeholder="e.g. Mathematics"
                            class="modern-input">
                    </div>
                    <div class="form-group">
                        <label>Description (Optional)</label>
                        <textarea v-model="form.description" placeholder="Briefly describe this subject..."
                            class="modern-textarea"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-ghost" @click="closeModal">Cancel</button>
                        <button type="submit" class="btn-primary" :disabled="submitting">
                            {{ submitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Subject') }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const subjects = ref([])
const loading = ref(true)
const searchQuery = ref('')
const activeMenu = ref(null)

// Modal State
const showModal = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const currentId = ref(null)

const form = ref({
    name: '',
    description: ''
})

const filteredSubjects = computed(() => {
    if (!searchQuery.value) return subjects.value
    const lower = searchQuery.value.toLowerCase()
    return subjects.value.filter(s =>
        s.name.toLowerCase().includes(lower) ||
        (s.description && s.description.toLowerCase().includes(lower))
    )
})

const fetchSubjects = async () => {
    try {
        const res = await api.get('/subjects/getsubjects')
        subjects.value = res.data.subjects
    } catch (error) {
        console.error("Failed to fetch subjects", error)
    } finally {
        loading.value = false
    }
}

const getGradient = (id) => {
    const gradients = [
        'linear-gradient(135deg, #6366f1, #8b5cf6)',
        'linear-gradient(135deg, #3b82f6, #2dd4bf)',
        'linear-gradient(135deg, #ec4899, #f43f5e)',
        'linear-gradient(135deg, #f59e0b, #d97706)',
        'linear-gradient(135deg, #10b981, #059669)'
    ]
    return gradients[id % gradients.length]
}

const toggleMenu = (id) => {
    activeMenu.value = activeMenu.value === id ? null : id
}

const closeMenu = () => {
    activeMenu.value = null
}

// Custom directive for clicking outside dropdown
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

const openEditModal = (subject) => {
    isEditing.value = true
    currentId.value = subject.id
    form.value = { name: subject.name, description: subject.description }
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
            await api.put(`/subjects/updatesubject/${currentId.value}`, {
                subject_name: form.value.name,
                description: form.value.description
            })
        } else {
            await api.post('/subjects/createsubject', {
                subject_name: form.value.name,
                description: form.value.description
            })
        }
        await fetchSubjects()
        closeModal()
    } catch (error) {
        alert(error.response?.data?.message || 'Operation failed')
    } finally {
        submitting.value = false
    }
}

const confirmDelete = async (subject) => {
    if (!confirm(`Are you sure you want to delete "${subject.name}"?`)) return

    try {
        await api.delete(`/subjects/deletesubject/${subject.id}`)
        fetchSubjects()
    } catch (error) {
        alert(error.response?.data?.message || 'Delete failed')
    }
    closeMenu()
}

const goToSubject = (id) => {
    router.push(`/dashboard/subjects/${id}`)
}

onMounted(() => {
    fetchSubjects()
})
</script>

<style scoped>
.subjects-container {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 2.5rem;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.header-text h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
}

.header-text p {
    color: var(--text-secondary);
    margin: 0;
    font-size: 1rem;
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
.subjects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
}

.subject-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    min-height: 200px;
}

.subject-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.card-header {
    height: 100px;
    position: relative;
    padding: 1.5rem;
}

.card-options {
    position: absolute;
    top: 1rem;
    right: 1rem;
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

.subject-icon {
    width: 60px;
    height: 60px;
    background: var(--bg-secondary);
    border-radius: 16px;
    position: absolute;
    bottom: -30px;
    left: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-primary);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    text-transform: uppercase;
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

.meta-tag {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.arrow-link {
    color: var(--primary-color);
    font-size: 0.9rem;
    font-weight: 600;
}

/* Skeleton Loader */
.skeleton-card {
    height: 250px;
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

/* Empty State */
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

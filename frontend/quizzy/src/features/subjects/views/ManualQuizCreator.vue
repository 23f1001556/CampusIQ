<template>
    <div class="manual-quiz-creator">
        <div class="page-header">
            <div class="breadcrumb">
                <router-link :to="`/dashboard/subjects/${subjectId}/chapters/${chapterId}/quizzes`"
                    class="breadcrumb-item">
                    ← Back to Quizzes
                </router-link>
            </div>
            <h1>{{ isEditing ? 'Edit Quiz' : 'Create Manual Quiz' }}</h1>
            <p class="subtitle">{{ isEditing ? 'Modify your quiz questions and settings' : 'Build your custom quiz with multiple choice questions' }}
            </p>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="loader"></div>
            <p>Loading quiz data...</p>
        </div>

        <div v-else class="quiz-form-container">
            <!-- Quiz Metadata Section -->
            <div class="section-card">
                <h2>Quiz Information</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Quiz Name *</label>
                        <input v-model="quizData.name" type="text" placeholder="e.g. Algebra Basics"
                            class="modern-input" required>
                    </div>
                    <div class="form-group">
                        <label>Duration (Minutes) *</label>
                        <input v-model="quizData.time_duration" type="number" min="1" placeholder="e.g. 30"
                            class="modern-input" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Remarks (Optional)</label>
                    <textarea v-model="quizData.remarks" placeholder="Add any notes or instructions..."
                        class="modern-textarea"></textarea>
                </div>
            </div>

            <!-- Questions Section -->
            <div class="section-card">
                <div class="section-header">
                    <h2>Questions ({{ questions.length }})</h2>
                    <button @click="addQuestion" class="btn-add-question">
                        <span class="icon">➕</span> Add Question
                    </button>
                </div>

                <div v-if="questions.length === 0" class="empty-questions">
                    <div class="empty-icon">📝</div>
                    <p>No questions yet. Click "Add Question" to get started.</p>
                </div>

                <div v-else class="questions-list">
                    <div v-for="(question, index) in questions" :key="question.displayId || question.id" class="question-card">
                        <div class="question-header">
                            <span class="question-number">Question {{ index + 1 }}</span>
                            <button @click="removeQuestion(index, question)" class="btn-delete" title="Delete Question">
                                🗑️
                            </button>
                        </div>

                        <div class="form-group">
                            <label>Question Statement *</label>
                            <textarea v-model="question.question_statement" placeholder="Enter your question here..."
                                class="modern-textarea question-input" required></textarea>
                        </div>

                        <div class="options-grid">
                            <div v-for="optionNum in 4" :key="optionNum" class="option-item">
                                <div class="option-header">
                                    <label>Option {{ optionNum }}</label>
                                    <input type="radio" :name="`correct-${question.displayId || question.id}`" :value="optionNum.toString()"
                                        v-model="question.correct_option" class="radio-correct"
                                        title="Mark as correct answer">
                                    <span class="radio-label">Correct</span>
                                </div>
                                <input v-model="question[`option_${optionNum}`]" type="text"
                                    :placeholder="`Option ${optionNum}`" class="modern-input" required>
                            </div>
                        </div>

                        <div v-if="!question.correct_option" class="validation-warning">
                            ⚠️ Please select the correct answer
                        </div>
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="action-buttons">
                <button @click="goBack" class="btn-secondary">Cancel</button>
                <button @click="saveQuiz" class="btn-primary" :disabled="saving || !isValid">
                    {{ saving ? 'Saving...' : (isEditing ? 'Update Quiz' : 'Create Quiz') }}
                </button>
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
const subjectId = route.params.subjectId
const chapterId = route.params.chapterId
const quizId = route.params.quizId
const isEditing = computed(() => !!quizId)

const loading = ref(false)
const saving = ref(false)

const quizData = ref({
    name: '',
    time_duration: 30,
    remarks: ''
})

const questions = ref([])
const deletedQuestions = ref([]) // Track IDs of questions to delete on save
let tempIdCounter = 1

onMounted(async () => {
    if (isEditing.value) {
        await fetchQuizData()
    }
})

const fetchQuizData = async () => {
    loading.value = true
    try {
        // 1. Fetch Quiz Details
        const quizRes = await api.get(`/quiz/getquiz/${quizId}`)
        const quiz = quizRes.data.quiz
        quizData.value = {
            name: quiz.name,
            time_duration: quiz.time_duration,
            remarks: quiz.remarks
        }

        // 2. Fetch Questions (we need full details for editing, getquiz returns simplified structure sometimes, 
        // but let's check if we made a dedicated edit endpoint. 
        // We made /quiz/get_questions/<id> which returns full details including correct option)
        const qRes = await api.get(`/quiz/get_questions/${quizId}`)
        questions.value = qRes.data.questions.map(q => ({
            ...q,
            displayId: `db-${q.id}` // Stable ID for v-for key
        }))

    } catch (error) {
        console.error("Failed to load quiz", error)
        alert("Failed to load quiz data")
        router.push(`/dashboard/subjects/${subjectId}/chapters/${chapterId}/quizzes`)
    } finally {
        loading.value = false
    }
}

const addQuestion = () => {
    questions.value.push({
        displayId: `temp-${tempIdCounter++}`, // Temporary ID for frontend key
        isNew: true,
        question_statement: '',
        option_1: '',
        option_2: '',
        option_3: '',
        option_4: '',
        correct_option: ''
    })
}

const removeQuestion = (index, question) => {
    if (confirm('Are you sure you want to remove this question?')) {
        if (!question.isNew) {
            deletedQuestions.value.push(question.id)
        }
        questions.value.splice(index, 1)
    }
}

const isValid = computed(() => {
    if (!quizData.value.name || !quizData.value.time_duration) return false
    if (questions.value.length === 0) return false

    for (const q of questions.value) {
        if (!q.question_statement || !q.option_1 || !q.option_2 || !q.option_3 || !q.option_4 || !q.correct_option) {
            return false
        }
    }
    return true
})

const saveQuiz = async () => {
    if (!isValid.value) {
        alert('Please fill in all required fields and ensure each question has a correct answer selected.')
        return
    }

    saving.value = true
    try {
        let currentQuizId = quizId

        // Step 1: Create or Update Quiz Metadata
        const quizPayload = {
            name: quizData.value.name,
            time_duration: parseInt(quizData.value.time_duration),
            remarks: quizData.value.remarks,
            chapter_id: chapterId
        }

        if (isEditing.value) {
            await api.put(`/quiz/updatequiz/${quizId}`, quizPayload)
        } else {
            const quizResponse = await api.post('/quiz/createquiz', quizPayload)
            currentQuizId = quizResponse.data.quiz_id
        }

        // Step 2: Handle Questions
        
        // A. Add New Questions
        const newQuestions = questions.value.filter(q => q.isNew).map(q => ({
            question_statement: q.question_statement,
            option_1: q.option_1,
            option_2: q.option_2,
            option_3: q.option_3,
            option_4: q.option_4,
            correct_option: q.correct_option
        }))

        if (newQuestions.length > 0) {
            await api.post(`/quiz/add_questions/${currentQuizId}`, { questions: newQuestions })
        }

        // B. Update Existing Questions (Only in Edit Mode)
        if (isEditing.value) {
            const existingQuestions = questions.value.filter(q => !q.isNew)
            // Update each modified question
            // Optimization: We could track dirty state, but for now update all existing is safer
            await Promise.all(existingQuestions.map(q => 
                api.put(`/quiz/update_question/${q.id}`, {
                    question_statement: q.question_statement,
                    option_1: q.option_1,
                    option_2: q.option_2,
                    option_3: q.option_3,
                    option_4: q.option_4,
                    correct_option: q.correct_option
                })
            ))

            // C. Delete Removed Questions
            if (deletedQuestions.value.length > 0) {
                await Promise.all(deletedQuestions.value.map(id => 
                    api.delete(`/quiz/delete_question/${id}`)
                ))
            }
        }

        alert(isEditing.value ? 'Quiz updated successfully!' : 'Quiz created successfully!')
        router.push(`/dashboard/subjects/${subjectId}/chapters/${chapterId}/quizzes`)
    } catch (error) {
        console.error('Failed to save quiz:', error)
        alert(error.response?.data?.message || 'Failed to save quiz')
    } finally {
        saving.value = false
    }
}

const goBack = () => {
    if (confirm('Are you sure? Any unsaved changes will be lost.')) {
        router.push(`/dashboard/subjects/${subjectId}/chapters/${chapterId}/quizzes`)
    }
}
</script>

<style scoped>
.manual-quiz-creator {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.page-header {
    margin-bottom: 2rem;
}

.breadcrumb-item {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.9rem;
    display: inline-block;
    margin-bottom: 1rem;
    transition: color 0.2s;
}

.breadcrumb-item:hover {
    color: var(--primary-color);
}

.page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    color: var(--text-primary);
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
}

.quiz-form-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.section-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 2rem;
}

.section-card h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 1.5rem 0;
    color: var(--text-primary);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-header h2 {
    margin: 0;
}

.form-row {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-weight: 500;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.modern-input,
.modern-textarea {
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 1rem;
    transition: all 0.2s;
}

.modern-input:focus,
.modern-textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.modern-textarea {
    resize: vertical;
    min-height: 80px;
    font-family: inherit;
}

.question-input {
    min-height: 100px;
}

.btn-add-question {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.75rem 1.25rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
}

.btn-add-question:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.empty-questions {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.questions-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.question-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s;
}

.question-card:hover {
    border-color: var(--primary-color);
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.question-number {
    font-weight: 600;
    color: var(--primary-color);
    font-size: 1.1rem;
}

.btn-delete {
    background: transparent;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    transition: all 0.2s;
    opacity: 0.6;
}

.btn-delete:hover {
    opacity: 1;
    background: rgba(239, 68, 68, 0.1);
}

.options-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
}

.option-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.option-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.option-header label {
    font-weight: 500;
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin: 0;
}

.radio-correct {
    cursor: pointer;
    width: 16px;
    height: 16px;
    margin-left: auto;
}

.radio-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
}

.validation-warning {
    margin-top: 1rem;
    padding: 0.75rem;
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 8px;
    color: #f59e0b;
    font-size: 0.9rem;
}

.action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding-top: 1rem;
}

.btn-primary,
.btn-secondary {
    padding: 0.875rem 2rem;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    border: none;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-secondary {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-primary);
}

.btn-secondary:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

@media (max-width: 768px) {
    .form-row {
        grid-template-columns: 1fr;
    }

    .options-grid {
        grid-template-columns: 1fr;
    }

    .action-buttons {
        flex-direction: column-reverse;
    }

    .btn-primary,
    .btn-secondary {
        width: 100%;
    }
}
</style>

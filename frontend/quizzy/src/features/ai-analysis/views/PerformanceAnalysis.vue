<template>
    <div class="analysis-panel">
        <div class="intro" v-if="!analysisResult && !loading">
            <div class="header-section">
                <div class="icon-box">📊</div>
                <div>
                    <h3>Performance Analysis</h3>
                    <p>Select quizzes to analyze your weak spots.</p>
                </div>
            </div>

            <div class="quiz-selector">
                <div v-if="quizzes.length === 0" class="no-quizzes">
                    No quizzes found. Complete some quizzes first!
                </div>
                <div v-else class="quiz-grid">
                    <div v-for="q in quizzes" :key="q.id" class="quiz-item"
                        :class="{ selected: selectedQuizzes.includes(q.id) }" @click="toggleQuiz(q.id)">
                        <div class="checkbox">
                            <span v-if="selectedQuizzes.includes(q.id)">✓</span>
                        </div>
                        <div class="q-info">
                            <span class="q-name">{{ q.name }}</span>
                            <span class="q-meta">{{ q.chapter_name || 'General' }} • {{ q.attempt_count }}
                                Attempts</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="actions">
                <button class="btn-primary" @click="analyze" :disabled="selectedQuizzes.length === 0">
                    Analyze Selected ({{ selectedQuizzes.length }})
                </button>
            </div>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>{{ loadingMessage }}</p>
        </div>

        <div v-if="analysisResult" class="result-view">
            <div class="result-header">
                <h3><span class="sparkle">✨</span> AI Insights</h3>
                <button class="btn-text" @click="reset">New Analysis</button>
            </div>

            <div class="summary-card">
                <p class="summary-text">{{ analysisResult.summary }}</p>
            </div>

            <div class="weak-areas-list">
                <h4>Focus Areas Identified</h4>
                <div v-for="(area, idx) in analysisResult.weak_areas" :key="idx" class="area-card">
                    <div class="area-header">
                        <span class="area-tag">Priority {{ idx + 1 }}</span>
                        <h5>{{ area.concept }}</h5>
                    </div>
                    <p class="advice">{{ area.advice }}</p>

                    <div class="area-actions">
                        <button class="btn-action" @click="getMoreInfo(area, idx)">
                            📖 Read Concept
                        </button>
                        <button class="btn-action primary" @click="practiceConcept(area)">
                            ⚡ Practice Quiz
                        </button>
                    </div>

                    <!-- Inline Study Material -->
                    <div v-if="studyMaterial[idx]" class="study-material fade-in">
                        <div class="material-header">
                            <h6>Study Guide: {{ area.concept }}</h6>
                            <div class="mat-actions">
                                <button class="btn-text small"
                                    @click="openSaveModal(studyMaterial[idx], area.concept)">💾 Save to Library</button>
                                <button class="close-small" @click="studyMaterial[idx] = null">×</button>
                            </div>
                        </div>
                        <div class="markdown-content">
                            {{ studyMaterial[idx] }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Save Confirmation Modal -->
        <div v-if="showSaveModal" class="modal-backdrop" @click.self="showSaveModal = false">
            <div class="modal-card">
                <h3>Save to Library</h3>
                <p>This study guide will be saved to the Subject/Chapter of the analyzed quiz.</p>
                <div class="modal-actions">
                    <button class="btn-text" @click="showSaveModal = false">Cancel</button>
                    <button class="btn-primary" @click="saveMaterial" :disabled="saving">
                        {{ saving ? 'Saving...' : 'Confirm Save' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const quizzes = ref([])
const selectedQuizzes = ref([])
const loading = ref(false)
const loadingMessage = ref('')
const analysisResult = ref(null)
const studyMaterial = ref({}) // Map concept -> markdown

// Fetch attemptable quizzes (or specifically those with history)
const fetchQuizzes = async () => {
    try {
        const res = await api.get('/quiz/getquizzes')
        // Filter only quizzes that have been attempted
        quizzes.value = res.data.quizzes.filter(q => q.attempt_count > 0)
    } catch (e) {
        console.error(e)
    }
}

const toggleQuiz = (id) => {
    if (selectedQuizzes.value.includes(id)) {
        selectedQuizzes.value = selectedQuizzes.value.filter(i => i !== id)
    } else {
        selectedQuizzes.value.push(id)
    }
}

const analyze = async () => {
    loading.value = true
    loadingMessage.value = "Analyzing performance patterns..."
    try {
        const res = await api.post('/ai/analyze_performance', {
            quiz_ids: selectedQuizzes.value
        })

        let raw = res.data.analysis
        // Clean JSON
        raw = raw.replace(/```json/g, '').replace(/```/g, '').trim()
        analysisResult.value = JSON.parse(raw)

    } catch (error) {
        alert(error.response?.data?.message || 'Analysis failed')
    } finally {
        loading.value = false
    }
}

const getMoreInfo = async (area, idx) => {
    // If it's already showing for this index, do nothing (or toggle off?). 
    // The UI has a close button, so we probably just want to ensure it's loaded.
    if (studyMaterial.value[idx]) return

    loading.value = true
    loadingMessage.value = `Generating study guide for ${area.concept}...`
    try {
        const res = await api.post('/ai/generate_study_material', {
            topic: area.concept,
            context: area.advice
        })
        studyMaterial.value[idx] = res.data.material
    } catch (e) {
        alert("Failed to generate material")
    } finally {
        loading.value = false
    }
}

const emit = defineEmits(['practice-concept'])

const practiceConcept = (area) => {
    emit('practice-concept', area.concept)
}

const reset = () => {
    analysisResult.value = null
    selectedQuizzes.value = []
    studyMaterial.value = {}
}

const showSaveModal = ref(false)
const currentMaterial = ref(null) // material to save
const saving = ref(false)

const openSaveModal = (materialStr, concept) => {
    currentMaterial.value = { content: materialStr, concept }
    showSaveModal.value = true
}

const saveMaterial = async () => {
    saving.value = true
    try {
        // Find subject/chapter context from the first selected quiz
        const firstQuizId = selectedQuizzes.value[0]
        const quiz = quizzes.value.find(q => q.id === firstQuizId)

        if (!quiz) throw new Error("Context not found")

        await api.post('/ai/save_analysis', {
            title: `AI Study Guide: ${currentMaterial.value.concept}`,
            content: currentMaterial.value.content,
            subject_id: quiz.subject_id,
            chapter_id: quiz.chapter_id,
            quiz_name: quiz.name
        })

        alert("Study material saved to library!")
        showSaveModal.value = false
    } catch (e) {
        alert(e.response?.data?.message || "Failed to save")
    } finally {
        saving.value = false
    }
}

onMounted(() => {
    fetchQuizzes()
})
</script>

<style scoped>
.analysis-panel {
    min-height: 400px;
    color: var(--text-primary);
}

.header-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.icon-box {
    width: 48px;
    height: 48px;
    background: rgba(79, 70, 229, 0.1);
    color: var(--primary-color);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.quiz-selector {
    margin-bottom: 2rem;
}

.quiz-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    max-height: 300px;
    overflow-y: auto;
    padding: 0.25rem;
}

.quiz-item {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    padding: 1rem;
    border-radius: 12px;
    cursor: pointer;
    display: flex;
    gap: 1rem;
    align-items: center;
    transition: all 0.2s;
}

.quiz-item:hover {
    border-color: var(--primary-color);
    background: var(--bg-secondary);
}

.quiz-item.selected {
    border-color: var(--primary-color);
    background: rgba(79, 70, 229, 0.05);
}

.checkbox {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    color: white;
}

.selected .checkbox {
    background: var(--primary-color);
    border-color: var(--primary-color);
}

.q-info {
    display: flex;
    flex-direction: column;
}

.q-name {
    font-weight: 600;
    font-size: 0.95rem;
}

.q-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.actions {
    display: flex;
    justify-content: flex-end;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.85rem 1.75rem;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    transition: opacity 0.2s;
}

.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Loading */
.loading-state {
    text-align: center;
    padding: 4rem;
    color: var(--text-secondary);
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(79, 70, 229, 0.1);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    margin: 0 auto 1rem;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* Results */
.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.summary-card {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(147, 51, 234, 0.05));
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(79, 70, 229, 0.2);
}

.summary-text {
    font-size: 1.1rem;
    line-height: 1.6;
    color: var(--text-primary);
    font-style: italic;
    margin: 0;
}

.area-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.area-header {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 0.75rem;
}

.area-tag {
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
}

.area-header h5 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--text-primary);
}

.advice {
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.area-actions {
    display: flex;
    gap: 1rem;
}

.btn-action {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.6rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
}

.btn-action:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.btn-action.primary {
    background: rgba(79, 70, 229, 0.1);
    color: var(--primary-color);
    border-color: transparent;
}

.btn-action.primary:hover {
    background: var(--primary-color);
    color: white;
}

/* Study Material */
.study-material {
    margin-top: 1.5rem;
    background: var(--bg-primary);
    border-radius: 12px;
    padding: 1.5rem;
    border-left: 4px solid var(--primary-color);
}

.material-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.close-small {
    background: transparent;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    color: var(--text-secondary);
}

.markdown-content {
    white-space: pre-wrap;
    line-height: 1.6;
    font-size: 0.95rem;
}

.fade-in {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(5px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.mat-actions {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.btn-text.small {
    font-size: 0.85rem;
    padding: 0;
}

/* Modal */
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-card {
    background: var(--bg-secondary);
    padding: 2rem;
    border-radius: 16px;
    width: 90%;
    max-width: 400px;
    border: 1px solid var(--border-color);
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
}
</style>

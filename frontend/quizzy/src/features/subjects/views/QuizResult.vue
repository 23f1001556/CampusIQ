<template>
    <div class="result-view">
        <div v-if="loading" class="loading">Loading results...</div>

        <div v-else class="content">
            <div class="score-card">
                <h2>Quiz Complete!</h2>
                <div class="score-circle">
                    <span class="score">{{ result.score }}</span>
                    <span class="total">/ {{ result.total_questions }}</span>
                </div>
                <p>Great job! Here is how you performed.</p>
                <div class="actions">
                    <router-link to="/dashboard" class="btn-secondary">Back to Dashboard</router-link>
                    <router-link to="/dashboard/ai-hub" class="btn-primary">Create New Quiz</router-link>
                </div>
            </div>

            <div class="details-section">
                <h3>Review Answers</h3>
                <div v-for="(q, idx) in result.questions" :key="q.id" class="answer-card"
                    :class="{ 'correct-card': q.user_selected === q.correct_option, 'wrong-card': q.user_selected !== q.correct_option }">
                    <p class="statement"><strong>Q{{ idx + 1 }}:</strong> {{ q.statement }}</p>
                    <div class="options-display">
                        <div v-for="(text, key) in q.options" :key="key" class="option" :class="{
                            'marked-option': q.user_selected === key,
                            'correct-option-highlight': q.correct_option === key
                        }">
                            <div class="option-text">
                                <span class="key-badge">{{ key }}</span> {{ text }}
                            </div>
                            <div class="badges">
                                <span v-if="q.user_selected === key" class="badge marked">Marked</span>
                                <span v-if="q.correct_option === key" class="badge correct">Correct</span>
                                <span v-if="q.user_selected === key && q.user_selected === q.correct_option"
                                    class="icon">✅</span>
                                <span v-if="q.user_selected === key && q.user_selected !== q.correct_option"
                                    class="icon">❌</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const scoreId = route.params.id
const result = ref(null)
const loading = ref(true)

const fetchResult = async () => {
    try {
        const res = await api.get(`/quiz/get_result/${scoreId}`)
        result.value = res.data
    } catch (error) {
        // Native alert removed as per preference? Or keep for non-blocking?
        // Let's console log for now or use a toast if available.
        console.error('Failed to load result', error)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchResult()
})
</script>

<style scoped>
.result-view {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.score-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 3rem;
    text-align: center;
    margin-bottom: 3rem;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.score-circle {
    font-size: 4rem;
    font-weight: 800;
    color: var(--primary-color);
    margin: 1rem 0;
}

.total {
    font-size: 2rem;
    color: var(--text-secondary);
}

.actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
    padding: 0.875rem 1.75rem;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.btn-secondary {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
}

.btn-primary:hover,
.btn-secondary:hover {
    transform: translateY(-2px);
}

.details-section h3 {
    margin-bottom: 2rem;
    font-size: 1.5rem;
    font-weight: 700;
}

.answer-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
}

.correct-card {
    border-left: 6px solid #10b981;
}

.wrong-card {
    border-left: 6px solid #ef4444;
}

.statement {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1.25rem;
}

.options-display {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.option {
    padding: 1rem;
    border-radius: 12px;
    background: var(--bg-primary);
    border: 1.5px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s;
}

.option-text {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.key-badge {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.8rem;
    border: 1px solid var(--border-color);
}

.marked-option {
    background: rgba(239, 68, 68, 0.05);
    border-color: rgba(239, 68, 68, 0.2);
}

.correct-option-highlight {
    background: rgba(16, 185, 129, 0.05);
    border-color: #10b981;
}

.badges {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.badge {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
}

.badge.marked {
    background: #ef4444;
    color: white;
}

.badge.correct {
    background: #10b981;
    color: white;
}

.icon {
    font-size: 1.2rem;
}
</style>

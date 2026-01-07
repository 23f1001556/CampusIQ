<template>
    <div class="quiz-attempt-view">
        <div v-if="loading" class="loading">Loading quiz...</div>

        <div v-else-if="quiz" class="quiz-container">
            <div class="quiz-header">
                <h2>{{ quiz.name }}</h2>
                <div class="meta">
                    <span class="timer-badge" :class="{ 'warning': secondsRemaining < 60 }">
                        Time Remaining: {{ timeLeftDisplay }}
                    </span>
                </div>
            </div>

            <form @submit.prevent="submitQuiz">
                <div v-for="(q, index) in quiz.questions" :key="q.id" class="question-card">
                    <h4>Q{{ index + 1 }}: {{ q.statement }}</h4>
                    <div class="options">
                        <label class="option-row">
                            <input type="radio" :name="'q' + q.id" :value="'1'" v-model="answers[q.id]">
                            <span>{{ q.option_1 }}</span>
                        </label>
                        <label class="option-row">
                            <input type="radio" :name="'q' + q.id" :value="'2'" v-model="answers[q.id]">
                            <span>{{ q.option_2 }}</span>
                        </label>
                        <label class="option-row">
                            <input type="radio" :name="'q' + q.id" :value="'3'" v-model="answers[q.id]">
                            <span>{{ q.option_3 }}</span>
                        </label>
                        <label class="option-row">
                            <input type="radio" :name="'q' + q.id" :value="'4'" v-model="answers[q.id]">
                            <span>{{ q.option_4 }}</span>
                        </label>
                    </div>
                </div>

                <div class="actions">
                    <button type="submit" class="btn-primary" :disabled="submitting">
                        {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
                    </button>
                    <button type="button" class="btn-secondary" @click="cancel">Cancel</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const quizId = route.params.id
const quiz = ref(null)
const loading = ref(true)
const submitting = ref(false)
const answers = ref({})

// Timer Logic
const secondsRemaining = ref(0)
const timeLeftDisplay = ref("00:00")
let timerInterval = null

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const startTimer = (durationMins) => {
    secondsRemaining.value = durationMins * 60
    timeLeftDisplay.value = formatTime(secondsRemaining.value)

    timerInterval = setInterval(() => {
        secondsRemaining.value--
        timeLeftDisplay.value = formatTime(secondsRemaining.value)

        if (secondsRemaining.value <= 0) {
            clearInterval(timerInterval)
            autoSubmit()
        }
    }, 1000)
}

const autoSubmit = () => {
    alert("Time is up! Your quiz will be submitted automatically.")
    submitQuiz(true)
}

const fetchQuiz = async () => {
    try {
        const res = await api.get(`/quiz/getquiz/${quizId}`)
        quiz.value = res.data.quiz
        // Initialize answers
        if (quiz.value.questions) {
            quiz.value.questions.forEach(q => {
                answers.value[q.id] = null
            })
        }

        // Start Timer
        if (quiz.value.time_duration) {
            startTimer(quiz.value.time_duration)
        }

        enterFullScreen()
        document.addEventListener("visibilitychange", handleVisibilityChange)

    } catch (error) {
        alert(error.response?.data?.message || 'Failed to load quiz')
        router.back()
    } finally {
        loading.value = false
    }
}

const enterFullScreen = () => {
    const elem = document.documentElement
    if (elem.requestFullscreen) {
        elem.requestFullscreen().catch(() => {
            // Full screen denied, silent catch
        })
    }
}

const handleVisibilityChange = () => {
    if (document.hidden) {
        alert("WARNING: You are not allowed to switch tabs during the quiz!")
        // Optional: Auto submit or strike
    }
}

const submitQuiz = async (isAuto = false) => {
    if (!isAuto && !confirm("Are you sure you want to submit?")) return

    if (timerInterval) clearInterval(timerInterval)

    submitting.value = true
    try {
        const res = await api.post('/quiz/submit', {
            quiz_id: quizId,
            answers: answers.value
        })

        // Exit security
        document.removeEventListener("visibilitychange", handleVisibilityChange)
        if (document.exitFullscreen) document.exitFullscreen().catch(() => { })

        // Handle Response
        if (res.data.score !== undefined && res.data.score !== null) {
            // Score available
            router.push(`/dashboard/quiz/result/${res.data.score_id}`)
        } else {
            // Pending Release
            alert(res.data.message || "Submission Successful. Results will be released later.")
            router.push('/dashboard/mock-quizzes')
        }

    } catch (error) {
        alert("Submission failed: " + (error.response?.data?.message || error.message))
    } finally {
        submitting.value = false
    }
}

const cancel = () => {
    document.removeEventListener("visibilitychange", handleVisibilityChange)
    if (document.exitFullscreen) document.exitFullscreen().catch(() => { })
    router.back()
}

onMounted(() => {
    fetchQuiz()
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
    document.removeEventListener("visibilitychange", handleVisibilityChange)
    if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.quiz-attempt-view {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.quiz-header {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid var(--border-color);
    position: sticky;
    top: 1rem;
    z-index: 100;
}

.timer-badge {
    padding: 0.5rem 1rem;
    background: rgba(99, 102, 241, 0.1);
    color: #6366f1;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.1rem;
    font-family: monospace;
}

.timer-badge.warning {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    animation: blink 1s infinite;
}

@keyframes blink {
    50% {
        opacity: 0.5;
    }
}

.question-card {
    background: var(--bg-primary);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
}

.question-card h4 {
    margin-bottom: 1rem;
}

.options {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.option-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: background 0.2s;
}

.option-row:hover {
    background: var(--bg-secondary);
}

.option-row input:checked+span {
    font-weight: bold;
    color: var(--primary-color);
}

.actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
}

.btn-secondary {
    background: transparent;
    border: 1px solid var(--border-color);
    padding: 0.75rem 2rem;
    border-radius: 8px;
    cursor: pointer;
    color: var(--text-primary);
}
</style>

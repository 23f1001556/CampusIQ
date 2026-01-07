<template>
    <div class="mock-attempt-view">
        <div v-if="loading" class="loading">Loading quiz...</div>

        <!-- Start Quiz Overlay -->
        <div v-if="!loading && !isStarted" class="start-overlay">
            <div class="start-card">
                <h2>{{ quiz?.title || 'Mock Quiz' }}</h2>
                <div class="instructions">
                    <h3>⚠️ Strict Exam Mode</h3>
                    <ul>
                        <li>Full screen mode will be enforced.</li>
                        <li>Tab switching is monitored.</li>
                        <li>Right-click and most keyboard shortcuts are disabled.</li>
                        <li>Only <strong>Numbers</strong>, <strong>Decimal (.)</strong> and <strong>Backspace</strong>
                            are
                            allowed.</li>
                        <li>Do not exit full screen or your attempt may be flagged.</li>
                    </ul>
                </div>
                <button class="btn-start" @click="startExam">Start Exam</button>
            </div>
        </div>

        <div v-else-if="quiz" class="quiz-container">
            <div class="quiz-header">
                <h2>{{ quiz.title }}</h2>
                <div class="timer" :class="{ 'warning': secondsRemaining < 60 }">
                    Time Remaining: {{ timeLeftDisplay }}
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
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const quizId = route.params.id
const quiz = ref(null)
const loading = ref(true)
const submitting = ref(false)
const answers = ref({})

// Exam Control
const isStarted = ref(false)
const isSubmitted = ref(false) // Track if normally submitted

// Prevent accidental navigation
onBeforeRouteLeave((to, from, next) => {
    if (isStarted.value && !isSubmitted.value) {
        const answer = window.confirm('⚠️ Warning: Leaving this page will effectively forfeit your attempt. You cannot return. Are you sure?')
        if (answer) {
            // Let them leave, but strictly speaking, the backend attempt is already "started" 
            // and won't be submittable if strictly enforced,
            // or will just look like an abandoned attempt (score=None).
            next()
        } else {
            next(false)
        }
    } else {
        next()
    }
})

const fetchQuiz = async () => {
    try {
        const res = await api.get(`/mock/quiz/${quizId}`)
        quiz.value = res.data
        // Initialize answers
        quiz.value.questions.forEach(q => {
            answers.value[q.id] = null
        })
    } catch (error) {
        if (error.response?.status === 403) {
            alert("You have already submitted this quiz.")
            router.push(`/dashboard/mock-result/${quizId}`)
        } else {
            console.error(error) // Log for debugging
            alert(error.response?.data?.message || 'Failed to load quiz')
            router.push('/dashboard/mock-quizzes')
        }
    } finally {
        loading.value = false
    }
}

const startExam = async () => {
    try {
        await api.post('/mock/start', { mock_quiz_id: quizId })
        isStarted.value = true
        enterFullScreen()
        addEventListeners()

        // Start Timer
        if (quiz.value.duration_minutes) {
            startTimer(quiz.value.duration_minutes)
        }
    } catch (error) {
        if (error.response?.status === 403) {
            alert("You have already attempted this quiz.")
            router.push(`/dashboard/mock-result/${quizId}`)
        } else {
            alert(error.response?.data?.message || "Failed to start quiz")
        }
    }
}

const enterFullScreen = () => {
    const el = document.documentElement
    if (el.requestFullscreen) el.requestFullscreen()
    else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen()
    else if (el.msRequestFullscreen) el.msRequestFullscreen()
}

// Restriction Logic
const preventContextMenu = (e) => {
    e.preventDefault()
    return false
}

const handleKeyDown = (e) => {
    // Allow: numbers 0-9, Numpad 0-9, Backspace, Delete, Arrow Keys, Tab, Enter (if needed), Decimal point
    const allowedKeys = [
        'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab',
        '.', 'Period', 'NumpadDecimal'
    ]

    // Allow numbers
    if ((e.key >= '0' && e.key <= '9') || allowedKeys.includes(e.key)) {
        return
    }

    // Block everything else
    e.preventDefault()
}

const handleVisibilityChange = () => {
    if (document.hidden && isStarted.value) {
        alert("⚠️ Warning: Tab switching is monitored. Please stay on this tab.")
    }
}

const addEventListeners = () => {
    document.addEventListener('contextmenu', preventContextMenu)
    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('visibilitychange', handleVisibilityChange)
}

const removeEventListeners = () => {
    document.removeEventListener('contextmenu', preventContextMenu)
    document.removeEventListener('keydown', handleKeyDown)
    document.removeEventListener('visibilitychange', handleVisibilityChange)
}

const submitQuiz = async (isAuto = false) => {
    if (!isAuto && !confirm("Are you sure you want to submit?")) return

    if (timerInterval) clearInterval(timerInterval)

    submitting.value = true
    try {
        await api.post('/mock/attempt', {
            mock_quiz_id: quizId,
            answers: answers.value
        })
        // Exit strict mode before navigating
        if (document.exitFullscreen) document.exitFullscreen()
        removeEventListeners()

        isSubmitted.value = true // Allow navigation
        router.push(`/dashboard/mock-result/${quizId}`)
    } catch (error) {
        alert("Submission failed: " + (error.response?.data?.message || error.message))
    } finally {
        submitting.value = false
    }
}

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
    alert("Time is up! Your exam will be submitted automatically.")
    submitQuiz(true)
}

onMounted(() => {
    fetchQuiz()
})

onUnmounted(() => {
    removeEventListeners()
    if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.mock-attempt-view {
    max-width: 800px;
    margin: 0 auto;
    /* Center content in full screen */
}

/* Start Overlay */
.start-overlay {
    position: fixed;
    inset: 0;
    background: var(--bg-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.start-card {
    background: var(--bg-secondary);
    padding: 3rem;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    text-align: center;
    max-width: 500px;
    width: 90%;
}

.instructions {
    text-align: left;
    margin: 2rem 0;
    background: #fff1f2;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #fecdd3;
    color: #9f1239;
}

.instructions h3 {
    margin-top: 0;
    color: #be123c;
}

.instructions ul {
    margin: 1rem 0 0 1.5rem;
    padding: 0;
}

.instructions li {
    margin-bottom: 0.5rem;
}

.btn-start {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 1rem 3rem;
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: 700;
    cursor: pointer;
    transition: transform 0.2s;
}

.btn-start:hover {
    transform: scale(1.05);
}

.quiz-container {
    padding-top: 2rem;
}

.timer {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--primary-color);
    font-family: monospace;
    padding: 0.5rem 1rem;
    background: rgba(99, 102, 241, 0.1);
    border-radius: 8px;
}

.timer.warning {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
    animation: blink 1s infinite;
}

@keyframes blink {
    50% {
        opacity: 0.5;
    }
}

.question-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
}

.question-card h4 {
    margin-top: 0;
    font-size: 1.1rem;
    line-height: 1.6;
}

.options {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1rem;
}

.option-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: all 0.2s;
}

.option-row:hover {
    background: var(--bg-accent);
    border-color: var(--primary-color);
}

.option-row input:checked+span {
    font-weight: 600;
    color: var(--primary-color);
}

.actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 2rem;
    padding-bottom: 4rem;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 1rem 3rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary:hover {
    background: var(--primary-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Dark mode adjustments for success/warning colors */
:root.dark .instructions {
    background: #4c0519;
    border-color: #881337;
    color: #fecdd3;
}

:root.dark .instructions h3 {
    color: #fb7185;
}
</style>

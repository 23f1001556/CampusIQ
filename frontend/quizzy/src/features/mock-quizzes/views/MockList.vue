<template>
    <div class="mock-list-view">
        <div class="header-section">
            <div class="header-content">
                <h1>Global Quizzes</h1>
                <p>Compete with others and test your knowledge with scheduled mock exams.</p>
            </div>
            <div class="stats-overview">
                <div class="stat-pill">
                    <span class="label">Available</span>
                    <span class="value">{{ activeCount }}</span>
                </div>
                <div class="stat-pill">
                    <span class="label">Attempted</span>
                    <span class="value">{{ attemptedCount }}</span>
                </div>
            </div>
        </div>

        <div v-if="loading" class="quizzes-grid">
            <div v-for="n in 3" :key="n" class="skeleton-card"></div>
        </div>

        <div v-else class="quizzes-grid">
            <div v-if="quizzes.length === 0" class="empty-state">
                <div class="empty-icon">🏆</div>
                <h3>No Mock Quizzes Available</h3>
                <p>Check back later for scheduled exams.</p>
            </div>

            <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-card" :class="{ 'card-attempted': quiz.attempted }">
                <div class="card-header" :style="{ background: getGradient(quiz.id) }">
                    <div class="status-badge" :class="getStatusClass(quiz.status)">
                        {{ getStatusText(quiz.status) }}
                    </div>
                    <div class="quiz-icon">📝</div>
                </div>

                <div class="card-body">
                    <h3>{{ quiz.name }}</h3>
                    <p class="description">{{ quiz.remarks || 'No description provided.' }}</p>

                    <div class="meta-grid">
                        <div class="meta-item">
                            <span class="icon">⏱️</span>
                            <span>{{ quiz.time_duration }} mins</span>
                        </div>
                        <div class="meta-item">
                            <span class="icon">📅</span>
                            <span>{{ formatDate(quiz.start_time) }}</span>
                        </div>
                    </div>

                    <div v-if="quiz.attempted" class="score-display">
                        <template v-if="quiz.scores_released || quiz.score">
                            <span class="score-label">Your Score</span>
                            <div class="score-value">
                                {{ quiz.score }} <span class="total">/ {{ quiz.total_marks }}</span>
                            </div>
                        </template>
                        <template v-else>
                            <span class="score-label">Status</span>
                            <div class="score-value pending">
                                Pending
                            </div>
                        </template>
                    </div>
                </div>

                <div class="card-footer">
                    <div v-if="quiz.attempted" class="actions">
                        <div class="dual-actions">
                            <!-- Global Quiz: No Re-attempt -->
                            <button v-if="quiz.status === 'live'" class="btn-disabled flex-1" disabled
                                title="Re-attempt not allowed for global quizzes">
                                Submitted
                            </button>

                            <!-- Result or Pending -->
                            <button v-if="quiz.scores_released || quiz.score" class="btn-secondary flex-1"
                                @click="$router.push(`/dashboard/quiz/result/${quiz.score_id}`)">
                                View Result
                            </button>
                            <button v-else class="btn-disabled flex-1" disabled>
                                Results Pending
                            </button>
                        </div>
                    </div>
                    <div v-else class="actions">
                        <button v-if="quiz.status === 'live'" class="btn-primary full-width"
                            @click="$router.push(`/dashboard/quiz/${quiz.id}/attempt`)">
                            Attempt Now
                        </button>
                        <button v-else-if="quiz.status === 'upcoming'" class="btn-disabled full-width" disabled>
                            Starts {{ formatDate(quiz.start_time) }}
                        </button>
                        <button v-else class="btn-disabled full-width" disabled>
                            Ended
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const quizzes = ref([])
const loading = ref(true)

const activeCount = computed(() => quizzes.value.filter(q => q.status === 'live').length)
const attemptedCount = computed(() => quizzes.value.filter(q => q.attempted).length)

const fetchQuizzes = async () => {
    try {
        const res = await api.get('/quiz/get_mock_quizzes')
        quizzes.value = res.data.quizzes
    } catch (error) {
        console.error("Failed to fetch quizzes", error)
    } finally {
        loading.value = false
    }
}

const getStatusText = (status) => {
    if (status === 'live') return 'Live Now'
    if (status === 'upcoming') return 'Upcoming'
    return 'Ended'
}

const getStatusClass = (status) => {
    if (status === 'live') return 'status-live'
    if (status === 'upcoming') return 'status-upcoming'
    return 'status-ended'
}

const getGradient = (id) => {
    const gradients = [
        'linear-gradient(135deg, #8b5cf6, #d8b4fe)',
        'linear-gradient(135deg, #f59e0b, #fcd34d)',
        'linear-gradient(135deg, #10b981, #6ee7b7)',
        'linear-gradient(135deg, #3b82f6, #93c5fd)'
    ]
    return gradients[id % gradients.length]
}

const formatDate = (iso) => {
    if (!iso) return ''
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
    fetchQuizzes()
})
</script>

<style scoped>
.mock-list-view {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.header-section {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 2.5rem;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.header-content h1 {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.5px;
}

.header-content p {
    color: var(--text-secondary);
    font-size: 1rem;
}

.stats-overview {
    display: flex;
    gap: 1rem;
}

.stat-pill {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 0.5rem 1rem;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.stat-pill .label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-transform: uppercase;
}

.stat-pill .value {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--primary-color);
}

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
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.quiz-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.card-header {
    height: 120px;
    position: relative;
    padding: 1rem;
}

.status-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(4px);
}

.status-live {
    color: #16a34a;
}

.status-completed {
    color: #4f46e5;
}

.status-upcoming {
    color: #2563eb;
}

.status-ended {
    color: #4b5563;
}

.quiz-icon {
    width: 56px;
    height: 56px;
    background: var(--bg-secondary);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    position: absolute;
    bottom: -28px;
    left: 1.5rem;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.card-body {
    padding: 2.5rem 1.5rem 1.5rem;
    flex: 1;
}

.card-body h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
}

.description {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 1.5rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.meta-grid {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.score-display {
    background: rgba(99, 102, 241, 0.05);
    border: 1px solid rgba(99, 102, 241, 0.1);
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    margin-top: 1rem;
}

.score-label {
    display: block;
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

.score-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--primary-color);
}

.score-value .total {
    font-size: 1rem;
    color: var(--text-secondary);
    font-weight: 600;
}

.card-footer {
    padding: 1.25rem 1.5rem;
    background: var(--bg-accent);
    border-top: 1px solid var(--border-color);
}

.full-width {
    width: 100%;
}

.dual-actions {
    display: flex;
    gap: 0.5rem;
    width: 100%;
}

.flex-1 {
    flex: 1;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.85rem;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
    background: transparent;
    border: 1px solid var(--primary-color);
    color: var(--primary-color);
    padding: 0.85rem;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-secondary:hover {
    background: rgba(99, 102, 241, 0.05);
}

.btn-disabled {
    background: var(--bg-primary);
    color: var(--text-disabled);
    border: 1px solid var(--border-color);
    padding: 0.85rem;
    border-radius: 12px;
    font-weight: 600;
    cursor: not-allowed;
    opacity: 0.8;
}

.skeleton-card {
    height: 300px;
    background: var(--bg-secondary);
    border-radius: 20px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        opacity: 0.6;
    }

    50% {
        opacity: 0.3;
    }

    100% {
        opacity: 0.6;
    }
}

.empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 4rem;
    background: var(--bg-secondary);
    border-radius: 20px;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}
</style>

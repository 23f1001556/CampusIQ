<template>
    <div class="result-view">
        <div v-if="loading" class="loading">Loading results...</div>

        <div v-else class="content">
            <div class="score-card">
                <h2>Quiz Result</h2>
                <div class="score-circle">
                    <span class="score">{{ result.score }}</span>
                    <span class="total">/ {{ result.total_questions }}</span>
                </div>
                <!-- AI Analysis Button (Future) -->
            </div>

            <div class="columns">
                <!-- Detailed Answers -->
                <div class="details-column">
                    <h3>Review Answers</h3>
                    <div v-for="(q, idx) in result.details" :key="idx" class="answer-card"
                        :class="{ 'correct-card': q.is_correct, 'wrong-card': !q.is_correct }">
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
                                    <span v-if="q.user_selected === key && q.is_correct" class="icon">✅</span>
                                    <span v-if="q.user_selected === key && !q.is_correct" class="icon">❌</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Leaderboard -->
                <div class="leaderboard-column">
                    <h3>Global Leaderboard</h3>
                    <div v-if="!result.is_published" class="leaderboard-placeholder">
                        <p>🔒 Rankings will be revealed once the admin publishes the results.</p>
                    </div>

                    <div v-else-if="loadingLeaderboard" class="loading">Loading ranks...</div>

                    <div v-else class="leaderboard-list">
                        <div v-for="entry in leaderboard" :key="entry.rank" class="rank-row"
                            :class="{ 'my-rank': entry.user_name === user.username }">
                            <span class="rank">#{{ entry.rank }}</span>
                            <div class="user-info">
                                <span class="name">{{ entry.fullname }}</span>
                                <small>@{{ entry.user_name }}</small>
                            </div>
                            <span class="score">{{ entry.score }} pts</span>
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
const quizId = route.params.id
const result = ref(null)
const leaderboard = ref([])
const loading = ref(true)
const loadingLeaderboard = ref(false)

const user = JSON.parse(localStorage.getItem('user') || '{}')

const fetchResult = async () => {
    try {
        const res = await api.get(`/mock/get_result/${quizId}`)
        result.value = res.data
        if (result.value.is_published) {
            fetchLeaderboard()
        }
    } catch (error) {
        alert(error.response?.data?.message || 'Failed to load result')
    } finally {
        loading.value = false
    }
}

const fetchLeaderboard = async () => {
    loadingLeaderboard.value = true
    try {
        const res = await api.get(`/mock/leaderboard/${quizId}`)
        leaderboard.value = res.data.leaderboard
    } catch (error) {
        console.error("Leaderboard error", error)
    } finally {
        loadingLeaderboard.value = false
    }
}

onMounted(() => {
    fetchResult()
})
</script>

<style scoped>
.result-view {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.score-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 3rem;
    text-align: center;
    margin-bottom: 2rem;
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

.columns {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
}

@media (max-width: 900px) {
    .columns {
        grid-template-columns: 1fr;
    }
}

.answer-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
    transition: transform 0.2s;
}

.answer-card:hover {
    transform: translateY(-2px);
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
    color: var(--text-primary);
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

/* Leaderboard */
.leaderboard-column {
    background: var(--bg-secondary);
    padding: 2rem;
    border-radius: 20px;
    height: fit-content;
    border: 1px solid var(--border-color);
    position: sticky;
    top: 20px;
}

.leaderboard-list {
    margin-top: 1.5rem;
}

.rank-row {
    display: flex;
    align-items: center;
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 0.5rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
}

.my-rank {
    background: rgba(99, 102, 241, 0.1);
    border-color: var(--primary-color);
}

.rank {
    width: 40px;
    font-weight: 800;
    color: var(--primary-color);
    font-size: 1.1rem;
}

.user-info {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.name {
    font-weight: 600;
    color: var(--text-primary);
}

small {
    color: var(--text-secondary);
}

.score {
    font-weight: 700;
    color: var(--primary-color);
}
</style>

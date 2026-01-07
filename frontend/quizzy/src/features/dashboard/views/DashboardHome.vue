<!-- <template>
    <div class="dashboard-home">
        <div class="stats-grid">
            <div class="card stat-card">
                <h3>Total Quizzes</h3>
                <p class="value">{{ stats.total_quizzes }}</p>
            </div>
            <div class="card stat-card">
                <h3>Average Score</h3>
                <p class="value">{{ stats.average_score }}%</p>
            </div>
            <div class="card stat-card">
                <h3>Days Active</h3>
                <p class="value">{{ stats.days_active }}</p>
            </div>
        </div>

        <section class="content-section">
            <div class="card">
                <h3>Recent Activity</h3>
                <div v-if="stats.recent_activity.length > 0" class="activity-list">
                    <div v-for="(act, idx) in stats.recent_activity" :key="idx" class="activity-item">
                        <div class="info">
                            <span class="title">{{ act.title }}</span>
                            <span class="date">{{ act.date }}</span>
                        </div>
                        <span class="score badge" :class="getScoreClass(act.score)">{{ act.score }} pts</span>
                    </div>
                </div>
                <p v-else style="color: var(--text-secondary); margin-top: 1rem;">
                    No recent activity. Start a quiz to see your progress here!
                </p>
                <button class="btn btn-primary" style="margin-top: 1rem;"
                    @click="$router.push('/dashboard/mock-quizzes')">Browse Quizzes</button>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const stats = ref({
    total_quizzes: 0,
    average_score: 0,
    days_active: 0,
    recent_activity: []
})

const fetchStats = async () => {
    try {
        const res = await api.get('/users/dashboard_stats')
        stats.value = res.data
    } catch (error) {
        console.error("Failed to fetch dashboard stats", error)
    }
}

const getScoreClass = (score) => {
    if (score >= 8) return 'high'
    if (score >= 5) return 'medium'
    return 'low'
}

onMounted(() => {
    fetchStats()
})
</script>

<style scoped>
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2.5rem;
}

.stat-card h3 {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.stat-card .value {
    margin: 0.5rem 0 0 0;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary-color);
}

.activity-list {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.activity-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg-secondary);
    border-radius: 8px;
}

.info {
    display: flex;
    flex-direction: column;
}

.title {
    font-weight: 600;
    font-size: 0.95rem;
}

.date {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
}

.badge.high {
    background: #dcfce7;
    color: #166534;
}

.badge.medium {
    background: #fef9c3;
    color: #854d0e;
}

.badge.low {
    background: #fee2e2;
    color: #991b1b;
}
</style> -->



<template>
    <div class="dashboard-home">
        <!-- Stats -->
        <section class="stats-grid">
            <div class="card stat-card">
                <h4>Total Quizzes</h4>
                <p class="stat-value">{{ stats.total_quizzes }}</p>
            </div>

            <div class="card stat-card">
                <h4>Average Score</h4>
                <p class="stat-value">{{ stats.average_score }}%</p>
            </div>

            <div class="card stat-card">
                <h4>Days Active</h4>
                <p class="stat-value">{{ stats.days_active }}</p>
            </div>
        </section>

        <!-- Activity -->
        <section class="card activity-card">
            <div class="card-header">
                <h3>Recent Activity</h3>
                <button class="btn btn-primary" @click="$router.push('/dashboard/mock-quizzes')">
                    Browse Quizzes
                </button>
            </div>

            <div v-if="stats.recent_activity.length" class="activity-list">
                <div v-for="(act, idx) in stats.recent_activity" :key="idx" class="activity-item">
                    <div class="activity-info">
                        <p class="activity-title">{{ act.title }}</p>
                        <span class="activity-date">{{ act.date }}</span>
                    </div>

                    <span class="score-badge" :class="getScoreClass(act.score)">
                        {{ act.score }} pts
                    </span>
                </div>
            </div>

            <p v-else class="empty-text">
                No recent activity yet. Start a quiz to track your progress 🚀
            </p>
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const stats = ref({
    total_quizzes: 0,
    average_score: 0,
    days_active: 0,
    recent_activity: []
})

const fetchStats = async () => {
    try {
        const res = await api.get('/users/dashboard_stats')
        stats.value = res.data
    } catch (err) {
        console.error('Failed to load dashboard stats', err)
    }
}

const getScoreClass = (score) => {
    if (score >= 8) return 'high'
    if (score >= 5) return 'medium'
    return 'low'
}

onMounted(fetchStats)
</script>

<style scoped>
.dashboard-home {
    padding: 1.5rem;
    max-width: 1200px;
    margin: auto;
}

/* ---------------- Stats ---------------- */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.25rem;
    margin-bottom: 2rem;
}

.stat-card {
    text-align: left;
}

.stat-card h4 {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.stat-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--primary-color);
}

/* ---------------- Card ---------------- */
.card {
    background: var(--bg-primary);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 26px rgba(0, 0, 0, 0.08);
}

/* ---------------- Activity ---------------- */
.activity-card {
    margin-top: 1rem;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.activity-list {
    margin-top: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.activity-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    background: var(--bg-secondary);
}

.activity-info {
    display: flex;
    flex-direction: column;
}

.activity-title {
    font-weight: 600;
    font-size: 0.95rem;
}

.activity-date {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* ---------------- Badges ---------------- */
.score-badge {
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    white-space: nowrap;
}

.score-badge.high {
    background: #dcfce7;
    color: #166534;
}

.score-badge.medium {
    background: #fef3c7;
    color: #92400e;
}

.score-badge.low {
    background: #fee2e2;
    color: #991b1b;
}

/* ---------------- Empty ---------------- */
.empty-text {
    margin-top: 1rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

/* ---------------- Button ---------------- */
.btn {
    padding: 0.55rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    border: none;
}

.btn-primary {
    background: var(--primary-color);
    color: #fff;
}

.btn-primary:hover {
    opacity: 0.9;
}

/* ---------------- Mobile ---------------- */
@media (max-width: 640px) {
    .stat-value {
        font-size: 1.8rem;
    }

    .card-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>

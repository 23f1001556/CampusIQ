<template>
    <div class="leaderboard-page">
        <div class="page-header">
            <h1>Global Leaderboard</h1>
            <p>See where you stand among top performers</p>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Crunching the numbers...</p>
        </div>

        <div v-else class="content-grid">
            <!-- User Stats Card -->
            <div class="stats-card user-stat">
                <div class="rank-circle">
                    <span class="label">Your Rank</span>
                    <span class="value">#{{ stats.user_rank > 0 ? stats.user_rank : '-' }}</span>
                </div>
                <div class="score-info">
                    <h3>{{ username }}</h3>
                    <p>Top {{ percentile }}%</p>
                    <div class="total-score">
                        <span>Total Score:</span>
                        <strong>{{ stats.user_score }}</strong>
                    </div>
                </div>
            </div>

            <!-- Graph Section -->
            <div class="stats-card graph-card">
                <h3>Score Distribution</h3>
                <div class="chart-container">
                    <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
                </div>
            </div>

            <!-- Leaderboard Table -->
            <div class="stats-card table-card">
                <h3>Top Performers</h3>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>User</th>
                                <th>Total Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="user in stats.leaderboard" :key="user.rank"
                                :class="{ 'current-user': user.username === username }">
                                <td class="rank-cell">
                                    <span v-if="user.rank === 1">🥇</span>
                                    <span v-else-if="user.rank === 2">🥈</span>
                                    <span v-else-if="user.rank === 3">🥉</span>
                                    <span v-else>{{ user.rank }}</span>
                                </td>
                                <td class="user-cell">
                                    <div class="avatar-ph">{{ user.username.charAt(0).toUpperCase() }}</div>
                                    {{ user.username }}
                                    <span v-if="user.username === username" class="me-badge">(You)</span>
                                </td>
                                <td class="score-cell">{{ user.score }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const loading = ref(true)
const stats = ref({
    leaderboard: [],
    user_rank: 0,
    user_score: 0,
    total_participants: 0,
    graph_labels: [],
    graph_values: []
})
const username = ref('')

const chartData = computed(() => {
    return {
        labels: stats.value.graph_labels,
        datasets: [{
            label: 'Users',
            data: stats.value.graph_values,
            backgroundColor: 'rgba(99, 102, 241, 0.5)',
            borderColor: '#6366f1',
            borderWidth: 1,
            borderRadius: 4,
            hoverBackgroundColor: '#6366f1'
        }]
    }
})

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0, 0, 0, 0.05)'
            }
        },
        x: {
            grid: {
                display: false
            }
        }
    }
}

const percentile = computed(() => {
    if (stats.value.total_participants === 0 || stats.value.user_rank === -1) return 0
    const p = ((stats.value.total_participants - stats.value.user_rank) / stats.value.total_participants) * 100
    return Math.max(0, p.toFixed(1))
})

const fetchData = async () => {
    try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        username.value = user.user_name || 'User'

        const res = await api.get('/quiz/leaderboard')
        stats.value = res.data
    } catch (error) {
        console.error("Failed to load leaderboard", error)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchData()
})
</script>

<style scoped>
.leaderboard-page {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.page-header {
    margin-bottom: 2rem;
    text-align: center;
}

.page-header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.page-header p {
    color: var(--text-secondary);
    font-size: 1.1rem;
}

.content-grid {
    display: grid;
    grid-template-columns: 350px 1fr;
    grid-template-rows: auto auto;
    gap: 1.5rem;
}

.stats-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

/* User Stat Card */
.user-stat {
    grid-column: 1 / 2;
    grid-row: 1 / 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    background: var(--bg-primary);
    /* Stand out */
    border: 1px solid var(--primary-color);
}

.rank-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
}

.rank-circle .label {
    font-size: 0.8rem;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.rank-circle .value {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1;
}

.score-info h3 {
    font-size: 1.5rem;
    margin: 0 0 0.25rem 0;
}

.score-info p {
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
}

.total-score {
    background: var(--bg-accent);
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    width: 100%;
}

/* Graph Card */
.graph-card {
    grid-column: 2 / 3;
    grid-row: 1 / 2;
    display: flex;
    flex-direction: column;
}

.chart-container {
    flex: 1;
    min-height: 250px;
    margin-top: 1rem;
}

/* Table Card */
.table-card {
    grid-column: 1 / 3;
    grid-row: 2 / 3;
}

.table-responsive {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    text-align: left;
    padding: 1rem;
    color: var(--text-secondary);
    font-weight: 500;
    border-bottom: 1px solid var(--border-color);
}

td {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
}

tr:last-child td {
    border-bottom: none;
}

.rank-cell {
    font-weight: 700;
    font-size: 1.1rem;
    width: 80px;
}

.user-cell {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 500;
}

.avatar-ph {
    width: 32px;
    height: 32px;
    background: var(--bg-accent);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.score-cell {
    font-family: 'Space Mono', monospace;
    font-weight: 600;
}

.current-user {
    background: rgba(99, 102, 241, 0.05);
}

.me-badge {
    font-size: 0.75rem;
    background: var(--primary-color);
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
    .content-grid {
        grid-template-columns: 1fr;
        grid-template-rows: auto;
    }

    .user-stat,
    .graph-card,
    .table-card {
        grid-column: 1 / 2;
        grid-row: auto;
    }
}
</style>

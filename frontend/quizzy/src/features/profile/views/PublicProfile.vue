<template>
    <div class="public-profile-container">
        <div v-if="loading" class="loading-state">
            <div class="loader"></div>
            <p>Loading profile...</p>
        </div>

        <div v-else-if="error" class="error-state">
            <h3>😕 User Not Found</h3>
            <p>{{ error }}</p>
            <button @click="$router.push({ name: 'InstituteDirectory' })" class="btn-back">Back to Directory</button>
        </div>

        <div v-else class="profile-content">
            <!-- Back Button -->
            <button @click="$router.back()" class="back-link">
                ← Back
            </button>

            <!-- Header Card -->
            <div class="profile-header-card">
                <div class="header-background"></div>
                <div class="header-content">
                    <div class="avatar-wrapper">
                        <img v-if="user.profile_picture" :src="getFullImageUrl(user.profile_picture)"
                            class="avatar-img" />
                        <div v-else class="avatar">{{ initials }}</div>
                    </div>

                    <div class="user-info">
                        <div class="name-row">
                            <h1>{{ user.fullname || user.username }}</h1>
                            <span v-if="user.role !== 'user'" class="badge" :class="user.role">{{ user.role }}</span>
                        </div>
                        <p class="email" v-if="user.email">{{ user.email }}</p>
                        <p class="qualification" v-if="user.qualification">{{ user.qualification }}</p>

                        <p class="bio" v-if="user.bio">{{ user.bio }}</p>

                        <div class="social-links" v-if="hasSocialLinks">
                            <a v-if="user.social_github" :href="user.social_github" target="_blank"
                                class="social-icon github">
                                <span class="icon">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                        viewBox="0 0 16 16">
                                        <path
                                            d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                                    </svg>
                                </span>
                            </a>
                            <a v-if="user.social_linkedin" :href="user.social_linkedin" target="_blank"
                                class="social-icon linkedin">
                                <span class="icon">💼</span>
                            </a>
                            <a v-if="user.social_instagram" :href="user.social_instagram" target="_blank"
                                class="social-icon instagram">
                                <span class="icon">📸</span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon quizzes">📚</div>
                    <div class="stat-info">
                        <h3>Total Quizzes</h3>
                        <p>{{ user.stats?.total_quizzes || 0 }}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon score">🏆</div>
                    <div class="stat-info">
                        <h3>Avg. Score</h3>
                        <p>{{ user.stats?.average_score || 0 }}%</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon joined">📅</div>
                    <div class="stat-info">
                        <h3>Joined</h3>
                        <p class="small-text">{{ user.joined_at || 'Unknown' }}</p>
                    </div>
                </div>
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
const user = ref({})
const loading = ref(true)
const error = ref(null)

const userId = route.params.id

const initials = computed(() => {
    const name = user.value.fullname || user.value.username || 'User'
    return name.substring(0, 2).toUpperCase()
})

const hasSocialLinks = computed(() => {
    return user.value.social_github || user.value.social_linkedin || user.value.social_instagram
})

const getFullImageUrl = (path) => {
    if (!path) return ''
    if (path.startsWith('http')) return path
    return `http://127.0.0.1:5000${path}`
}

const fetchProfile = async () => {
    try {
        loading.value = true
        const res = await api.get(`/users/public-profile/${userId}`)
        user.value = res.data.user
    } catch (err) {
        console.error("Failed to load profile", err)
        error.value = err.response?.data?.message || "User not found or access denied"
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchProfile()
})
</script>

<style scoped>
.public-profile-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

.back-link {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 0.9rem;
    cursor: pointer;
    margin-bottom: 1.5rem;
    padding: 0;
}

.back-link:hover {
    color: var(--primary-color);
    text-decoration: underline;
}

/* Header (Similar to Profile.vue but read-only) */
.profile-header-card {
    position: relative;
    background: var(--bg-secondary);
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
}

.header-background {
    height: 120px;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    opacity: 0.9;
}

.header-content {
    padding: 0 2rem 2rem 2rem;
    display: flex;
    align-items: flex-end;
    gap: 2rem;
    margin-top: -20px;
    /* Aligned with Profile.vue fix to prevent cut-off */
}

.avatar-wrapper {
    position: relative;
    flex-shrink: 0;
}

.avatar {
    width: 120px;
    height: 120px;
    background: #1e293b;
    color: #fff;
    border: 4px solid var(--bg-secondary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    font-weight: 700;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.avatar-img {
    width: 120px;
    height: 120px;
    border: 4px solid var(--bg-secondary);
    border-radius: 50%;
    object-fit: cover;
    background: #1e293b;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* ... existing styles ... */

.user-info {
    padding-bottom: 0.5rem;
    flex: 1;
    margin-top: 2rem;
    /* Push text down */
}

/* ... */

.bio {
    margin-top: 1rem;
    font-size: 1rem;
    line-height: 1.5;
    color: var(--text-primary);
    max-width: 650px;
    white-space: pre-wrap;
    word-break: break-word;
    /* Safety for long words */
}

.name-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.25rem;
}

.name-row h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    color: var(--text-primary);
}

.badge {
    padding: 0.25rem 0.6rem;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
}

.email {
    color: var(--text-secondary);
    font-size: 1rem;
    margin: 0;
}

.qualification {
    color: var(--primary-color);
    font-weight: 500;
    margin: 0.25rem 0 0 0;
    font-size: 0.9rem;
}

.social-links {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.social-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    transition: all 0.2s;
    text-decoration: none;
    font-size: 1.2rem;
}

.social-icon:hover {
    background: var(--bg-accent);
    transform: translateY(-2px);
}

/* Stats */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.stat-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.stat-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.stat-icon.quizzes {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.stat-icon.score {
    background: rgba(234, 179, 8, 0.1);
    color: #eab308;
}

.stat-icon.joined {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.stat-info h3 {
    margin: 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.stat-info p {
    margin: 0.2rem 0 0 0;
    font-size: 1.4rem;
    font-weight: 700;
}

.stat-info .small-text {
    font-size: 1rem;
    font-weight: 600;
}

.loading-state,
.error-state {
    text-align: center;
    padding: 5rem;
    color: var(--text-secondary);
}

.loader {
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1.5rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.btn-back {
    margin-top: 1rem;
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
}

@media (max-width: 800px) {
    .header-content {
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    .name-row {
        justify-content: center;
    }

    .social-links {
        justify-content: center;
    }
}
</style>

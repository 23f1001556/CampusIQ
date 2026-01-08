<template>
    <div class="profile-container">
        <!-- Header Section -->
        <div class="profile-header-card">
            <div class="header-background"></div>
            <div class="header-content">
                <div class="avatar-wrapper" @click="triggerFileInput">
                    <img v-if="user.profile_picture" :src="getFullImageUrl(user.profile_picture)" class="avatar-img"
                        alt="Profile" />
                    <div v-else class="avatar">{{ initials }}</div>

                    <div class="upload-overlay">
                        <span class="camera-icon">📷</span>
                    </div>
                    <div class="status-indicator"></div>
                    <input type="file" ref="fileInput" class="hidden-input" accept="image/*"
                        @change="handleFileUpload" />
                </div>

                <div class="user-info">
                    <div class="name-row">
                        <h1>{{ user.fullname || user.username }}</h1>
                        <span v-if="user.isadmin" class="badge admin-badge">Admin</span>
                    </div>
                    <p class="email">{{ user.email }}</p>
                    <p class="qualification" v-if="user.qualification">{{ user.qualification }}</p>

                    <p class="bio" v-if="user.bio">{{ user.bio }}</p>

                    <div class="social-links" v-if="hasSocialLinks">
                        <a v-if="user.social_github" :href="user.social_github" target="_blank"
                            class="social-icon github" title="GitHub">
                            <span class="icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                    viewBox="0 0 16 16">
                                    <path
                                        d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                                </svg>
                            </span>
                        </a>
                        <a v-if="user.social_linkedin" :href="user.social_linkedin" target="_blank"
                            class="social-icon linkedin" title="LinkedIn">
                            <span class="icon">💼</span>
                        </a>
                        <a v-if="user.social_instagram" :href="user.social_instagram" target="_blank"
                            class="social-icon instagram" title="Instagram">
                            <span class="icon">📸</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid" v-if="!user.isadmin">
            <div class="stat-card">
                <div class="stat-icon quizzes">📚</div>
                <div class="stat-info">
                    <h3>Total Quizzes</h3>
                    <p>{{ stats.total_quizzes }}</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon score">🏆</div>
                <div class="stat-info">
                    <h3>Avg. Score</h3>
                    <p>{{ stats.average_score }}%</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon active">🔥</div>
                <div class="stat-info">
                    <h3>Days Active</h3>
                    <p>{{ stats.days_active }}</p>
                </div>
            </div>
        </div>

        <div class="main-content-grid" :class="{ 'admin-grid': user.isadmin }">
            <!-- Edit Profile Section -->
            <div class="content-card edit-profile">
                <h2>Edit Profile</h2>
                <form @submit.prevent="saveProfile" class="modern-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input v-model="form.fullname" maxlength="30" placeholder="John Doe" />
                        </div>
                        <div class="form-group">
                            <label>Qualification</label>
                            <input v-model="form.qualification" maxlength="30"
                                placeholder="e.g. BSc Computer Science" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Bio (Max 40 chars)</label>
                        <input v-model="form.bio" maxlength="40" placeholder="Short bio (e.g. Data Scientist)" />
                    </div>

                    <div class="form-group">
                        <label>Social Profiles</label>
                        <div class="social-inputs">
                            <div class="social-input-group">
                                <span class="input-icon">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                        viewBox="0 0 16 16">
                                        <path
                                            d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                                    </svg>
                                </span>
                                <input v-model="form.social_github" maxlength="100" placeholder="GitHub URL" />
                            </div>
                            <div class="social-input-group">
                                <span class="input-icon">💼</span>
                                <input v-model="form.social_linkedin" maxlength="100" placeholder="LinkedIn URL" />
                            </div>
                            <div class="social-input-group">
                                <span class="input-icon">📸</span>
                                <input v-model="form.social_instagram" maxlength="100" placeholder="Instagram URL" />
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Date of Birth</label>
                        <input type="date" v-model="form.dob" />
                    </div>

                    <div class="divider"></div>
                    <div class="ai-config-section">
                        <h3>AI Configuration</h3>
                        <p class="section-desc">Provide your own Gemini API key for AI features, or leave blank to use
                            system default.</p>
                        <div class="form-group">
                            <label>Gemini API Key</label>
                            <input type="password" v-model="form.gemini_api_key"
                                placeholder="enter your gemini api key here " class="api-key-input" />
                            <small class="help-text">Your key is stored securely using industry-standard
                                encryption.</small>
                        </div>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn-save" :disabled="saving">
                            <span v-if="saving">Saving...</span>
                            <span v-else>Save Changes</span>
                        </button>
                    </div>
                </form>
            </div>

            <!-- Recent Activity Section -->
            <div class="content-card recent-activity">
                <h2>Recent Activity</h2>
                <div v-if="stats.recent_activity && stats.recent_activity.length > 0" class="activity-list">
                    <div v-for="(activity, index) in stats.recent_activity" :key="index" class="activity-item">
                        <div class="activity-icon" :class="activity.type.toLowerCase()">
                            <template v-if="activity.type === 'Standard'">📝</template>
                            <template v-else-if="activity.type === 'Mock'">🤖</template>
                            <template v-else-if="activity.type === 'Action'">⚡</template>
                        </div>
                        <div class="activity-details">
                            <span class="activity-title">{{ activity.title }}</span>
                            <span class="activity-meta" v-if="activity.details">{{ activity.details }}</span>
                            <span class="activity-meta" v-else>{{ activity.type }} Quiz • {{ activity.date }}</span>
                        </div>
                        <div class="activity-score" v-if="activity.score !== undefined"
                            :class="getScoreClass(activity.score)">
                            {{ activity.score }} pts
                        </div>
                        <div class="activity-date" v-else>
                            {{ activity.date }}
                        </div>
                    </div>
                </div>
                <div v-else class="empty-state">
                    <p>No recent activity found.</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const user = ref({})
const stats = ref({
    total_quizzes: 0,
    average_score: 0,
    days_active: 0,
    recent_activity: []
})

const form = ref({
    fullname: '',
    qualification: '',
    dob: '',
    gemini_api_key: '',
    bio: '',
    social_github: '',
    social_linkedin: '',
    social_instagram: ''
})
const saving = ref(false)
const fileInput = ref(null)

const initials = computed(() => {
    const name = user.value.fullname || user.value.username || 'User'
    return name.substring(0, 2).toUpperCase()
})

const hasSocialLinks = computed(() => {
    return user.value.social_github || user.value.social_linkedin || user.value.social_instagram
})

const getFullImageUrl = (path) => {
    if (!path) return ''
    // If backend returns absolute URL or one starting with http, return as is
    if (path.startsWith('http')) return path
    // Otherwise prepend API base URL if needed, or if it's relative to root
    // Assuming backend serves static from root or we need to point to backend host
    return `http://127.0.0.1:5000${path}`
}

const triggerFileInput = () => {
    fileInput.value.click()
}

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
        const res = await api.post('/users/profile-picture', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        // Update user profile picture immediately
        user.value.profile_picture = res.data.url
        alert("Profile picture updated!")
    } catch (error) {
        console.error(error)
        alert(error.response?.data?.message || "Failed to upload image")
    }
}

const fetchProfile = async () => {
    try {
        const res = await api.get('/users/profile')
        user.value = res.data.user
        stats.value = res.data.stats

        // Populate form
        form.value.fullname = user.value.fullname || ''
        form.value.qualification = user.value.qualification || ''
        form.value.dob = user.value.dob || ''
        form.value.gemini_api_key = user.value.gemini_api_key || ''
        form.value.bio = user.value.bio || ''
        form.value.social_github = user.value.social_github || ''
        form.value.social_linkedin = user.value.social_linkedin || ''
        form.value.social_instagram = user.value.social_instagram || ''
    } catch (error) {
        console.error("Failed to load profile", error)
    }
}

const saveProfile = async () => {
    saving.value = true
    try {
        await api.put('/users/profile', form.value)
        await fetchProfile()
        alert("Profile updated successfully")
    } catch (error) {
        console.error(error)
        alert("Failed to update profile")
    } finally {
        saving.value = false
    }
}

const getScoreClass = (score) => {
    if (score >= 80) return 'score-high'
    if (score >= 50) return 'score-medium'
    return 'score-low'
}

onMounted(() => {
    fetchProfile()
})
</script>

<style scoped>
.profile-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

/* Header Card */
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
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    opacity: 0.9;
}

.header-content {
    padding: 0 2rem 2rem 2rem;
    display: flex;
    align-items: flex-end;
    gap: 2rem;
    margin-top: -20px;
    /* Reduced overlap to prevent text being cut */
}

.avatar-wrapper {
    position: relative;
    cursor: pointer;
    transition: transform 0.2s;
}

.avatar-wrapper:hover .upload-overlay {
    opacity: 1;
}

.avatar-wrapper:active {
    transform: scale(0.95);
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

.upload-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.2s;
    border: 4px solid transparent;
    /* Match border width to keep size same */
}

.camera-icon {
    font-size: 1.5rem;
    color: white;
}

.hidden-input {
    display: none;
}

.status-indicator {
    position: absolute;
    bottom: 10px;
    right: 10px;
    width: 20px;
    height: 20px;
    background: #22c55e;
    border: 3px solid var(--bg-secondary);
    border-radius: 50%;
}

.user-info {
    padding-bottom: 0.5rem;
    flex: 1;
    margin-top: 2rem;
    /* Pushes text down below the avatar/banner overlap */
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

.bio {
    margin-top: 0.75rem;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.5;
    max-width: 600px;
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
    transform: translateY(-2px);
    background: var(--bg-accent);
}

.badge {
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.admin-badge {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
}

.stat-icon.quizzes {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.stat-icon.score {
    background: rgba(234, 179, 8, 0.1);
    color: #eab308;
}

.stat-icon.active {
    background: rgba(236, 72, 153, 0.1);
    color: #ec4899;
}

.stat-info h3 {
    margin: 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.stat-info p {
    margin: 0.25rem 0 0 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
}

/* Main Content Grid */
.main-content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.main-content-grid.admin-grid {
    grid-template-columns: 1fr;
}

@media (max-width: 900px) {

    .main-content-grid,
    .main-content-grid.admin-grid {
        grid-template-columns: 1fr;
    }

    .header-content {
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding-bottom: 1.5rem;
    }

    .name-row {
        justify-content: center;
    }

    .bio {
        text-align: center;
        margin-left: auto;
        margin-right: auto;
    }

    .social-links {
        justify-content: center;
    }
}

.content-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid var(--border-color);
}

.content-card h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
}

/* Form Styles */
.modern-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
}

.form-group input,
.bio-input {
    padding: 0.875rem 1rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 0.95rem;
    transition: all 0.2s;
    font-family: inherit;
}

.bio-input {
    resize: vertical;
    min-height: 80px;
}

.form-group input:focus,
.bio-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.social-inputs {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.social-input-group {
    display: flex;
    align-items: center;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    overflow: hidden;
}

.social-input-group .input-icon {
    padding: 0 0.8rem;
    font-size: 1.1rem;
    color: var(--text-secondary);
}

.social-input-group input {
    border: none;
    border-radius: 0;
    flex: 1;
    padding-left: 0;
}

.social-input-group input:focus {
    box-shadow: none;
}

.social-input-group:focus-within {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn-save {
    width: 100%;
    padding: 1rem;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.btn-save:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.btn-save:disabled {
    opacity: 0.7;
    cursor: default;
}

.divider {
    height: 1px;
    background: var(--border-color);
    margin: 2rem 0;
}

.ai-config-section h3 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
    border: none;
    padding: 0;
}

.section-desc {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
}

.help-text {
    display: block;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.api-key-input {
    letter-spacing: 0.1rem;
    font-family: monospace;
}

/* Activity List */
.activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.activity-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--bg-primary);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    transition: transform 0.2s;
}

.activity-item:hover {
    transform: translateX(4px);
    border-color: var(--primary-color);
}

.activity-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
}

.activity-icon.standard {
    background: rgba(59, 130, 246, 0.1);
}

.activity-icon.mock {
    background: rgba(168, 85, 247, 0.1);
}

.activity-icon.action {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

.activity-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.activity-title {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.95rem;
}

.activity-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.activity-score {
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    background: var(--bg-secondary);
}

.activity-date {
    font-size: 0.8rem;
    color: var(--text-secondary);
    padding: 0.25rem 0.75rem;
    background: var(--bg-secondary);
    border-radius: 8px;
    background: var(--bg-secondary);
}

.score-high {
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
}

.score-medium {
    color: #f59e0b;
    background: rgba(245, 158, 11, 0.1);
}

.score-low {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
}

.empty-state {
    text-align: center;
    color: var(--text-secondary);
    padding: 2rem;
    font-style: italic;
}
</style>

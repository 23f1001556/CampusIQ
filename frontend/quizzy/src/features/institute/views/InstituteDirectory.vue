<template>
    <div class="directory-container">
        <!-- Header -->
        <div class="directory-header">
            <div class="header-text">
                <h1>Institute Directory</h1>
                <p>Browse and connect with peers within your institute.</p>
            </div>
            <div class="search-wrapper">
                <span class="search-icon">🔍</span>
                <input v-model="searchQuery" @input="debouncedSearch" placeholder="Search students, managers..."
                    class="search-input" />
            </div>
        </div>

        <!-- Directory Grid -->
        <div v-if="loading" class="loading-state">
            <div class="loader"></div>
            <p>Loading directory...</p>
        </div>

        <div v-else-if="users.length === 0" class="empty-state">
            <div class="empty-icon">👥</div>
            <h3>No users found</h3>
            <p>Try adjusting your search terms.</p>
        </div>

        <div v-else class="users-grid">
            <div v-for="user in users" :key="user.id" class="user-card" @click="viewProfile(user.id)">
                <div class="card-header">
                    <img v-if="user.profile_picture" :src="getFullImageUrl(user.profile_picture)" class="avatar-img" />
                    <div v-else class="avatar-placeholder">{{ getInitials(user) }}</div>

                    <span v-if="user.role !== 'user'" class="role-badge" :class="user.role">
                        {{ user.role }}
                    </span>
                </div>

                <div class="card-body">
                    <h3>{{ user.fullname || user.username }}</h3>
                    <p class="qualification">{{ user.qualification || 'Student' }}</p>
                    <p class="bio-snippet" v-if="user.bio">{{ truncateBio(user.bio) }}</p>
                </div>

                <div class="card-footer">
                    <button class="view-btn">View Profile</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import debounce from 'lodash/debounce' // Standard lodash or simple timeout

const router = useRouter()
const users = ref([])
const loading = ref(true)
const searchQuery = ref('')
const error = ref(null)

const getFullImageUrl = (path) => {
    if (!path) return ''
    if (path.startsWith('http')) return path
    return `http://127.0.0.1:5000${path}`
}

const getInitials = (user) => {
    const name = user.fullname || user.username || 'User'
    return name.substring(0, 2).toUpperCase()
}

const truncateBio = (bio) => {
    if (!bio) return ''
    return bio.length > 60 ? bio.substring(0, 60) + '...' : bio
}

const fetchDirectory = async () => {
    try {
        loading.value = true
        const res = await api.get('/users/directory', {
            params: { search: searchQuery.value }
        })
        users.value = res.data.users
    } catch (err) {
        console.error("Failed to fetch directory", err)
        error.value = "Failed to load directory"
    } finally {
        loading.value = false
    }
}

const debouncedSearch = debounce(() => {
    fetchDirectory()
}, 300)

const viewProfile = (userId) => {
    router.push({ name: 'PublicProfile', params: { id: userId } })
}

onMounted(() => {
    fetchDirectory()
})
</script>

<style scoped>
.directory-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

.directory-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3rem;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.header-text h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #fff, #999);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-text p {
    color: var(--text-secondary);
}

.search-wrapper {
    position: relative;
    width: 300px;
}

.search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-secondary);
}

.search-input {
    width: 100%;
    padding: 0.8rem 1rem 0.8rem 2.8rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    color: white;
    font-size: 0.95rem;
    transition: all 0.2s;
}

.search-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Grid */
.users-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
}

.user-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 1.5rem;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.user-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    border-color: var(--primary-color);
}

.card-header {
    position: relative;
    margin-bottom: 1rem;
}

.avatar-img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--bg-primary);
}

.avatar-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 700;
    border: 3px solid var(--bg-primary);
}

.role-badge {
    position: absolute;
    bottom: 0;
    right: -10px;
    background: var(--bg-tertiary);
    /* fallback */
    padding: 0.2rem 0.6rem;
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    border: 2px solid var(--bg-secondary);
}

.role-badge.manager {
    background: #f59e0b;
    color: black;
}

.role-badge.admin {
    background: #ef4444;
    color: white;
}

.card-body h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0.5rem 0 0.2rem 0;
    color: var(--text-primary);
}

.qualification {
    font-size: 0.85rem;
    color: var(--primary-color);
    margin-bottom: 0.8rem;
}

.bio-snippet {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.4;
    margin-bottom: 1rem;
    min-height: 40px;
    /* Force consistent height */
}

.card-footer {
    margin-top: auto;
    width: 100%;
}

.view-btn {
    width: 100%;
    padding: 0.6rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    color: var(--text-secondary);
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
}

.user-card:hover .view-btn {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

.loading-state,
.empty-state {
    text-align: center;
    padding: 4rem;
    color: var(--text-secondary);
}

.loader {
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@media (max-width: 768px) {
    .directory-header {
        flex-direction: column;
        align-items: stretch;
    }

    .search-wrapper {
        width: 100%;
    }
}
</style>

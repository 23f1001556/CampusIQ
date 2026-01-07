<template>
    <div class="demo-page">
        <!-- Minimal Nav -->
        <nav class="nav-bar">
            <router-link to="/" class="logo">
                <span class="logo-icon">⚡</span>
                <span class="logo-text">Quizzy</span>
            </router-link>
            <router-link to="/register" class="btn-primary-sm">Start Free Trial</router-link>
        </nav>

        <!-- Hero Video Section -->
        <section class="demo-hero">
            <div class="container">
                <div class="pill-badge">Product Tour</div>
                <h1>See Quizzy in <span class="gradient-text">Action</span></h1>
                <p class="subtitle">Discover how our AI-driven platform transforms the way you study and prepare for
                    exams.</p>

                <div class="video-container">
                    <div class="video-mockup">
                        <div class="video-overlay" v-if="!isPlaying" @click="isPlaying = true">
                            <div class="play-button">
                                <span class="play-icon">▶</span>
                            </div>
                            <p>Click to Watch Demo</p>
                        </div>
                        <!-- Using a placeholder image for the video -->
                        <img src="https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&q=80&w=1000"
                            alt="App Demo Mockup" class="demo-img" />

                        <div class="video-controls" v-if="isPlaying">
                            <div class="progress-bar">
                                <div class="progress" style="width: 45%;"></div>
                            </div>
                            <div class="controls-row">
                                <span>⏸</span>
                                <span>02:14 / 05:00</span>
                                <div class="spacer"></div>
                                <span>🔊</span>
                                <span>⛶</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Perks Section -->
        <section class="perks">
            <div class="container">
                <div class="section-header">
                    <h2>Why Students <span class="gradient-text">Love</span> Quizzy</h2>
                    <p>Designed to solve the biggest challenges in modern education.</p>
                </div>

                <div class="perks-grid">
                    <div class="perk-card">
                        <div class="perk-icon">🚀</div>
                        <h4>3x Faster Prep</h4>
                        <p>Generate comprehensive study materials and quizzes instantly, saving hours of manual
                            note-taking.</p>
                    </div>
                    <div class="perk-card">
                        <div class="perk-icon">🎯</div>
                        <h4>Precision focus</h4>
                        <p>AI identifies exactly where you struggle, ensuring you never waste time on what you already
                            know.</p>
                    </div>
                    <div class="perk-card">
                        <div class="perk-icon">🛡️</div>
                        <h4>Exam Readiness</h4>
                        <p>Our strict mock mode builds real-world exam confidence while maintaining total academic
                            integrity.</p>
                    </div>
                    <div class="perk-card">
                        <div class="perk-icon">📱</div>
                        <h4>Study Anywhere</h4>
                        <p>A fully responsive interface that works perfectly on your phone, tablet, or laptop.</p>
                    </div>
                    <div class="perk-card">
                        <div class="perk-icon">🏛️</div>
                        <h4>Institutional Control</h4>
                        <p>Colleges and faculty gain full governance—managing subjects and creating faculty-led graded
                            quizzes for total curriculum control.</p>
                    </div>
                    <div class="perk-card">
                        <div class="perk-icon">👨‍🏫</div>
                        <h4>Faculty Insights</h4>
                        <p>Institutes can monitor entire batches with centralized dashboards, tracking progress to
                            maintain high academic standards.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Call to Action -->
        <section class="cta-section">
            <div class="cta-card">
                <h2>Ready to transform your grades?</h2>
                <p>Join thousands of students staying ahead of the curve with Quizzy.</p>
                <div class="cta-actions">
                    <router-link to="/register" class="btn-hero-primary">Create Account</router-link>
                    <router-link to="/login" class="btn-hero-secondary">Login</router-link>
                </div>
            </div>
        </section>

        <footer class="footer">
            <p>&copy; 2026 Quizzy. Your AI Study Partner.</p>
        </footer>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const isPlaying = ref(false);
</script>

<style scoped>
.demo-page {
    min-height: 100vh;
    background: #0f172a;
    color: white;
    font-family: 'Inter', sans-serif;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 5%;
}

/* Nav */
.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 5%;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 100;
}

.logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.5rem;
    font-weight: 800;
    text-decoration: none;
    color: white;
}

.logo-icon {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.btn-primary-sm {
    padding: 0.6rem 1.2rem;
    background: #6366f1;
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
}

/* Hero */
.demo-hero {
    padding: 6rem 0 4rem;
    text-align: center;
}

.pill-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 100px;
    color: #818cf8;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.demo-hero h1 {
    font-size: clamp(2.5rem, 5vw, 3.5rem);
    font-weight: 800;
    margin-bottom: 1rem;
}

.gradient-text {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    font-size: 1.25rem;
    color: #94a3b8;
    margin-bottom: 4rem;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

/* Video Player Mockup */
.video-container {
    max-width: 900px;
    margin: 0 auto;
}

.video-mockup {
    position: relative;
    background: #1e293b;
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);
}

.demo-img {
    width: 100%;
    aspect-ratio: 16/9;
    object-fit: cover;
    opacity: 0.6;
}

.video-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, 0.4);
    z-index: 10;
    cursor: pointer;
    transition: background 0.3s;
}

.video-overlay:hover {
    background: rgba(15, 23, 42, 0.2);
}

.play-button {
    width: 80px;
    height: 80px;
    background: #6366f1;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    box-shadow: 0 0 30px rgba(99, 102, 241, 0.5);
    transition: transform 0.2s;
}

.video-overlay:hover .play-button {
    transform: scale(1.1);
}

.play-icon {
    font-size: 2rem;
    margin-left: 5px;
}

.video-controls {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem 1.5rem;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.progress-bar {
    height: 4px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
}

.progress {
    height: 100%;
    background: #6366f1;
    border-radius: 2px;
}

.controls-row {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    font-size: 0.9rem;
    color: #e2e8f0;
}

.spacer {
    flex: 1;
}

/* Perks */
.perks {
    padding: 8rem 0;
}

.section-header {
    text-align: center;
    margin-bottom: 4rem;
}

.section-header h2 {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
}

.perks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.perk-card {
    background: rgba(255, 255, 255, 0.03);
    padding: 2.5rem;
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: transform 0.3s;
}

.perk-card:hover {
    transform: translateY(-5px);
    border-color: rgba(99, 102, 241, 0.3);
}

.perk-icon {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
}

.perk-card h4 {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.perk-card p {
    color: #94a3b8;
    line-height: 1.6;
}

/* CTA Section */
.cta-section {
    padding: 4rem 5% 8rem;
}

.cta-card {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    padding: 4rem;
    border-radius: 32px;
    text-align: center;
    max-width: 1000px;
    margin: 0 auto;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.cta-card h2 {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
}

.cta-card p {
    color: #c7d2fe;
    font-size: 1.25rem;
    margin-bottom: 2.5rem;
}

.cta-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
}

.btn-hero-primary {
    padding: 1rem 2rem;
    background: #6366f1;
    color: white;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.2s;
}

.btn-hero-secondary {
    padding: 1rem 2rem;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 600;
}

.footer {
    text-align: center;
    padding: 4rem 5%;
    color: #475569;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

@media (max-width: 768px) {
    .cta-card {
        padding: 3rem 1.5rem;
    }

    .cta-actions {
        flex-direction: column;
    }
}
</style>

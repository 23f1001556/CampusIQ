# Quizzy - AI-Powered Learning & Assessment Platform

Quizzy is a modern, full-stack web application designed to revolutionize how quizzes and assessments are managed and taken. It combines a robust **Flask** backend with a dynamic **Vue.js** frontend to deliver a seamless learning experience, featuring AI-generated content, detailed analytics, and institutional management.

## 🚀 Key Features

- **🤖 AI-Powered Quiz Generation**: Integrated with **Google Gemini AI** to automatically generate quiz questions based on specific topics or uploaded PDF study materials.
- **👥 Role-Based Access Control (RBAC)**:
  - **Admin**: Full system control, user management, and global statistics.
  - **Manager**: Institute-level management, restricted to specific domains (e.g., `@alpha.edu`), with filtered user views and analytics.
  - **User (Student)**: Take quizzes, view progress, and access the institute directory.
- **🏛️ Institute Directory**: Domain-scoped user discovery, allowing students and staff within the same organization to connect.
- **📊 Advanced Analytics**: Detailed performance tracking, leaderboards, and score trends for both individuals and managers.
- **👤 Public Profiles**: Shareable user profiles showcasing achievements, bio, and social links with privacy safeguards.

---

## 🏗️ Backend Architecture

The backend is built with **Python (Flask)**, adhering to professional software engineering principles for scalability and maintainability.

### 1. Application Factory Pattern

The core utilizes the **Application Factory** pattern (`create_app`), ensuring:

- **Circular Import Prevention**: Models and routes are initialized cleanly.
- **Testing capabilities**: Easy creation of separate instances for unit testing.
- **Configuration Management**: Seamless switching between `Development`, `Testing`, and `Production` environments.

### 2. Modular Blueprint Structure

The codebase is organized into **Blueprints**, enforcing a clear separation of concerns:

- `auth`: Authentication (Login, Register, JWT handling).
- `users`: User profile management, directory search, and public profiles.
- `subjects/chapters`: Hierarchical content management.
- `quiz`: Quiz logic, attempting, and scoring.
- `ai`: Dedicated service layer for LLM interactions.

### 3. Database Modeling (SQLAlchemy)

A robust relational schema (SQLite/PostgreSQL) handles complex data relationships:

- **Users**: normalized with role flags and profile metadata.
- **Content Hierarchy**: `Subject` -> `Chapter` -> `Quiz` -> `Question`.
- **Performance**: `Scores`, `MockAttempt` for tracking user progress.

### 4. Security & Optimization

- **JWT Authentication**: Stateless, secure API access.
- **Decorators**: Custom `@admin_required` and `@manager_required` decorators for granular route protection.
- **Domain Scoping**: Logic to strictly isolate data for Managers based on email domains.

---

## 🛠️ Tech Stack

### Backend

- **Framework**: Flask (Python 3.10+)
- **ORM**: SQLAlchemy
- **AI Engine**: Google Gemini API
- **Task Queue**: Celery & Redis (ready for async tasks)
- **Authentication**: Flask-JWT-Extended

### Frontend

- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **State Management**: Pinia / Reactive State
- **Styling**: Custom CSS (Glassmorphism & Dark Mode)

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Redis (Optional, for Celery tasks)

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/quizzy.git
cd quizzy/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set Environment Variables (.env)
cp .env.example .env
# Configure JWT_SECRET_KEY, GEMINI_API_KEY, etc.

# Initialize Database
flask db upgrade
# OR run the seed script for test data
python seed.py

# Run Server
flask run
```

### 2. Frontend Setup

```bash
cd ../frontend/quizzy

# Install dependencies
npm install

# Run Development Server
npm run dev
```

## 🧪 Testing

The backend includes test infrastructure. Run tests using:

```bash
cd backend
pytest
```

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).

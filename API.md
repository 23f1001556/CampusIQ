# Quizzy API Documentation

This documentation provides a comprehensive guide to the backend API endpoints. All authenticated routes require a valid **JWT Token** in the `Authorization` header (`Bearer <token>`).

Base URL: `/` (Relative to server host)

---

## 🔐 Authentication Module (`/auth`)

### Register User

- **Endpoint**: `POST /auth/register`
- **Description**: Creates a new user account (Student or Manager). Sends verification email.
- **Body**:
  ```json
  {
    "username": "john_doe",
    "email": "john@alpha.edu",
    "password": "StrongPassword123!"
  }
  ```
- **Response**: `201 Created`

### Login

- **Endpoint**: `POST /auth/login`
- **Description**: Authenticates user and returns access token.
- **Body**:
  ```json
  {
    "email": "john@alpha.edu",
    "password": "StrongPassword123!"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "token": "eyJh...",
    "user": { "id": 1, "username": "john", "role": "user" }
  }
  ```

### Get Current User

- **Endpoint**: `GET /auth/getme`
- **Description**: Retrieves details of the currently logged-in user.
- **Auth**: Required.

### Forbidden/Reset Password

- **Endpoint**: `POST /auth/forgot_password`
- **Body**: `{ "email": "..." }`
- **Endpoint**: `POST /auth/reset_password/<token>`
- **Body**: `{ "password": "..." }`

---

## 👤 User Management (`/users`)

### Get Profile

- **Endpoint**: `GET /users/profile`
- **Description**: Get full profile details including stats and bio.
- **Auth**: Required.

### Update Profile

- **Endpoint**: `PUT /users/profile`
- **Description**: Update personal information.
- **Body**:
  ```json
  {
    "fullname": "John Doe",
    "bio": "CS Student",
    "qualification": "B.Tech",
    "social_github": "https://github.com/..."
  }
  ```

### Institute Directory

- **Endpoint**: `GET /users/directory`
- **Description**: Search for other students/managers within the same institute domain.
- **Query Params**: `?search=name`

### Public Profile

- **Endpoint**: `GET /users/public-profile/<user_id>`
- **Description**: View another user's public profile stats and info.

---

## 📚 Content Management (`/subjects`)

### List Subjects

- **Endpoint**: `GET /subjects`
- **Description**: Get all subjects created by the current user (Admin/Manager).

### Create Subject

- **Endpoint**: `POST /subjects`
- **Body**: `{ "name": "Physics", "description": "..." }`

### Create Chapter

- **Endpoint**: `POST /subjects/<subject_id>/chapters`
- **Body**: `{ "name": "Thermodynamics", "description": "..." }`

---

## 🎯 Quiz Management (`/quiz`)

### Create Quiz (Manual)

- **Endpoint**: `POST /quiz/createquiz`
- **Description**: Create a new quiz container.
- **Body**:
  ```json
  {
    "name": "Mid-Term Exam",
    "chapter_id": 5,
    "time_duration": 30,
    "date_of_quiz": "2024-05-20 10:00:00"
  }
  ```

### Add Questions

- **Endpoint**: `POST /quiz/add_questions/<quiz_id>`
- **Body**:
  ```json
  {
    "questions": [
      {
        "question_statement": "What is 2+2?",
        "option_1": "3",
        "option_2": "4",
        "option_3": "5",
        "option_4": "6",
        "correct_option": "2" // Corresponds to option_2
      }
    ]
  }
  ```

### Submit Quiz Attempt

- **Endpoint**: `POST /quiz/submit`
- **Description**: Submit answers for grading.
- **Body**:
  ```json
  {
    "quiz_id": 10,
    "answers": {
      "101": "2", // QuestionID: SelectedOption
      "102": "1"
    }
  }
  ```

### Get Result

- **Endpoint**: `GET /quiz/get_result/<score_id>`
- **Description**: Get detailed question-wise analysis of an attempt.

### Leaderboard

- **Endpoint**: `GET /quiz/leaderboard`
- **Description**: Global ranking of students based on total score.

---

## 🤖 AI Services (`/ai`)

### Analyze PDF

- **Endpoint**: `POST /ai/analyze`
- **Description**: Upload study material to generate summary or quiz topics.
- **Body**: Multipart Form Data (`file`: pdf/txt)

### Generate Quiz (AI)

- **Endpoint**: `POST /quiz/generate-ai` (or via AI Hub flow)
- **Description**: Request LLM to generate questions based on analyzed context.

---

## 🏛️ Admin & Analytics (`/admin`, `/institute`)

### Admin Stats

- **Endpoint**: `GET /admin/stats`
- **Description**: System-wide user and content metrics.

### Institute Stats (Manager)

- **Endpoint**: `GET /institute/stats`
- **Description**: Metrics scoped to the manager's email domain (e.g., total students in `@alpha.edu`).

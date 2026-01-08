import { createRouter, createWebHistory } from 'vue-router'
import Login from '../features/auth/views/Login.vue'
import Register from '../features/auth/views/Register.vue'

import LandingPage from '../features/landing/views/LandingPage.vue'
import DemoView from '../features/landing/views/DemoView.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },
  {
    path: '/demo',
    name: 'Demo',
    component: DemoView
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/dashboard',
    component: () => import('../layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
        {
            path: 'admin',
            name: 'AdminDashboard',
            component: () => import('../features/admin/views/AdminDashboard.vue'),
            meta: { requiresAdmin: true }
        },
        {
            path: 'manager',
            name: 'ManagerDashboard',
            component: () => import('../features/admin/views/ManagerDashboard.vue'),
            meta: { requiresManager: true }
        },
        {
            path: '',
            name: 'Overview',
            component: () => import('../features/dashboard/views/DashboardHome.vue')
        },
        {
            path: 'profile',
            name: 'Profile',
            component: () => import('../features/profile/views/Profile.vue')
        },

        {
            path: 'subjects',
            name: 'Subjects',
            component: () => import('../features/subjects/views/SubjectList.vue'),
            // meta: { requiresNonAdmin: true }
        },
        {
            path: 'subjects/:id',
            name: 'SubjectDetail',
            component: () => import('../features/subjects/views/SubjectDetail.vue'),
            // meta: { requiresNonAdmin: true }
        },
        {
            path: 'mock-quizzes',
            name: 'MockList',
            component: () => import('../features/mock-quizzes/views/MockList.vue')
        },
        {
            path: 'mock-attempt/:id',
            name: 'MockAttempt',
            component: () => import('../features/mock-quizzes/views/MockAttempt.vue'),
            meta: { fullScreen: true }
        },
        {
            path: 'mock-result/:id',
            name: 'MockResult',
            component: () => import('../features/mock-quizzes/views/MockResult.vue')
        },
        {
            path: 'subjects/:subjectId/chapters/:chapterId/quizzes',
            name: 'ChapterQuizList',
            component: () => import('../features/subjects/views/ChapterQuizList.vue')
        },
        {
            path: 'quiz/result/:id',
            name: 'QuizResult',
            component: () => import('../features/subjects/views/QuizResult.vue')
        },
        {
            path: 'quiz/:id/attempt',
            name: 'QuizAttempt',
            component: () => import('../features/subjects/views/QuizAttempt.vue')
        },
        {
            path: 'leaderboard',
            name: 'Leaderboard',
            component: () => import('../features/leaderboard/views/Leaderboard.vue')
        },
        {
            path: 'ai-hub',
            name: 'AIHub',
            component: () => import('../features/ai-analysis/views/AIHub.vue')
        },
        {
            path: 'institute',
            name: 'institute',
            component: () => import('../features/institute/views/InstituteView.vue')
        },
        {
            path: 'institute/:id',
            name: 'course-detail',
            component: () => import('../features/institute/views/CourseDetail.vue')
        },
        {
            path: 'institute/saved',
            name: 'saved-content',
            component: () => import('../features/institute/views/SavedContent.vue')
        },
        {
            path: 'subjects/:subjectId/chapters/:chapterId/quizzes/create',
            name: 'ManualQuizCreator',
            component: () => import('../features/subjects/views/ManualQuizCreator.vue')
        },
        {
            path: 'subjects/:subjectId/chapters/:chapterId/quizzes/:quizId/edit',
            name: 'ManualQuizEditor',
            component: () => import('../features/subjects/views/ManualQuizCreator.vue')
        }
    ]
  },
  {
    path: '/verify-email/:token',
    name: 'VerifyEmail',
    component: () => import('../features/auth/views/VerifyEmail.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../features/auth/views/ForgotPassword.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next('/login')
    } else {
      // Check for admin requirement
      if (to.matched.some(record => record.meta.requiresAdmin)) {
        try {
          const user = JSON.parse(localStorage.getItem('user'))
          if (user && (user.isadmin || user.role === 'admin')) {
            next()
          } else {
             // Redirect to dashboard if not admin
             next('/dashboard')
          }
        } catch (e) {
          next('/login')
        }
      } else if (to.matched.some(record => record.meta.requiresManager)) {
        // Manager-only pages
        try {
          const user = JSON.parse(localStorage.getItem('user'))
          if (user && user.role === 'manager') {
            next()
          } else if (user && (user.isadmin || user.role === 'admin')) {
            // Redirect admins to their dashboard
            next('/dashboard/admin')
          } else {
            next('/dashboard')
          }
        } catch (e) {
          next('/login')
        }
      } else if (to.matched.some(record => record.meta.requiresNonAdmin)) {
        // Prevent admins from accessing certain pages like subjects
        try {
          const user = JSON.parse(localStorage.getItem('user'))
          if (user && (user.isadmin || user.role === 'admin')) {
            // Redirect admins away from non-admin pages
            next('/dashboard/admin')
          } else {
            next()
          }
        } catch (e) {
          next()
        }
      } else {
        next()
      }
    }
  } else {
    // Prevent logged-in users from visiting landing, demo, login, or register
    if (token && (to.path === '/' || to.path === '/demo' || to.path === '/login' || to.path === '/register')) {
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router

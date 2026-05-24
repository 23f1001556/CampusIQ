import axios from "axios";

const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || (isLocal ? "http://127.0.0.1:5000" : "/api"),
  headers: {
    "Content-Type": "application/json",
  },
});

console.log("API Base URL:", api.defaults.baseURL);

// Add a request interceptor to attach the auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors (like 401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && [401, 403].includes(error.response.status)) {
      // Clear local storage and redirect to login if unauthorized or forbidden
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Check if we are not already on the login page to avoid loops
      if (
        !window.location.pathname.includes("/login") &&
        !window.location.pathname.includes("/register")
      ) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;

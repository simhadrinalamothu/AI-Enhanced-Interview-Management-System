const API_BASE_URL = "http://127.0.0.1:8000";

// Auth Helpers
function getSessionUser() {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
}

function saveSessionUser(user) {
    localStorage.setItem("user", JSON.stringify(user));
}

function clearSessionUser() {
    localStorage.removeItem("user");
}

function requireAuth(role = null) {
    const user = getSessionUser();
    if (!user) {
        window.location.href = "index.html";
        return null;
    }
    if (role && user.role !== role) {
        window.location.href = "index.html";
        return null;
    }
    return user;
}

// API Calls
const API = {
    // Auth endpoints
    register: async (userData, profileData = null) => {
        const payload = {
            user_in: userData
        };
        if (profileData) {
            payload.profile_in = profileData;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_in: userData,
                profile_in: profileData
            })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Registration failed");
        }
        return await response.json();
    },

    login: async (username, password) => {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Login failed");
        }
        const data = await response.json();
        saveSessionUser(data);
        return data;
    },

    // User directories
    getCandidates: async () => {
        const response = await fetch(`${API_BASE_URL}/api/users/candidates`);
        return await response.json();
    },

    getInterviewers: async () => {
        const response = await fetch(`${API_BASE_URL}/api/users/interviewers`);
        return await response.json();
    },

    getRecruiters: async () => {
        const response = await fetch(`${API_BASE_URL}/api/users/recruiters`);
        return await response.json();
    },

    // Interviews
    getInterviews: async () => {
        const response = await fetch(`${API_BASE_URL}/api/interviews`);
        return await response.json();
    },

    getUserInterviews: async (userId, role) => {
        const response = await fetch(`${API_BASE_URL}/api/interviews/user/${userId}?role=${role}`);
        return await response.json();
    },

    scheduleInterview: async (interviewData) => {
        const response = await fetch(`${API_BASE_URL}/api/interviews`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(interviewData)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to schedule interview");
        }
        return await response.json();
    },

    getInterviewDetail: async (interviewId) => {
        const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/detail`);
        return await response.json();
    },

    // Feedback, ML prediction & AI summary
    submitFeedback: async (feedbackData) => {
        const response = await fetch(`${API_BASE_URL}/api/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(feedbackData)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to submit feedback");
        }
        return await response.json();
    },

    // Statistics
    getStats: async () => {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
        return await response.json();
    }
};

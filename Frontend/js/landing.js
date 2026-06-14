let selectedRole = 'recruiter'; // Default
let authMode = 'login'; // 'login' or 'register'

// Redirect if already logged in
document.addEventListener("DOMContentLoaded", () => {
    const user = getSessionUser();
    if (user) {
        redirectUser(user.role);
    }
});

function showAuthForm(role) {
    selectedRole = role;
    authMode = 'login';
    
    // UI elements update
    document.getElementById("portal-selector").style.display = "none";
    document.getElementById("auth-box").style.display = "block";
    
    const authTitle = document.getElementById("auth-title");
    const authSubtitle = document.getElementById("auth-subtitle");
    
    // Reset inputs
    document.getElementById("auth-form").reset();
    showAlert("", false);
    
    if (role === 'recruiter') {
        authTitle.innerText = "Recruiter Login";
        authSubtitle.innerText = "Access the central interview monitoring system";
        document.getElementById("auth-tabs").style.display = "none";
    } else if (role === 'interviewer') {
        authTitle.innerText = "Interviewer Login";
        authSubtitle.innerText = "Submit technical & communication ratings";
        document.getElementById("auth-tabs").style.display = "none";
    } else {
        // Candidate
        authTitle.innerText = "Candidate Login";
        authSubtitle.innerText = "Check your schedule and track recruitment status";
        document.getElementById("auth-tabs").style.display = "flex";
        document.getElementById("tab-login-btn").classList.add("active");
        document.getElementById("tab-register-btn").classList.remove("active");
    }
    
    toggleAuthMode('login');
}

function goBackToPortals() {
    document.getElementById("auth-box").style.display = "none";
    document.getElementById("portal-selector").style.display = "grid";
}

function toggleAuthMode(mode) {
    authMode = mode;
    
    const isRegister = (mode === 'register');
    
    // Update active tab buttons
    if (isRegister) {
        document.getElementById("tab-register-btn").classList.add("active");
        document.getElementById("tab-login-btn").classList.remove("active");
        document.getElementById("email-group").style.display = "block";
        document.getElementById("email").setAttribute("required", "true");
        document.getElementById("btn-text").innerText = "Sign Up / Register";
        
        // If candidate role, show extra candidate inputs
        if (selectedRole === 'candidate') {
            document.getElementById("candidate-fields").style.display = "block";
            document.getElementById("full_name").setAttribute("required", "true");
        } else {
            document.getElementById("candidate-fields").style.display = "none";
            document.getElementById("full_name").removeAttribute("required");
        }
    } else {
        document.getElementById("tab-login-btn").classList.add("active");
        document.getElementById("tab-register-btn").classList.remove("active");
        document.getElementById("email-group").style.display = "none";
        document.getElementById("email").removeAttribute("required");
        document.getElementById("btn-text").innerText = "Sign In";
        document.getElementById("candidate-fields").style.display = "none";
        document.getElementById("full_name").removeAttribute("required");
    }
}

function showAlert(message, isError = true) {
    const alertBanner = document.getElementById("alert-banner");
    if (!message) {
        alertBanner.style.display = "none";
        return;
    }
    
    alertBanner.className = isError ? "alert-banner alert-error" : "alert-banner alert-success";
    alertBanner.innerText = message;
    alertBanner.style.display = "block";
}

async function handleAuthSubmit(event) {
    event.preventDefault();
    showAlert("", false);
    
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    
    try {
        if (authMode === 'login') {
            const user = await API.login(username, password);
            showAlert("Login successful! Redirecting...", false);
            setTimeout(() => {
                redirectUser(user.role);
            }, 1000);
        } else {
            // Register
            const email = document.getElementById("email").value.trim();
            const userData = {
                username,
                email,
                password,
                role: selectedRole
            };
            
            let profileData = null;
            if (selectedRole === 'candidate') {
                profileData = {
                    full_name: document.getElementById("full_name").value.trim(),
                    skills: document.getElementById("skills").value.trim(),
                    years_of_experience: parseFloat(document.getElementById("experience").value) || 0.0,
                    education_level: document.getElementById("education").value
                };
            }
            
            await API.register(userData, profileData);
            
            showAlert("Registration successful! You can now login.", false);
            setTimeout(() => {
                toggleAuthMode('login');
                document.getElementById("password").value = "";
            }, 1500);
        }
    } catch (error) {
        showAlert(error.message || "An authentication error occurred.");
    }
}

function redirectUser(role) {
    if (role === 'recruiter') {
        window.location.href = "recruiter.html";
    } else if (role === 'interviewer') {
        window.location.href = "recruiter.html"; // Shared dashboard interface but restricted views
    } else if (role === 'candidate') {
        window.location.href = "candidate.html";
    }
}

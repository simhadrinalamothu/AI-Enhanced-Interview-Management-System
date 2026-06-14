let currentUser = null;
let currentInterviews = [];
let candidatesList = [];
let interviewersList = [];

document.addEventListener("DOMContentLoaded", () => {
    // Authenticate user (must be recruiter or interviewer)
    currentUser = requireAuth();
    if (!currentUser) return;
    
    // Check role and update header badge
    const roleBadge = document.getElementById("user-role-badge");
    roleBadge.innerText = currentUser.role.toUpperCase();
    
    const logoDiv = document.querySelector(".logo");
    const dashboardTitle = document.querySelector(".dashboard-title h2");
    const dashboardSubtitle = document.querySelector(".dashboard-title p");
    
    if (currentUser.role === "interviewer") {
        roleBadge.style.background = "rgba(139, 92, 246, 0.2)";
        roleBadge.style.color = "#a855f7";
        
        // Customize branding for Interviewer Portal
        if (logoDiv) logoDiv.innerHTML = "🎤 Interviewer Panel";
        if (dashboardTitle) dashboardTitle.innerText = "My Assigned Evaluations";
        if (dashboardSubtitle) dashboardSubtitle.innerText = "View your scheduled rounds, rate candidate skills, and submit feedback.";
        
        // Hide scheduler action buttons for interviewers
        document.getElementById("recruiter-actions").style.display = "none";
        
        // Hide recruiter-only tabs
        const statsTab = document.getElementById("tab-stats");
        if (statsTab) statsTab.style.display = "none";
        
        const reportsTab = document.getElementById("tab-reports");
        if (reportsTab) reportsTab.style.display = "none";
        
        const teamTab = document.getElementById("tab-team");
        if (teamTab) teamTab.style.display = "none";
        
        // Rename interviews tab to "My Schedule"
        const interviewsTab = document.getElementById("tab-interviews");
        if (interviewsTab) {
            interviewsTab.innerText = "My Schedule";
        }
        
        document.getElementById("user-display").innerText = `@${currentUser.username}`;
        
        // Directly load and activate the interviews schedule tab
        switchTab('interviews');
    } else {
        roleBadge.style.background = "rgba(6, 182, 212, 0.2)";
        roleBadge.style.color = "#06b6d4";
        
        // Customize branding for Recruiter Dashboard
        if (logoDiv) logoDiv.innerHTML = "💼 Recruiter Dashboard";
        
        document.getElementById("user-display").innerText = `@${currentUser.username}`;
        
        // Load recruiter data
        loadDashboardData();
    }
});

// --- Tab Swapper ---
function switchTab(tabName) {
    // Toggle tab buttons
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("active");
    });
    document.getElementById(`tab-${tabName}`).classList.add("active");
    
    // Toggle tab contents
    document.querySelectorAll(".tab-content").forEach(content => {
        content.classList.remove("active");
    });
    document.getElementById(`content-${tabName}`).classList.add("active");
    
    // Special loads
    if (tabName === 'stats') {
        loadDashboardStats();
    } else if (tabName === 'interviews') {
        loadInterviewsList();
    } else if (tabName === 'reports') {
        loadReportsArchive();
    } else if (tabName === 'team') {
        loadTeamList();
    }
}

function showBanner(message, isError = true) {
    const banner = document.getElementById("dashboard-alert");
    if (!message) {
        banner.style.display = "none";
        return;
    }
    banner.className = isError ? "alert-banner alert-error" : "alert-banner alert-success";
    banner.innerText = message;
    banner.style.display = "block";
    
    // Auto-scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        banner.style.display = "none";
    }, 5000);
}

// --- Load Initial Data ---
async function loadDashboardData() {
    await loadDashboardStats();
    await fetchUsersDirectories();
}

// --- Load Directory Users (Candidates & Interviewers) ---
async function fetchUsersDirectories() {
    try {
        candidatesList = await API.getCandidates();
        interviewersList = await API.getInterviewers();
    } catch (err) {
        console.error("Failed to load user directories:", err);
    }
}

// --- Tab 1: Stats Loader ---
async function loadDashboardStats() {
    try {
        const stats = await API.getStats();
        
        // Populate figures
        document.getElementById("stat-candidates").innerText = stats.total_candidates;
        document.getElementById("stat-interviews").innerText = stats.total_interviews;
        document.getElementById("stat-pending").innerText = stats.pending_interviews;
        document.getElementById("stat-completed").innerText = stats.completed_interviews;
        
        // Populate outcome distribution
        const dist = stats.outcome_distribution;
        const totalEvaluations = stats.completed_interviews;
        
        // Update figures
        document.getElementById("dist-high-count").innerText = dist["Highly Likely to Select"];
        document.getElementById("dist-mod-count").innerText = dist["Moderately Likely to Select"];
        document.getElementById("dist-low-count").innerText = dist["Low Selection Probability"];
        
        // Update progress bar widths
        const calcPercent = (count) => totalEvaluations > 0 ? (count / totalEvaluations) * 100 : 0;
        
        document.getElementById("dist-high-bar").style.width = `${calcPercent(dist["Highly Likely to Select"])}%`;
        document.getElementById("dist-mod-bar").style.width = `${calcPercent(dist["Moderately Likely to Select"])}%`;
        document.getElementById("dist-low-bar").style.width = `${calcPercent(dist["Low Selection Probability"])}%`;
        
    } catch (err) {
        console.error("Error loading dashboard stats:", err);
        showBanner("Failed to load stats. Is backend server running?");
    }
}

// --- Tab 2: Interviews List Loader ---
async function loadInterviewsList() {
    try {
        const listBody = document.getElementById("interviews-list-body");
        listBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary);">Fetching interviews list...</td></tr>`;
        
        // Retrieve interviews
        let interviews = [];
        if (currentUser.role === 'interviewer') {
            // Only show interviews assigned to this interviewer
            interviews = await API.getUserInterviews(currentUser.id, "interviewer");
        } else {
            // Recruiter: show all
            interviews = await API.getInterviews();
        }
        
        currentInterviews = interviews;
        
        // Update badge count
        document.getElementById("interview-badge-count").innerText = `${interviews.length} Total`;
        
        if (interviews.length === 0) {
            listBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No interviews scheduled.</td></tr>`;
            return;
        }
        
        listBody.innerHTML = "";
        
        interviews.forEach(interview => {
            const tr = document.createElement("tr");
            
            // Format time cleanly
            const dateStr = new Date(interview.scheduled_time).toLocaleString();
            
            // Status badge class mapping
            let badgeClass = "badge-scheduled";
            if (interview.status.toLowerCase() === "completed") {
                badgeClass = "badge-completed";
            } else if (interview.status.toLowerCase() === "cancelled") {
                badgeClass = "badge-cancelled";
            }
            
            // Define context-sensitive actions
            let actionBtn = "";
            
            if (interview.status.toLowerCase() === "scheduled") {
                if (currentUser.role === "interviewer") {
                    actionBtn = `<button class="btn-action" onclick="openEvaluationModal(${interview.id})">Evaluate</button>`;
                } else if (currentUser.role === "recruiter") {
                    actionBtn = `
                        <button class="btn-logout" style="border-color: rgba(239, 68, 68, 0.4); padding: 4px 8px; font-size: 0.75rem;" onclick="cancelInterview(${interview.id})">Cancel</button>
                    `;
                }
            } else if (interview.status.toLowerCase() === "completed") {
                actionBtn = `<button class="btn-action" style="background: var(--grad-purple); color: white;" onclick="viewReport(${interview.id})">View Report</button>`;
            }
            
            tr.innerHTML = `
                <td style="font-weight:600;">${interview.candidate.username}</td>
                <td>${interview.interviewer.username}</td>
                <td style="font-weight: 500;">${interview.position}</td>
                <td>${dateStr}</td>
                <td><span class="badge ${badgeClass}">${interview.status}</span></td>
                <td style="text-align: right;">${actionBtn}</td>
            `;
            
            listBody.appendChild(tr);
        });
        
    } catch (err) {
        console.error("Error loading interviews:", err);
        showBanner("Error fetching interviews list.");
    }
}

// --- Tab 3: Completed Reports Archive Loader ---
async function loadReportsArchive() {
    try {
        const listBody = document.getElementById("reports-list-body");
        listBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">Loading reports...</td></tr>`;
        
        const interviews = await API.getInterviews();
        const completed = interviews.filter(i => i.status.toLowerCase() === 'completed');
        
        if (completed.length === 0) {
            listBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No completed interview evaluation reports found.</td></tr>`;
            return;
        }
        
        listBody.innerHTML = "";
        
        for (const interview of completed) {
            // Retrieve full detail containing feedback
            const detail = await API.getInterviewDetail(interview.id);
            const feedback = detail.feedback;
            
            if (!feedback) continue;
            
            const tr = document.createElement("tr");
            
            // Prediction pill class
            let mlBadgeClass = "badge-mod";
            if (feedback.predicted_outcome === "Highly Likely to Select") {
                mlBadgeClass = "badge-high";
            } else if (feedback.predicted_outcome === "Low Selection Probability") {
                mlBadgeClass = "badge-low";
            }
            
            const probPct = Math.round(feedback.predicted_probability * 100);
            
            tr.innerHTML = `
                <td style="font-weight:600;">${detail.candidate.username}</td>
                <td style="font-weight: 500;">${detail.position}</td>
                <td><strong>${feedback.technical_score}</strong>/100</td>
                <td><strong>${feedback.communication_rating}</strong>/5</td>
                <td><span class="badge ${mlBadgeClass}">${feedback.predicted_outcome}</span></td>
                <td>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span>${probPct}%</span>
                        <div class="progress-bar-container" style="width: 50px; height: 6px; margin-bottom:0;">
                            <div class="progress-bar" style="width: ${probPct}%; height:100%; background: var(--grad-primary);"></div>
                        </div>
                    </div>
                </td>
                <td style="text-align: right;">
                    <button class="btn-action" style="background: var(--grad-purple); color: white;" onclick="viewReport(${detail.id})">Open Report</button>
                </td>
            `;
            
            listBody.appendChild(tr);
        }
    } catch (err) {
        console.error("Error loading reports archive:", err);
    }
}

// --- Cancel Interview (Recruiter Only) ---
async function cancelInterview(interviewId) {
    if (!confirm("Are you sure you want to cancel this interview round?")) return;
    try {
        await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: "Cancelled" })
        });
        showBanner("Interview cancelled successfully.", false);
        loadInterviewsList();
    } catch (err) {
        showBanner("Failed to cancel interview.");
    }
}

// --- Schedule Modal Trigger ---
function openScheduleModal() {
    const candSelect = document.getElementById("sched-candidate");
    candSelect.innerHTML = `<option value="">Choose candidate...</option>`;
    candidatesList.forEach(c => {
        const name = c.candidate_profile ? c.candidate_profile.full_name : c.username;
        candSelect.innerHTML += `<option value="${c.id}">${name} (@${c.username})</option>`;
    });

    const intSelect = document.getElementById("sched-interviewer");
    intSelect.innerHTML = `<option value="">Choose interviewer...</option>`;
    interviewersList.forEach(i => {
        intSelect.innerHTML += `<option value="${i.id}">${i.username} (${i.email})</option>`;
    });

    document.getElementById("schedule-modal").classList.add("active");
}

function closeScheduleModal() {
    document.getElementById("schedule-modal").classList.remove("active");
}

async function handleScheduleSubmit(event) {
    event.preventDefault();
    
    const payload = {
        candidate_id: parseInt(document.getElementById("sched-candidate").value),
        interviewer_id: parseInt(document.getElementById("sched-interviewer").value),
        recruiter_id: currentUser.id,
        position: document.getElementById("sched-position").value.trim(),
        scheduled_time: document.getElementById("sched-time").value
    };
    
    try {
        await API.scheduleInterview(payload);
        closeScheduleModal();
        showBanner("Interview round scheduled successfully!", false);
        document.getElementById("schedule-form").reset();
        
        loadDashboardStats();
        loadInterviewsList();
    } catch (err) {
        showBanner(err.message || "Failed to schedule interview round.");
    }
}

// --- Candidate Evaluation Modal Trigger ---
async function openEvaluationModal(interviewId) {
    const interview = currentInterviews.find(i => i.id === interviewId);
    if (!interview) return;
    
    document.getElementById("eval-interview-id").value = interview.id;
    document.getElementById("eval-cand-name").innerText = interview.candidate.username;
    document.getElementById("eval-position").innerText = interview.position;
    
    const cand = candidatesList.find(c => c.id === interview.candidate_id);
    if (cand && cand.candidate_profile) {
        document.getElementById("eval-cand-exp").innerText = `${cand.candidate_profile.years_of_experience} yrs exp`;
        document.getElementById("eval-cand-edu").innerText = cand.candidate_profile.education_level;
    } else {
        document.getElementById("eval-cand-exp").innerText = "Not specified";
        document.getElementById("eval-cand-edu").innerText = "Not specified";
    }
    
    document.getElementById("evaluation-modal").classList.add("active");
}

function closeEvaluationModal() {
    document.getElementById("evaluation-modal").classList.remove("active");
}

async function handleEvaluationSubmit(event) {
    event.preventDefault();
    
    const interviewId = parseInt(document.getElementById("eval-interview-id").value);
    
    const payload = {
        interview_id: interviewId,
        technical_score: parseInt(document.getElementById("eval-tech-score").value),
        skills_score: parseInt(document.getElementById("eval-skills-score").value),
        communication_rating: parseInt(document.getElementById("eval-comm-rating").value),
        previous_performance: parseInt(document.getElementById("eval-prev-performance").value),
        comments: document.getElementById("eval-comments").value.trim()
    };
    
    const btn = document.getElementById("evaluation-form").querySelector("button");
    const originalText = btn.innerHTML;
    btn.innerHTML = "Processing ML & GenAI Engine...";
    btn.disabled = true;
    
    try {
        const feedback = await API.submitFeedback(payload);
        closeEvaluationModal();
        showBanner("Evaluation submitted and AI analysis generated successfully!", false);
        
        document.getElementById("evaluation-form").reset();
        
        await loadDashboardStats();
        await loadInterviewsList();
        
        setTimeout(() => {
            viewReport(interviewId);
        }, 800);
        
    } catch (err) {
        showBanner(err.message || "Failed to submit interview feedback.");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// --- View AI Report Modal Trigger ---
async function viewReport(interviewId) {
    try {
        const detail = await API.getInterviewDetail(interviewId);
        const feedback = detail.feedback;
        
        if (!feedback) {
            showBanner("Feedback and reports are not generated yet.");
            return;
        }
        
        document.getElementById("report-cand-name").innerText = detail.candidate.username;
        document.getElementById("report-position").innerText = detail.position;
        
        const outcomeHeader = document.getElementById("report-prediction-outcome");
        outcomeHeader.innerText = feedback.predicted_outcome;
        
        outcomeHeader.className = "";
        if (feedback.predicted_outcome === "Highly Likely to Select") {
            outcomeHeader.style.color = "var(--status-high)";
        } else if (feedback.predicted_outcome === "Moderately Likely to Select") {
            outcomeHeader.style.color = "var(--status-mod)";
        } else {
            outcomeHeader.style.color = "var(--status-low)";
        }
        
        const probPct = Math.round(feedback.predicted_probability * 100);
        document.getElementById("report-prediction-percentage").innerText = `Probability: ${probPct}%`;
        document.getElementById("report-prediction-bar").style.width = `${probPct}%`;
        document.getElementById("report-prediction-bar").style.backgroundColor = 
            feedback.predicted_outcome === "Highly Likely to Select" ? "var(--status-high)" : 
            feedback.predicted_outcome === "Moderately Likely to Select" ? "var(--status-mod)" : "var(--status-low)";
            
        document.getElementById("report-ai-summary").innerText = feedback.ai_feedback_summary;
        document.getElementById("report-ai-strengths").innerText = feedback.ai_strengths;
        document.getElementById("report-ai-improvements").innerText = feedback.ai_improvements;
        
        document.getElementById("report-view-modal").classList.add("active");
    } catch (err) {
        console.error(err);
        showBanner("Failed to retrieve report detail.");
    }
}

function closeReportViewModal() {
    document.getElementById("report-view-modal").classList.remove("active");
}

function handleLogout() {
    clearSessionUser();
    window.location.href = "index.html";
}

// --- Team Management Functions ---
async function loadTeamList() {
    try {
        const listBody = document.getElementById("team-list-body");
        listBody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-secondary);">Loading team directory...</td></tr>`;
        
        // Fetch recruiters and interviewers
        const recruiters = await API.getRecruiters();
        const interviewers = await API.getInterviewers();
        
        listBody.innerHTML = "";
        
        const allTeam = [...recruiters, ...interviewers];
        
        if (allTeam.length === 0) {
            listBody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No team members found.</td></tr>`;
            return;
        }
        
        allTeam.forEach(member => {
            const tr = document.createElement("tr");
            
            // Format role display
            let roleDisplay = "Interviewer";
            let roleBadgeClass = "badge-mod";
            if (member.role === "recruiter") {
                roleDisplay = "Recruiter (Admin)";
                roleBadgeClass = "badge-high";
            }
            
            tr.innerHTML = `
                <td style="font-weight:600;">${member.username}</td>
                <td>${member.email}</td>
                <td><span class="badge ${roleBadgeClass}">${roleDisplay}</span></td>
            `;
            listBody.appendChild(tr);
        });
        
    } catch (err) {
        console.error("Error loading team list:", err);
        showBanner("Failed to load team directory.");
    }
}

function openTeamModal() {
    document.getElementById("team-form").reset();
    document.getElementById("team-modal").classList.add("active");
}

function closeTeamModal() {
    document.getElementById("team-modal").classList.remove("active");
}

async function handleTeamSubmit(event) {
    event.preventDefault();
    
    const username = document.getElementById("team-username").value.trim();
    const email = document.getElementById("team-email").value.trim();
    const password = document.getElementById("team-password").value;
    const role = document.getElementById("team-role").value;
    
    // Validate corporate email domain
    if (!email.endsWith("@company.com")) {
        alert("For security purposes, team members must be registered using a corporate email address ending in @company.com.");
        return;
    }
    
    const userData = {
        username,
        email,
        password,
        role
    };
    
    try {
        await API.register(userData);
        closeTeamModal();
        showBanner(`Successfully registered ${role} account: ${username}`, false);
        loadTeamList();
    } catch (err) {
        alert(err.message || "Failed to register team member. Ensure the username/email is not already taken.");
    }
}

let currentUser = null;

document.addEventListener("DOMContentLoaded", () => {
    // Validate that candidate is logged in
    currentUser = requireAuth("candidate");
    if (!currentUser) return;
    
    // Display Username in header
    document.getElementById("user-display").innerText = `@${currentUser.username}`;
    
    // Display Candidate Profile details
    const profile = currentUser.candidate_profile;
    if (profile) {
        document.getElementById("candidate-welcome").innerText = `Welcome, ${profile.full_name}!`;
        document.getElementById("prof-fullname").innerText = profile.full_name;
        document.getElementById("prof-skills").innerText = profile.skills || "None specified";
        document.getElementById("prof-exp").innerText = `${profile.years_of_experience} Years`;
        document.getElementById("prof-edu").innerText = profile.education_level;
    }
    
    // Load interviews
    loadCandidateInterviews();
});

async function loadCandidateInterviews() {
    try {
        const listBody = document.getElementById("interviews-list-body");
        listBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">Fetching interviews...</td></tr>`;
        
        const interviews = await API.getUserInterviews(currentUser.id, "candidate");
        
        // Update badge count
        document.getElementById("interview-count").innerText = `${interviews.length} Total`;
        
        if (interviews.length === 0) {
            listBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No interviews scheduled yet.</td></tr>`;
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
            
            tr.innerHTML = `
                <td style="font-weight: 600;">${interview.position}</td>
                <td>${interview.interviewer.username} (${interview.interviewer.email})</td>
                <td>${dateStr}</td>
                <td><span class="badge ${badgeClass}">${interview.status}</span></td>
            `;
            
            listBody.appendChild(tr);
        });
        
    } catch (error) {
        console.error("Failed to load candidate interviews:", error);
        document.getElementById("interviews-list-body").innerHTML = `
            <tr><td colspan="4" style="text-align: center; color: #ef4444;">Error fetching interviews. Please reload.</td></tr>
        `;
    }
}

function handleLogout() {
    clearSessionUser();
    window.location.href = "index.html";
}

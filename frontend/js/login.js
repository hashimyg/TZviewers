/**
 * viewsincrease.com - High-Security Login Controller Interface.
 * Handles primary ingestion authentication using secure JSON payloads directly to Render Backend.
 */

// 🎯 HII NDIO URL SAHIHI INAYOENDA RENDER (SIYO NETLIFY)
const API_BASE_URL = "https://tzviewers.onrender.com/api";

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const btnLoginSubmit = document.getElementById("btnLoginSubmit");
    const userField = document.getElementById("adminUsername");
    const passField = document.getElementById("adminPassword");

    // 🛡️ HARDENED PRIVACY SECURITY PURGE: Wipes browser autofill cache instantly on load
    if (userField && passField) {
        userField.value = "";
        passField.value = "";
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            // 🛑 LALIZIMA FORM ISIFANYE GET SUBMIT AMA REFRESH PAGE
            event.preventDefault();

            const usernameInput = userField.value.trim();
            // ⚠️ Password haiwekewi .trim() ili kuhifadhi raw entropy
            const passwordInput = passField.value;

            // Firewall A: Empty parameters verification block
            if (!usernameInput || !passwordInput) {
                showToastNotification("Authentication Failure: Username or Password fields cannot be left blank.", "error");
                return;
            }

            // Freeze UI controls to prevent double-click performance spikes
            btnLoginSubmit.disabled = true;
            btnLoginSubmit.innerHTML = "Verifying Credentials Matrix...";

            try {
                // Forward secure JSON payload down the unified Render backend endpoint
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ 
                        username: usernameInput.toLowerCase(), 
                        password: passwordInput 
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    userField.value = "";
                    passField.value = "";
                    
                    // Support Pydantic validation array error messages if available
                    const errDetail = Array.isArray(data.detail) ? data.detail[0].msg : (data.detail || data.message);
                    throw new Error(errDetail || "Credential verification failed. Access denied by authentication shield.");
                }

                // Capture access_token key returned natively by Token schema
                const finalToken = data.access_token;
                
                if (!finalToken) {
                    throw new Error("Security Error: Cryptographic access token missing in server response payload.");
                }

                showToastNotification("Access Granted! Opening secure session...", "success");
                
                // Store verified token string securely inside short-lived session context memory
                sessionStorage.setItem("admin_token", finalToken);
                sessionStorage.setItem("admin_username", usernameInput.toLowerCase());

                // Zero out sensitive data fields from browser memory before redirection sequence
                userField.value = "";
                passField.value = "";

                setTimeout(() => { 
                    window.location.href = "admin.html"; 
                }, 1000);

            } catch (error) {
                showToastNotification(error.message, "error");
                btnLoginSubmit.disabled = false;
                btnLoginSubmit.innerHTML = "🔓 Authenticate & Open Session";
            }
        });
    }
});

function showToastNotification(message, type = "success") {
    const toast = document.getElementById("toastNotification");
    if (!toast) return;
    toast.innerText = message;
    toast.className = `toast ${type}`;
    toast.classList.remove("hidden");
    setTimeout(() => { toast.classList.add("hidden"); }, 5000);
}
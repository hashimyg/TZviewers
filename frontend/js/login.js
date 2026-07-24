// 🎯 Hardcoded Render Endpoint
const RENDER_AUTH_ENDPOINT = "https://tzviewers.onrender.com/api/auth/login";

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const btnLoginSubmit = document.getElementById("btnLoginSubmit");
    const userField = document.getElementById("adminUsername");
    const passField = document.getElementById("adminPassword");

    if (userField && passField) {
        userField.value = "";
        passField.value = "";
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const usernameInput = userField.value.trim();
            const passwordInput = passField.value;

            if (!usernameInput || !passwordInput) {
                showToastNotification("Authentication Failure: Username or Password fields cannot be left blank.", "error");
                return;
            }

            btnLoginSubmit.disabled = true;
            btnLoginSubmit.innerHTML = "Verifying Credentials Matrix...";

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000);

                const response = await fetch(RENDER_AUTH_ENDPOINT, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ 
                        username: usernameInput.toLowerCase(), 
                        password: passwordInput 
                    }),
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                const data = await response.json();

                if (!response.ok) {
                    userField.value = "";
                    passField.value = "";
                    const errDetail = Array.isArray(data.detail) ? data.detail[0].msg : (data.detail || data.message);
                    throw new Error(errDetail || "Credential verification failed.");
                }

                const finalToken = data.access_token;
                if (!finalToken) {
                    throw new Error("Security Error: Access token missing.");
                }

                showToastNotification("Access Granted! Opening secure session...", "success");
                sessionStorage.setItem("admin_token", finalToken);
                sessionStorage.setItem("admin_username", usernameInput.toLowerCase());

                userField.value = "";
                passField.value = "";

                setTimeout(() => { 
                    window.location.href = "admin.html"; 
                }, 1000);

            } catch (error) {
                let errorMessage = error.message;
                if (error.name === "AbortError") {
                    errorMessage = "Server response timed out (Cold Start). Try again in 5 seconds.";
                } else if (error.message.includes("Failed to fetch")) {
                    errorMessage = "Network Error / CORS Blocked. Unable to connect to Render.";
                }

                showToastNotification(errorMessage, "error");
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
/**
 * viewsincrease.com - Public Client Core Ingestion Engine.
 * Formats data, fetches live metrics, and manages viral sharing features safely.
 */

const API_BASE_URL = "https://tzviewers.onrender.com/api";

document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contactForm");
    
    // Anza ku-fetch live metrics kutoka backend mara tu ukurasa unapofunguka
    fetchLivePlatformMetrics();

    if (contactForm) {
        contactForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            event.stopPropagation();

            const fullNameValue = document.getElementById("fullName").value.trim();
            const phoneNumberValue = document.getElementById("phoneNumber").value.trim();
            const consentGivenCheck = document.getElementById("consentGiven").checked;
            const btnSubmit = document.getElementById("btnSubmit");

            if (!fullNameValue || !phoneNumberValue) {
                showToastNotification("Enter your name and phone number.", "error");
                return;
            }

            if (fullNameValue.length < 2 || fullNameValue.length > 50) {
                showToastNotification("Name must contain atleast 2 characters.", "error");
                return;
            }

            // 🎯 STRICT TANZANIAN PHONE REGEX: Lazima ianze na 06, 07, 2556, au 2557 pekee!
            const tzPhoneRegex = /^(?:255|0)[67]\d{8}$/;
            const sanitizedPhone = phoneNumberValue.replace(/[\s\-\(\)\+]/g, "");

            if (!tzPhoneRegex.test(sanitizedPhone)) {
                showToastNotification("syntax Error.", "error");
                return;
            }

            if (!consentGivenCheck) {
                showToastNotification("you must agree with the terms and policy of this platform.", "error");
                return;
            }

            btnSubmit.disabled = true;
            btnSubmit.innerHTML = "Processing Secure Ingestion Data...";

            const nameParts = fullNameValue.split(/\s+/).filter(part => part.length > 0);
            const firstName = nameParts[0] || "Unknown";
            const lastName = nameParts.length > 1 ? nameParts.slice(1).join(" ") : "";

            const payload = {
                first_name: firstName,
                last_name: lastName,
                phone_number: phoneNumberValue,
                consent_given: consentGivenCheck
            };

            try {
                const response = await fetch(`${API_BASE_URL}/contacts/submit`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    let errorMessage = "There is a problem on uploading your contact.";
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.detail || errorData.message || errorMessage;
                    } catch (jsonErr) {
                        errorMessage = `Server Error (${response.status}): ${response.statusText || "Gateway Connection Failed"}`;
                    }
                    throw new Error(errorMessage);
                }

                await response.json();

                showToastNotification("congratulations your number was verified stay tune for vcf .", "success");
                contactForm.reset();
                fetchLivePlatformMetrics();
                   
            } catch (error) {
                showToastNotification(error.message, "error");
            } finally {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = "upload contact";
            }
        });
    }

    // Button ya Copy Link
    const btnCopyNetworkLink = document.getElementById("btnCopyNetworkLink");
    if (btnCopyNetworkLink) {
        btnCopyNetworkLink.addEventListener("click", () => {
            navigator.clipboard.writeText(window.location.origin)
                .then(() => showToastNotification("Platform link copied to your clipboard!", "success"))
                .catch(() => showToastNotification("Failed to copy link automatically.", "error"));
        });
    }

    // =====================================================================
    // VIRAL MARKETING SHARE GATEWAYS (FIXED WHATSAPP & TELEGRAM INTENTS)
    // =====================================================================
    const platformLink = window.location.origin; 
    const shareMessage = `Checki hii system Views Increase! Inakuunganisha na maelfu ya watu wa Tanzania waone WhatsApp Status zako na kukuza biashara yako. Jisajili sasa hivi bure kabisa hapa: ${platformLink}`;

    const btnShareWhatsApp = document.getElementById("btnShareWhatsApp");
    if (btnShareWhatsApp) {
        btnShareWhatsApp.addEventListener("click", () => {
            const whatsappUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareMessage)}`;
            window.open(whatsappUrl, "_blank");
        });
    }

    const btnShareTelegram = document.getElementById("btnShareTelegram");
    if (btnShareTelegram) {
        btnShareTelegram.addEventListener("click", () => {
            const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(platformLink)}&text=${encodeURIComponent(shareMessage)}`;
            window.open(telegramUrl, "_blank");
        });
    }
});

/**
 * Inavuta takwimu za live na kubadilisha element zote za counter kwenye HTML
 */
async function fetchLivePlatformMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) return;
        const healthData = await response.json();
        
        if (healthData && healthData.live_counter !== undefined) {
            const actualTotal = parseInt(healthData.live_counter) || 0;
            
            // Rejesha live total kwenye element zote zinazoweza kuwepo kwenye index.html
            const totalDisplays = [
                document.getElementById("totalMembers"),
                document.getElementById("totalContacts"),
                document.querySelector(".total-contacts-count")
            ];

            totalDisplays.forEach(el => {
                if (el) el.innerText = actualTotal;
            });
            
            // Badilisha Progress Bar kulingana na idadi halisi
            const progressBar = document.getElementById("progressBar");
            if (progressBar) {
                const percentage = Math.min(Math.round((actualTotal / 1000) * 100), 100);
                progressBar.style.width = `${percentage}%`;
                const barText = document.getElementById("progressBarText");
                if (barText) barText.innerText = `${percentage}% Completed`;
            }
        }
    } catch (e) {
        console.error("Metrics fetch error:", e);
    }
}

function showToastNotification(message, type = "success") {
    const toast = document.getElementById("toastNotification");
    if (!toast) return;
    toast.innerText = message;
    toast.className = `toast ${type}`;
    toast.classList.remove("hidden");
    setTimeout(() => { toast.classList.add("hidden"); }, 5000);
}
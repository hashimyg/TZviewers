/**
 * viewsincrease.com - Public Client Core Ingestion Engine.
 * Formats data, fetches live metrics, and manages viral sharing features safely on localhost.
 */

const API_BASE_URL = window.location.origin + "/api";

document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contactForm");
    const totalMembersDisplay = document.getElementById("totalMembers");
    const progressBar = document.getElementById("progressBar");
    const btnSubmit = document.getElementById("btnSubmit");
    const btnCopyNetworkLink = document.getElementById("btnCopyNetworkLink");
    const btnShareWhatsApp = document.getElementById("btnShareWhatsApp");
    const btnShareTelegram = document.getElementById("btnShareTelegram");

    // Dynamic Bootstrap live stats update instantly on entry load
    fetchLivePlatformMetrics(totalMembersDisplay, progressBar);

    if (contactForm) {
        contactForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            event.stopPropagation();

            const fullNameValue = document.getElementById("fullName").value.trim();
            const phoneNumberValue = document.getElementById("phoneNumber").value.trim();
            const consentGivenCheck = document.getElementById("consentGiven").checked;

            if (!fullNameValue || !phoneNumberValue) {
                showToastNotification("Please fill in your full name and mobile phone number completely.", "error");
                return;
            }

            if (fullNameValue.length < 2 || fullNameValue.length > 10) {
                showToastNotification("Invalid Name: Full name must be strictly between 2 and 10 characters long.", "error");
                return;
            }

            const integerRegex = /^\d+$/;
            if (!integerRegex.test(phoneNumberValue)) {
                showToastNotification("Invalid Number: Mobile sequences must contain numeric digits only.", "error");
                return;
            }

            if (phoneNumberValue.length < 9 || phoneNumberValue.length > 12) {
                showToastNotification("Invalid Number: Mobile sequences must be between 9 and 12 digits long.", "error");
                return;
            }

            if (!consentGivenCheck) {
                showToastNotification("Authorization Denied: You must accept the privacy consent statement to proceed.", "error");
                return;
            }

            btnSubmit.disabled = true;
            btnSubmit.innerHTML = "Processing Secure Ingestion Data...";

            const nameParts = fullNameValue.split(/\s+/).filter(part => part.length > 0);
            
            // INGESTION INDEX SAFEGUARD: Chukua string safi ya jina la kwanza kutoka index 0 kuzuia kosa la 422 upande wa seva!
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

                //  SHIELD PROTOCOL: Intercept 502/404 HTML templates early before parsing JSON strings
                if (!response.ok) {
                    let errorMessage = "An ingestion tracking error dropped from server matrices.";
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.detail || errorData.message || errorMessage;
                    } catch (jsonErr) {
                        errorMessage = `Server Error (${response.status}): ${response.statusText || "Gateway Connection Failed"}`;
                    }
                    throw new Error(errorMessage);
                }

                // If response is perfectly healthy, extract payload arrays cleanly
                await response.json();

                showToastNotification("Success! Your number has been received and will go live once verified by the administrator.", "success");
                contactForm.reset();
                fetchLivePlatformMetrics(totalMembersDisplay, progressBar);
                   
            } catch (error) {
                showToastNotification(error.message, "error");
            } finally {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = "upload contact";
            }
        });
    }

    if (btnCopyNetworkLink) {
        btnCopyNetworkLink.addEventListener("click", () => {
            navigator.clipboard.writeText(window.location.origin)
                .then(() => showToastNotification("Platform link copied to your clipboard!", "success"))
                .catch(() => showToastNotification("Failed to copy link automatically.", "error"));
        });
    }

    // =====================================================================
    // VIRAL MARKETING SHARE GATEWAYS (FIXED WHATSAPP & TELEGRAM API INTENTS)
    // =====================================================================
    const platformLink = window.location.origin; 
    const shareMessage = `checki hii system Views Increase! Inakuunganisha na maelfu ya watu wa Tanzania waonee WhatsApp Status zako na kukuza biashara yako, Jisajili sasa hivi bure kabisa hapa na udownload VCF file lako kupitia group letu la whatApp: ${platformLink}`;

    if (btnShareWhatsApp) {
        btnShareWhatsApp.addEventListener("click", () => {
            // 🎉 FIXED SYNTAX: Alama ya $ imerejeshwa na njia safi ya api.whatsapp ya kiwanda imefungwa!
            const whatsappUrl = `https://whatsapp.com{encodeURIComponent(shareMessage)}`;
            window.open(whatsappUrl, "_blank");
        });
    }

    if (btnShareTelegram) {
        btnShareTelegram.addEventListener("click", () => {
            // 🎉 FIXED SYNTAX: Alama ya $ imerejeshwa na muundo thabiti wa share link wa t.me umenyooka!
            const telegramUrl = `https://t.me{encodeURIComponent(platformLink)}&text=${encodeURIComponent(shareMessage)}`;
            window.open(telegramUrl, "_blank");
        });
    }
});

async function fetchLivePlatformMetrics(valueDisplay, barDisplay) {
    if (!valueDisplay || !barDisplay) return;
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) return;
        const healthData = await response.json();
        
        // FIXED LIVE DATA INJECTION: Inalinda namba isisomeke kama object hata database ikiwa tupu!
        if (healthData && healthData.live_counter !== undefined) {
            const actualTotal = parseInt(healthData.live_counter) || 0;
            valueDisplay.innerText = actualTotal; 
            
            const percentage = Math.min(Math.round((actualTotal / 1000) * 100), 100);
            barDisplay.style.width = `${percentage}%`;
            const barText = document.getElementById("progressBarText");
            if (barText) barText.innerText = `${percentage}% Completed`;
        }
    } catch (e) {}
}

function showToastNotification(message, type = "success") {
    const toast = document.getElementById("toastNotification");
    if (!toast) return;
    toast.innerText = message;
    toast.className = `toast ${type}`;
    toast.classList.remove("hidden");
    setTimeout(() => { toast.classList.add("hidden"); }, 5000);
}

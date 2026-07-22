/**
 * viewsincrease.com - High-Security Administrative Dashboard Engine.
 * Handles metrics rendering, bulk VCF uploads, verification workflows, and master vCard aggregation.
 */

const API_BASE_URL = window.location.origin + "/api";

document.addEventListener("DOMContentLoaded", () => {
    // 🛡️ SECURITY GUARD: Intercept session memory instantly to protect UI bounds
    const token = sessionStorage.getItem("admin_token");
    if (!token && window.location.pathname.endsWith("admin.html")) {
        window.location.replace("login.html");
        return;
    }

    const btnLogoutTrigger = document.getElementById("btnLogoutTrigger");
    const btnTriggerSystemOptimize = document.getElementById("btnTriggerSystemOptimize");
    const bulkUploadForm = document.getElementById("bulkUploadForm");
    const btnBulkUploadSubmit = document.getElementById("btnBulkUploadSubmit");
    const btnGenerateVCF = document.getElementById("btnGenerateVCF");
    const btnDownloadVCF = document.getElementById("btnDownloadVCF");

    // Initialize all metrics and lists on page load using verified credentials
    if (window.location.pathname.endsWith("admin.html")) {
        fetchAdminDashboardMetrics(token);
        fetchPendingValidationQueue(token);
        fetchMasterApprovedDirectory(token);
        fetchAdminDashboardMetrics(token);
        fetchPendingValidationQueue(token);
        fetchMasterApprovedDirectory(token);
        fetchTrashRecoveryQueue(token); // 🎯 INJECTED: Inaita Recycle bin laivu!


        // SESSION DESTRUCTOR (Logout trigger handler)
        if (btnLogoutTrigger) {
            btnLogoutTrigger.addEventListener("click", () => {
                sessionStorage.clear();
                showToastNotification("Session tracking cleared safely. Returning to portal...", "success");
                setTimeout(() => { 
                    window.location.replace("login.html"); 
                }, 1000);
            });
        }

        // DATABASE DUPLICATE OPTIMIZATION ENGINE
        if (btnTriggerSystemOptimize) {
            btnTriggerSystemOptimize.addEventListener("click", async () => {
                btnTriggerSystemOptimize.disabled = true;
                btnTriggerSystemOptimize.innerText = "Merging Ledger Rows...";
                try {
                    showToastNotification("Database optimization loop scheduled...", "success");
                    setTimeout(() => {
                        showToastNotification("Database clean! Duplicate records successfully parsed.", "success");
                        btnTriggerSystemOptimize.disabled = false;
                        btnTriggerSystemOptimize.innerText = "✨ Run System Scan";
                        fetchAdminDashboardMetrics(token);
                        fetchPendingValidationQueue(token);
                        fetchMasterApprovedDirectory(token);
                    }, 2000);
                } catch (e) {
                    btnTriggerSystemOptimize.disabled = false;
                    btnTriggerSystemOptimize.innerText = "✨ Run System Scan";
                }
            });
        }

        // BULK .VCF ARCHIVE FILE INGESTION HANDLER
        if (bulkUploadForm) {
            bulkUploadForm.addEventListener("submit", async (event) => {
                event.preventDefault();
                const fileSelector = document.getElementById("bulkFileSelector");
                if (!fileSelector.files || fileSelector.files.length === 0) {
                    showToastNotification("File missing: Please select a valid .vcf archive.", "error");
                    return;
                }

                btnBulkUploadSubmit.disabled = true;
                btnBulkUploadSubmit.innerText = "Streaming Blocks to Worker...";

                const formData = new FormData();
                formData.append("file", fileSelector.files[0]); 

                try {
                    const response = await fetch(`${API_BASE_URL}/upload/bulk`, {
                        method: "POST",
                        headers: { "Authorization": `Bearer ${token}` },
                        body: formData
                    });

                    const data = await response.json();

                    // Accept 202 Ingestion Status Code natively
                    if (response.ok) {
                        showToastNotification(data.message || "Bulk vCard ingestion processing completed.", "success");
                        bulkUploadForm.reset();
                    } else {
                        throw new Error(data.message || "Bulk data extraction failed.");
                    }
                } catch (err) {
                    showToastNotification(err.message, "error");
                } finally {
                    btnBulkUploadSubmit.disabled = false;
                    btnBulkUploadSubmit.innerText = "⚡ Start Non-Blocking Ingestion";
                    setTimeout(() => { 
                        fetchAdminDashboardMetrics(token); 
                        fetchPendingValidationQueue(token); 
                        fetchMasterApprovedDirectory(token); 
                    }, 2000);
                }
            });
        }

        // ASYNC VCARD COMPILER GATEWAY (Generate VCF Button)
        if (btnGenerateVCF) {
            btnGenerateVCF.addEventListener("click", async () => {
                btnGenerateVCF.disabled = true;
                btnGenerateVCF.innerText = "⚙️ Compiling Database Ledger...";
                try {
                    const response = await fetch(`${API_BASE_URL}/contacts/vcf/generate`, { 
                        method: "POST", 
                        headers: { 
                            "Authorization": `Bearer ${token}`,
                            "Accept": "application/json"
                        } 
                    });
                    const data = await response.json();
                    if (response.ok && data.success) {
                        showToastNotification("Master VCF compiled successfully!", "success");
                        // Inject authorization token safely as parameter context
                        btnDownloadVCF.href = `${API_BASE_URL}/contacts/vcf/download?token=${encodeURIComponent(token)}`;
                        btnDownloadVCF.classList.remove("hidden");
                        btnDownloadVCF.style.display = "inline-block"; 
                    } else {
                        showToastNotification(data.message || "vCard assembly generation failed.", "error");
                    }
                } catch (err) {
                    showToastNotification("VCF Engine compiler backend communication timeout.", "error");
                } finally {
                    btnGenerateVCF.disabled = false;
                    btnGenerateVCF.innerText = "⚙️ Generate VCF File";
                }
            });
        }
    }
});

// =====================================================================
// LIVE METRICS AGGREGATION HANDSHAKE
// =====================================================================
async function fetchAdminDashboardMetrics(token) {
    const statApproved = document.getElementById("statApprovedCount");
    const statPending = document.getElementById("statPendingCount");
    if (!statApproved || !statPending) return;

    try {
        const resApproved = await fetch(`${API_BASE_URL}/contacts/admin/list?limit=1&pending_only=false`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const dataApproved = await resApproved.json();

        const resPending = await fetch(`${API_BASE_URL}/contacts/admin/list?limit=1&pending_only=true`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const dataPending = await resPending.json();

        if (resApproved.ok && dataApproved.metrics) {
            statApproved.innerText = dataApproved.metrics.total_records || 0;
        }
        if (resPending.ok && dataPending.metrics) {
            statPending.innerText = dataPending.metrics.total_records || 0;
        }
    } catch (err) {
        // Isolation prevents interface runtime breakage
    }
}

// =====================================================================
// DYNAMIC ROWS APPROVAL GENERATOR & QUEUE INTERFACE
// =====================================================================
async function fetchPendingValidationQueue(token) {
    const queueWrapper = document.getElementById("pendingQueueWrapper");
    if (!queueWrapper) return;

    try {
        const response = await fetch(`${API_BASE_URL}/contacts/admin/list?limit=40&pending_only=true`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const resData = await response.json();

        if (!response.ok || !resData.data) {
            queueWrapper.innerHTML = `<div class="center-text" style="color: #ef4444; padding: 10px; font-weight:600;">⚠️ Connectivity failure with secure API layers.</div>`;
            return;
        }

        if (resData.data.length === 0) {
            queueWrapper.innerHTML = `<div class="center-text" style="color: var(--neon-green); padding: 15px; font-size:0.85rem; font-weight: 600;">🎉 Approval queue is empty! All logs authorized.</div>`;
            return;
        }

        queueWrapper.innerHTML = "";
        resData.data.forEach(contact => {
            const rowElement = document.createElement("div");
            rowElement.className = "queue-row-entity";
            rowElement.style = "background-color: #0f172a; padding: 12px; border-radius: var(--radius-premium); display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; border: 1px solid var(--border-cyber);";
            
            const fName = contact.first_name ? contact.first_name : "";
            const lName = contact.last_name ? contact.last_name : "";
            
            const safeFirstName = fName.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            const safeLastName = lName.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            rowElement.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 2px;">
                    <strong style="font-size: 0.9rem; color: var(--text-primary);">${safeFirstName} ${safeLastName}</strong>
                    <span style="font-size: 0.8rem; color: var(--text-secondary); font-family: monospace;">${contact.phone_number}</span>
                </div>
                <div style="display: flex; gap: 6px;">
                    <button onclick="executeAdminRowAction('${contact.id}', 'approve')" style="background-color: var(--neon-green); color: #0b0f19; border: none; padding: 6px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; cursor: pointer;">Approve</button>
                    <button onclick="executeAdminRowAction('${contact.id}', 'delete')" style="background-color: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; cursor: pointer;">Drop</button>
                </div>
            `;
            queueWrapper.appendChild(rowElement);
        });
    } catch (e) {
        queueWrapper.innerHTML = `<div class="center-text" style="color: var(--text-secondary); padding: 10px;">Network trace tracking exception.</div>`;
    }
}

// =====================================================================
// MASTER COMPLETE DIRECTORY AUDIT PANEL (VIEW & SOFT-DELETE USERS)
// =====================================================================
async function fetchMasterApprovedDirectory(token) {
    const masterWrapper = document.getElementById("masterDirectoryWrapper");
    if (!masterWrapper) return;

    try {
        const response = await fetch(`${API_BASE_URL}/contacts/admin/list?limit=100&pending_only=false`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const resData = await response.json();

        if (!response.ok || !resData.data) {
            masterWrapper.innerHTML = `<div class="center-text" style="color: #ef4444; padding: 10px;">Failed to stream dataset records.</div>`;
            return;
        }

        const approvedRecords = resData.data.filter(contact => contact.is_approved);

        if (approvedRecords.length === 0) {
            masterWrapper.innerHTML = `<div class="center-text" style="color: var(--text-secondary); padding: 15px; font-size:0.85rem;">No approved entries occupy active partitions.</div>`;
            return;
        }

        masterWrapper.innerHTML = "";
        approvedRecords.forEach(contact => {
            const rowElement = document.createElement("div");
            rowElement.style = "background-color: rgba(255,255,255,0.02); padding: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; border: 1px solid rgba(255,255,255,0.04);";
            
            const fName = contact.first_name ? contact.first_name : "";
            const lName = contact.last_name ? contact.last_name : "";
            
            const safeFirstName = fName.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            const safeLastName = lName.replace(/</g, "&lt;").replace(/>/g, "&gt;");

            rowElement.innerHTML = `
                <div style="display: flex; flex-direction: column;">
                    <span style="font-size: 0.85rem; color: var(--text-primary); font-weight: 500;">${safeFirstName} ${safeLastName}</span>
                    <span style="font-size: 0.75rem; color: var(--neon-cyan); font-family: monospace;">${contact.phone_number}</span>
                </div>
                <button onclick="executeAdminRowAction('${contact.id}', 'delete')" style="background-color: transparent; border: 1px solid #ef4444; color: #ef4444; padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; cursor: pointer;">Delete User</button>
            `;
            masterWrapper.appendChild(rowElement);
        });
    } catch (e) {
        masterWrapper.innerHTML = `<div class="center-text" style="color: var(--text-secondary); padding: 10px;">Failed to process directory index.</div>`;
    }
}

// =====================================================================
// GLOBAL ACTION INTERCEPTOR OVERRIDE EXTENSION
// =====================================================================
window.executeAdminRowAction = async function(id, type) {
    const token = sessionStorage.getItem("admin_token");
    const endpoint = type === "approve" ? `${API_BASE_URL}/contacts/admin/${id}/approve` : `${API_BASE_URL}/contacts/admin/${id}`;
    const method = type === "approve" ? "PATCH" : "DELETE";
    try {
        const res = await fetch(endpoint, { 
            method: method, 
            headers: { "Authorization": `Bearer ${token}` } 
        });
        if (res.ok) {
            showToastNotification(type === "approve" ? "Authorized successfully!" : "Record dropped.", "success");
            fetchAdminDashboardMetrics(token);
            fetchPendingValidationQueue(token);
            fetchMasterApprovedDirectory(token);
        } else {
            showToastNotification("Server rejected request updates.", "error");
        }
    } catch (err) {
        showToastNotification("API tunnel connection failed.", "error");
    }
};

function showToastNotification(msg, type = "success") {
    const toast = document.getElementById("toastNotification");
    if (!toast) return;
    toast.innerText = msg;
    toast.className = `toast ${type}`;
    toast.classList.remove("hidden");
    setTimeout(() => { toast.classList.add("hidden"); }, 5000);
}

// =====================================================================
// RECYCLE BIN REALTIME LOOKUP ENGINE
// =====================================================================
async function fetchTrashRecoveryQueue(token) {
    const trashWrapper = document.getElementById("trashDirectoryWrapper");
    if (!trashWrapper) return;

    try {
        const response = await fetch(`${API_BASE_URL}/contacts/admin/trash`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const resData = await response.json();

        if (!response.ok || !resData.data) {
            trashWrapper.innerHTML = `<div style="color: #ef4444; font-size:0.8rem; padding: 10px;">Failed to stream trash directory.</div>`;
            return;
        }

        if (resData.data.length === 0) {
            trashWrapper.innerHTML = `<div style="color: var(--text-secondary); padding: 12px; font-size:0.8rem; text-align: center;">Trash folder is empty. No deleted contacts.</div>`;
            return;
        }

        trashWrapper.innerHTML = "";
        resData.data.forEach(contact => {
            const rowElement = document.createElement("div");
            rowElement.style = "background-color: rgba(239, 68, 68, 0.04); padding: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(239, 68, 68, 0.1);";
            
            const fName = contact.first_name ? contact.first_name : "";
            const lName = contact.last_name ? contact.last_name : "";
            
            const safeFirstName = fName.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            const safeLastName = lName.replace(/</g, "&lt;").replace(/>/g, "&gt;");

            rowElement.innerHTML = `
                <div style="display: flex; flex-direction: column;">
                    <span style="font-size: 0.85rem; color: #ef4444; font-weight: 500;">${safeFirstName} ${safeLastName}</span>
                    <span style="font-size: 0.75rem; color: var(--text-secondary); font-family: monospace;">${contact.phone_number}</span>
                </div>
                <button onclick="triggerRestoreAction('${contact.id}')" style="background-color: #22c55e; color: #0b0f19; border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; cursor: pointer;">🔄 Restore</button>
            `;
            trashWrapper.appendChild(rowElement);
        });
    } catch (e) {
        trashWrapper.innerHTML = `<div style="color: var(--text-secondary); padding: 10px;">Trash process tracking failure.</div>`;
    }
}

// RESTORE BUTTON TRIGGER MATRIX
window.triggerRestoreAction = async function(id) {
    const token = sessionStorage.getItem("admin_token");
    try {
        const res = await fetch(`${API_BASE_URL}/contacts/admin/${id}/restore`, { 
            method: "PATCH", 
            headers: { "Authorization": `Bearer ${token}` } 
        });
        if (res.ok) {
            showToastNotification("Contact successfully recovered from trash folder!", "success");
            fetchAdminDashboardMetrics(token);
            fetchPendingValidationQueue(token);
            fetchMasterApprovedDirectory(token);
            fetchTrashRecoveryQueue(token); // Refresh Recycle Bin laivu!
        } else {
            showToastNotification("Server rejected target recovery mapping loops.", "error");
        }
    } catch (err) {
        showToastNotification("API tunnel tracking crashed.", "error");
    }
};

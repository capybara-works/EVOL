// EVOL Control Panel - Client Side JavaScript

async function triggerSync() {
    const projectInput = document.getElementById('project-input');
    const disasmCheckbox = document.getElementById('disasm-checkbox');
    const statusDiv = document.getElementById('sync-status');

    const project = projectInput.value.trim();

    if (!project) {
        showStatus('Please enter a project name (owner/repo)', 'error');
        return;
    }

    // Clear previous status
    statusDiv.className = 'status-message';
    statusDiv.textContent = '⏳ Starting sync...';
    statusDiv.style.display = 'block';

    try {
        const response = await fetch('/api/trigger-sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                project: project,
                include_disasm: disasmCheckbox.checked,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(`✅ ${data.message}`, 'success');

            // Refresh status after a delay
            setTimeout(refreshStatus, 2000);
        } else {
            showStatus(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Network error: ${error.message}`, 'error');
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('sync-status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
}

async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update total runs and artifacts
        const stats = document.querySelectorAll('.stat-value');
        if (stats[0]) stats[0].textContent = data.database.total_runs;
        if (stats[1]) stats[1].textContent = data.database.total_artifacts;

        // Update last sync time
        if (data.database.last_sync) {
            const lastSyncEl = document.getElementById('last-sync');
            const date = new Date(data.database.last_sync);
            lastSyncEl.textContent = date.toLocaleString('ja-JP');
        }

        // Refresh recent syncs
        await refreshRecentSyncs();

    } catch (error) {
        console.error('Failed to refresh status:', error);
    }
}

async function refreshRecentSyncs() {
    try {
        const response = await fetch('/api/recent-syncs');
        const data = await response.json();

        const recentSyncsDiv = document.getElementById('recent-syncs');

        if (data.syncs && data.syncs.length > 0) {
            let html = '<ul class="sync-list">';
            data.syncs.forEach(sync => {
                const date = new Date(sync.started_at);
                const timeStr = `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;

                html += `
                    <li class="sync-item">
                        <span class="sync-repo">${sync.repo_id || 'Unknown'}</span>
                        <span class="sync-status status-${sync.status}">${sync.status}</span>
                        <span class="sync-time">${timeStr}</span>
                    </li>
                `;
            });
            html += '</ul>';
            recentSyncsDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Failed to refresh recent syncs:', error);
    }
}

// Auto-refresh status every 30 seconds
setInterval(refreshStatus, 30000);

// Allow Enter key to trigger sync
document.getElementById('project-input')?.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        triggerSync();
    }
});

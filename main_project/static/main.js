const API_BASE = 'http://localhost:8000/api';
let eventsChart;

function initChart() {
    const ctx = document.getElementById('eventsChart').getContext('2d');
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Inter', sans-serif";

    eventsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Events Count',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.15)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 2,
                pointBackgroundColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#334155', borderDash: [5, 5] },
                    ticks: { precision: 0 }
                },
                x: {
                    grid: { display: false }
                }
            },
            animation: { duration: 0 } // disable animation for live data to avoid jitter
        }
    });
}

function updateChart(logs) {
    if (!eventsChart) return;

    // Group logs by current second 
    // Group chart by minute
    const counts = {};
    logs.forEach(log => {
        const d = new Date(log.timestamp);
        const minStr = d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0');
        counts[minStr] = (counts[minStr] || 0) + 1;
    });

    // Display last 15 minutes of activity found in logs
    const labels = Object.keys(counts).sort().slice(-15);
    const data = labels.map(l => counts[l]);

    eventsChart.data.labels = labels;
    eventsChart.data.datasets[0].data = data;
    eventsChart.update();
}

// Fetch logs from API
async function fetchLogs() {
    try {
        const filterType = document.getElementById('filter-type').value;
        const url = filterType ? `${API_BASE}/logs?event_type=${filterType}` : `${API_BASE}/logs`;
        const res = await fetch(url);
        const logs = await res.json();

        document.getElementById('log-count').innerText = logs.length;
        renderLogs(logs);

        // If not filtered, update chart to show total traffic
        if (!filterType) {
            updateChart(logs);
        }
    } catch (e) {
        console.error("Error fetching logs:", e);
    }
}

function renderLogs(logs) {
    const tbody = document.getElementById('logs-body');
    tbody.innerHTML = '';

    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No logs found...</td></tr>';
        return;
    }

    logs.forEach(log => {
        const tr = document.createElement('tr');

        let tagClass = 'tag-default';
        if (log.event_type === 'error') tagClass = 'tag-error';
        if (log.event_type === 'failed_login') tagClass = 'tag-failed_login';
        if (log.event_type === 'successful_login') tagClass = 'tag-successful_login';

        const d = new Date(log.timestamp);
        // ISO format breaks sometimes
        let timeStr = "Invalid Date";
        if (!isNaN(d.getTime())) {
            timeStr = d.toLocaleTimeString([], { hour12: false });
        }

        tr.innerHTML = `
            <td>${timeStr}</td>
            <td>${log.host}</td>
            <td class="${tagClass}">${log.event_type}</td>
            <td>${log.raw_message}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function fetchAlerts() {
    try {
        const res = await fetch(`${API_BASE}/alerts`);
        const alerts = await res.json();

        const activeCount = alerts.filter(a => a.status !== 'Benign').length;
        document.getElementById('alert-count').innerText = activeCount;
        renderAlerts(alerts);
    } catch (e) {
        console.error("Error fetching alerts:", e);
    }
}

function renderAlerts(alerts) {
    const container = document.getElementById('alerts-list');

    if (alerts.length === 0) {
        container.innerHTML = '<div class="empty-state">No active alerts...</div>';
        return;
    }

    container.innerHTML = '';
    alerts.forEach(alert => {
        const isBenign = alert.status === 'Benign';
        const card = document.createElement('div');
        card.className = `alert-card ${isBenign ? 'benign' : ''}`;

        let timeStr = "Unknown time";
        const d = new Date(alert.timestamp);
        if (!isNaN(d.getTime())) {
            timeStr = d.toLocaleString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        }

        card.innerHTML = `
            <div class="alert-header">
                <span class="alert-title">${alert.rule_triggered}</span>
                <span class="alert-time">${timeStr}</span>
            </div>
            <div class="alert-body">
                <strong>Host:</strong> ${alert.host}<br>
                ${alert.message}
            </div>
            <div class="alert-actions">
                ${isBenign
                ? `<span style="font-size:0.75rem; color: #10b981; font-weight: 400;">✓ Marked as Benign</span>
                       <button class="btn btn-outline" onclick="updateAlertStatus(${alert.id}, 'New')" style="margin-left: 0.5rem; padding: 0.25rem 0.5rem; font-size: 0.7rem;">Unmark</button>`
                : `<button class="btn btn-outline" onclick="updateAlertStatus(${alert.id}, 'Benign')">Mark Benign</button>
                       <button class="btn btn-primary" onclick="investigateAlert(${alert.id}, '${alert.host}')">Investigate</button>`
            }
            </div>
        `;
        container.appendChild(card);
    });
}

window.updateAlertStatus = async function (id, newStatus) {
    try {
        await fetch(`${API_BASE}/alerts/${id}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        fetchAlerts();
    } catch (e) {
        console.error("Error updating alert status:", e);
    }
}

let investigateWin = null;

window.investigateAlert = async function (id, host) {
    await updateAlertStatus(id, 'Investigating');

    const targetUrl = `/static/investigate.html?host=${host}`;
    if (!investigateWin || investigateWin.closed) {
        investigateWin = window.open(targetUrl, 'investigateWindow');
    } else {
        investigateWin.location.href = targetUrl;
        investigateWin.focus();
    }
}

document.getElementById('filter-type').addEventListener('change', fetchLogs);

// Init everything
window.onload = () => {
    initChart();
    fetchLogs();
    fetchAlerts();

    // Clear DB
    document.getElementById('clear-db-btn').addEventListener('click', () => {
        const modal = document.getElementById('clear-db-modal');
        const actions = document.getElementById('clear-db-actions');
        const msg = document.getElementById('clear-db-message');

        msg.innerText = "Are you sure you want to completely clear the database? All logs and alerts will be permanently deleted.";
        msg.style.color = "";
        actions.style.display = "flex";

        modal.classList.remove('hidden');
    });

    document.getElementById('cancel-clear-btn').addEventListener('click', () => {
        document.getElementById('clear-db-modal').classList.add('hidden');
    });

    document.getElementById('confirm-clear-btn').addEventListener('click', async () => {
        const actions = document.getElementById('clear-db-actions');
        const msg = document.getElementById('clear-db-message');

        try {
            actions.style.display = "none";
            msg.innerText = "Clearing database...";

            await fetch(`${API_BASE}/database`, { method: 'DELETE' });
            fetchLogs();
            fetchAlerts();
            if (eventsChart) {
                eventsChart.data.labels = [];
                eventsChart.data.datasets[0].data = [];
                eventsChart.update();
            }

            msg.innerText = "Database cleared successfully! New logs will begin populating automatically.";
            msg.style.color = "var(--success)";

            setTimeout(() => {
                document.getElementById('clear-db-modal').classList.add('hidden');
            }, 3000);

        } catch (e) {
            console.error("Error clearing DB:", e);
            msg.innerText = "Error clearing database. Check console.";
            msg.style.color = "var(--danger)";
            setTimeout(() => {
                document.getElementById('clear-db-modal').classList.add('hidden');
            }, 3000);
        }
    });

    // Toggle Theme
    const themes = ['theme-Dark', 'theme-Light', 'theme-Dracula', 'theme-Cyberpunk', 'theme-Solarized'];

    const savedTheme = localStorage.getItem('theme') || 'theme-Dark';
    let currentThemeIndex = themes.indexOf(savedTheme) !== -1 ? themes.indexOf(savedTheme) : 0;
    document.body.className = themes[currentThemeIndex];
    document.getElementById('theme-toggle-btn').innerText = `Theme: ${themes[currentThemeIndex].replace('theme-', '')}`;

    document.getElementById('theme-toggle-btn').addEventListener('click', () => {
        currentThemeIndex = (currentThemeIndex + 1) % themes.length;
        const newTheme = themes[currentThemeIndex];
        document.body.className = newTheme;
        localStorage.setItem('theme', newTheme);
        document.getElementById('theme-toggle-btn').innerText = `Theme: ${newTheme.replace('theme-', '')}`;

        if (eventsChart) {
            const isDark = !newTheme.includes('Light');
            eventsChart.options.scales.x.grid.color = isDark ? '#334155' : '#cbd5e1';
            eventsChart.options.scales.y.grid.color = isDark ? '#334155' : '#cbd5e1';
            eventsChart.update();
        }
    });

    window.addEventListener('storage', (e) => {
        if (e.key === 'theme') {
            document.body.className = e.newValue;
            currentThemeIndex = themes.indexOf(e.newValue);
            // Valid themes only!
            if (currentThemeIndex === -1) currentThemeIndex = 0;

            document.getElementById('theme-toggle-btn').innerText = `Theme: ${e.newValue.replace('theme-', '')}`;
            if (eventsChart) {
                const isDark = !e.newValue.includes('Light');
                eventsChart.options.scales.x.grid.color = isDark ? '#334155' : '#cbd5e1';
                eventsChart.options.scales.y.grid.color = isDark ? '#334155' : '#cbd5e1';
                eventsChart.update();
            }
        }
    });

    // Auto-refresh data every 1 second
    setInterval(() => {
        fetchLogs();
        fetchAlerts();
    }, 1000);
};

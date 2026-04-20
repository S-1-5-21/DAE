const API_BASE = 'http://localhost:8000/api';
let currentHost = null;

async function fetchTargetLogs() {
    if (!currentHost) return;
    try {
        const res = await fetch(`${API_BASE}/logs?host=${currentHost}`);
        const logs = await res.json();
        const tbody = document.getElementById('investigate-logs-body');
        tbody.innerHTML = '';

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="empty-state" style="text-align: center;">No logs found...</td></tr>';
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement('tr');
            let tagClass = 'tag-default';
            if (log.event_type === 'error') tagClass = 'tag-error';
            if (log.event_type === 'failed_login') tagClass = 'tag-failed_login';
            if (log.event_type === 'successful_login') tagClass = 'tag-successful_login';

            const d = new Date(log.timestamp);
            let timeStr = "Invalid Date";
            if (!isNaN(d.getTime())) {
                timeStr = d.toLocaleTimeString([], { hour12: false });
            }

            tr.innerHTML = `
                <td>${timeStr}</td>
                <td class="${tagClass}">${log.event_type}</td>
                <td>${log.raw_message}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error fetching logs for host:", e);
        document.getElementById('investigate-logs-body').innerHTML = '<tr><td colspan="3" class="empty-state" style="color:var(--danger); text-align: center;">Error fetching logs... check console.</td></tr>';
    }
}

window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const host = urlParams.get('host');
    
    if (host) {
        currentHost = host;
        document.getElementById('target-host-display').innerText = host;
        document.getElementById('page-title').innerText = `Investigating: ${host}`;
        document.title = `Investigating: ${host}`;
        fetchTargetLogs();
    } else {
        document.getElementById('target-host-display').innerText = "No Host Specified";
        document.getElementById('investigate-logs-body').innerHTML = '<tr><td colspan="3" class="empty-state" style="text-align: center;">Append ?host=... to URL</td></tr>';
    }

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
    });

    window.addEventListener('storage', (e) => {
        if (e.key === 'theme') {
            document.body.className = e.newValue;
            currentThemeIndex = themes.indexOf(e.newValue) !== -1 ? themes.indexOf(e.newValue) : 0;
            document.getElementById('theme-toggle-btn').innerText = `Theme: ${e.newValue.replace('theme-', '')}`;
        }
    });
};

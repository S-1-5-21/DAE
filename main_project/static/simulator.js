const API_BASE = 'http://localhost:8000/api';

const WEB_HOSTS = ["web-prod-01", "web-prod-02"];
const DB_HOSTS = ["db-prod-01"];
const WORKSTATIONS = ["workstation-102", "workstation-107"];
const USERS = ["jsmith", "bwayne", "ckent", "pwilson"];

const HOST_IPS = {
    "web-prod-01": "10.0.1.10",
    "web-prod-02": "10.0.1.11",
    "db-prod-01": "10.0.2.50",
    "workstation-102": "192.168.1.102",
    "workstation-107": "192.168.1.107"
};

let activityTimer = null;
const continuousLoops = {};

function randomChoice(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function logToOutput(msg, color = "#94a3b8") {
    const out = document.getElementById('sim-log-output');
    const d = new Date().toLocaleTimeString([], { hour12: false });
    const line = document.createElement('div');
    line.className = 'log-line';
    line.style.color = color;
    line.innerText = `[${d}] ${msg}`;
    out.prepend(line);
}

async function sendLog(host, eventType, message, sourceIp = null, destIp = null) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        host: host,
        event_type: eventType,
        raw_message: message,
        source_ip: sourceIp,
        dest_ip: destIp
    };

    try {
        await fetch(`${API_BASE}/logs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(logEntry)
        });
        logToOutput(`✓ ${host} [Src: ${sourceIp || 'N/A'} -> Dest: ${destIp || 'N/A'}] | ${eventType} | ${message}`);
    } catch (e) {
        logToOutput(`✗ ERROR: Could not send log to API`, 'var(--danger)');
        console.error(e);
    }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function generateNormalEvent() {
    const type = randomChoice(["web", "db", "workstation"]);

    if (type === "web") {
        const host = randomChoice(WEB_HOSTS);
        const evt = randomChoice(["page_view", "api_request"]);
        const clientIp = "203.0.113." + Math.floor(Math.random() * 255);
        await sendLog(host, evt, `Standard ${evt.replace('_', ' ')} from client IP`, clientIp, HOST_IPS[host]);
    } else if (type === "db") {
        const host = randomChoice(DB_HOSTS);
        const webHost = randomChoice(WEB_HOSTS);
        await sendLog(host, 'database_query', "Executed routine background query successfully", HOST_IPS[webHost], HOST_IPS[host]);
    } else {
        const host = randomChoice(WORKSTATIONS);
        const user = randomChoice(USERS);
        const evt = randomChoice(["successful_login", "file_access"]);
        await sendLog(host, evt, `User ${user} ${evt.replace('_', ' ')} routinely`, HOST_IPS[host], HOST_IPS[host]);
    }
}

function startActivity() {
    (async function loop() {
        if (!activityTimer) return;
        await generateNormalEvent();
        const nextDelay = 1000 + Math.random() * 3000; // 1 to 4 seconds
        activityTimer = setTimeout(loop, nextDelay);
    })();
}

function toggleActivity() {
    const btn = document.getElementById('toggle-activity');
    if (activityTimer) {
        clearTimeout(activityTimer);
        activityTimer = null;
        btn.classList.remove('active');
        btn.innerText = "Enable Background Activity";
        logToOutput("Background Activity Disabled", "var(--warning)");
    } else {
        activityTimer = setTimeout(() => { }, 0); // dummy init
        btn.classList.add('active');
        btn.innerText = "Disable Background Activity";
        logToOutput("Background Activity Enabled - Generating normal traffic...", "var(--success)");
        startActivity();
    }
}

document.getElementById('toggle-activity').addEventListener('click', toggleActivity);

// Scenarios

window.toggleContinuous = async function (scenario) {
    const btn = document.getElementById(`loop-${scenario}`);
    if (continuousLoops[scenario]) {
        continuousLoops[scenario] = false;
        btn.classList.remove('active');
        btn.innerText = "Continuous";
        logToOutput(`<<< STOPPED CONTINUOUS: ${scenario.toUpperCase()}`, "#ec4899");
    } else {
        continuousLoops[scenario] = true;
        btn.classList.add('active');
        btn.innerText = "Running...";
        logToOutput(`>>> STARTING CONTINUOUS: ${scenario.toUpperCase()}`, "#ec4899");

        while (continuousLoops[scenario]) {
            await runScenarioLogic(scenario);
            if (continuousLoops[scenario]) {
                await sleep(5000); // 5 sec sleep between loops
            }
        }
    }
}

window.triggerScenario = async function (scenario) {
    logToOutput(`>>> INITIATING SCENARIO (ONCE): ${scenario.toUpperCase()}`, "#ec4899");
    await runScenarioLogic(scenario);
    logToOutput(`<<< SCENARIO COMPLETE`, "#ec4899");
}

async function runScenarioLogic(scenario) {
    if (scenario === 'password_attack') {
        const host = randomChoice(WORKSTATIONS);
        const targetUser = randomChoice(["bwayne", "pwilson", "jsmith"]);
        const attackerIp = "192.168." + Math.floor(Math.random() * 255) + "." + Math.floor(Math.random() * 255);
        await sendLog(host, "successful_login", `User ${randomChoice(USERS)} logged in successfully.`, attackerIp, HOST_IPS[host]);
        await sleep(1000);
        for (let i = 0; i < 6; i++) {
            await sendLog(host, "failed_login", `Repeated authentication failure for user ${targetUser} from IP ${attackerIp}`, attackerIp, HOST_IPS[host]);
            await sleep(300);
        }

    } else if (scenario === 'server_failure') {
        const host = randomChoice(WEB_HOSTS);
        const errs = ["Database connection lost", "Gateway timeout 504", "Out of memory error", "Disk read failure on volume 1"];
        const clientIp = "203.0.113." + Math.floor(Math.random() * 255);
        await sendLog(host, "page_view", "User loaded the dashboard successfully.", clientIp, HOST_IPS[host]);
        await sleep(1000);
        for (let i = 0; i < 6; i++) {
            await sendLog(host, "error", `Critical service timeout: ${randomChoice(errs)} (${i + 1})`, HOST_IPS[host], HOST_IPS[host]);
            await sleep(400);
        }

    } else if (scenario === 'file_access') {
        const host = randomChoice(WORKSTATIONS);
        const files = ["/etc/shadow", "HR_Payroll_2026.xlsx", "Customer_Data_Dump.csv", "SSH_private_keys", "/var/log/auth.log"];
        await sendLog(host, "file_access", "User accessed public document /docs/policy.pdf", HOST_IPS[host], HOST_IPS[host]);
        await sleep(1000);
        for (let i = 0; i < 6; i++) {
            await sendLog(host, "file_access", `Restricted file access: Read attempt on ${randomChoice(files)} (${i + 1})`, HOST_IPS[host], HOST_IPS[host]);
            await sleep(300);
        }

    } else if (scenario === 'traffic_surge') {
        const host = randomChoice(WEB_HOSTS);
        const targetApi = `/api/v1/data-${Math.floor(Math.random() * 100)}`;
        const attackerIp = "198.51.100." + Math.floor(Math.random() * 255);
        for (let i = 0; i < 2; i++) {
            const clientIp = "203.0.113." + Math.floor(Math.random() * 255);
            await sendLog(host, "api_request", "Normal API request /api/v1/health", clientIp, HOST_IPS[host]);
            await sleep(500);
        }
        for (let i = 0; i < 16; i++) {
            await sendLog(host, "api_request", `Overwhelming API request flood from single origin targeting ${targetApi} (${i + 1})`, attackerIp, HOST_IPS[host]);
            await sleep(50);
        }

    } else if (scenario === 'privilege_misuse') {
        const host = randomChoice(WORKSTATIONS);
        const user = randomChoice(["jsmith", "ckent", "pwilson"]);
        const actions = [
            "modified security group policies",
            "deleted production database backups",
            "changed firewall rules",
            "created a hidden admin account",
            "disabled endpoint protection"
        ];
        await sendLog(host, "successful_login", `Standard user ${user} logged in.`, HOST_IPS[host], HOST_IPS[host]);
        await sleep(1000);
        for (let i = 0; i < 4; i++) {
            await sendLog(host, "admin_action", `Admin-only action executed: ${user} ${randomChoice(actions)}.`, HOST_IPS[host], HOST_IPS[host]);
            await sleep(500);
        }
    } else if (scenario === 'port_scan') {
        const attackerIp = "192.168.1." + Math.floor(Math.random() * 255);
        const targetHost = randomChoice(WEB_HOSTS);
        await sendLog(targetHost, "network_connection", `Inbound connection from ${attackerIp} on port 80`, attackerIp, HOST_IPS[targetHost]);
        await sleep(500);
        for (let i = 0; i < 6; i++) {
            await sendLog(targetHost, "network_connection", `Blocked connection from ${attackerIp} on rapid port progression (Port ${1024 + i * 15})`, attackerIp, HOST_IPS[targetHost]);
            await sleep(200);
        }

    } else if (scenario === 'data_exfiltration') {
        const host = randomChoice(DB_HOSTS);
        const webHost = randomChoice(WEB_HOSTS);
        await sendLog(host, "database_query", "User executed routine background query successfully", HOST_IPS[webHost], HOST_IPS[host]);
        await sleep(1000);
        const externalIp = "198.51.100." + Math.floor(Math.random() * 255);
        for (let i = 0; i < 4; i++) {
            await sendLog(host, "data_transfer", `Unusual large outward data transfer to unknown external IP (${(i + 1) * 50} MB)`, HOST_IPS[host], externalIp);
            await sleep(600);
        }

    } else if (scenario === 'malware_execution') {
        const host = randomChoice(WORKSTATIONS);
        await sendLog(host, "file_access", "User downloaded email attachment 'invoice_final.doc'", HOST_IPS[host], HOST_IPS[host]);
        await sleep(1000);
        for (let i = 0; i < 3; i++) {
            await sendLog(host, "process_creation", "Suspicious process spawned: powershell.exe -ExecutionPolicy Bypass -encodedCommand...", HOST_IPS[host], HOST_IPS[host]);
            await sleep(800);
        }
    }
}

window.onload = () => {
    const themes = ['theme-Dark', 'theme-Dracula', 'theme-Cyberpunk', 'theme-Solarized'];

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

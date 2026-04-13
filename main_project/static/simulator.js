const API_BASE = 'http://localhost:8000/api';

const WEB_HOSTS = ["web-prod-01", "web-prod-02"];
const DB_HOSTS = ["db-prod-01"];
const WORKSTATIONS = ["workstation-102", "workstation-107"];
const USERS = ["jsmith", "bwayne", "ckent", "pwilson"];

let heartbeatTimer = null;
const continuousLoops = {};

function randomChoice(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function logToOutput(msg, color="#94a3b8") {
    const out = document.getElementById('sim-log-output');
    const d = new Date().toLocaleTimeString([], { hour12: false });
    const line = document.createElement('div');
    line.className = 'log-line';
    line.style.color = color;
    line.innerText = `[${d}] ${msg}`;
    out.prepend(line);
}

async function sendLog(host, eventType, message) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        host: host,
        event_type: eventType,
        raw_message: message
    };

    try {
        await fetch(`${API_BASE}/logs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(logEntry)
        });
        logToOutput(`✓ ${host} | ${eventType} | ${message}`);
    } catch(e) {
        logToOutput(`✗ ERROR: Could not send log to API`, 'var(--danger)');
        console.error(e);
    }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Background Normal Traffic
async function generateNormalEvent() {
    const type = randomChoice(["web", "db", "workstation"]);
    
    if (type === "web") {
        const host = randomChoice(WEB_HOSTS);
        const evt = randomChoice(["page_view", "api_request"]);
        await sendLog(host, evt, `Standard ${evt.replace('_', ' ')} from client IP`);
    } else if (type === "db") {
        const host = randomChoice(DB_HOSTS);
        await sendLog(host, 'database_query', "Executed routine background query successfully");
    } else {
        const host = randomChoice(WORKSTATIONS);
        const user = randomChoice(USERS);
        const evt = randomChoice(["successful_login", "file_access"]);
        await sendLog(host, evt, `User ${user} ${evt.replace('_', ' ')} routinely`);
    }
}

function startHeartbeat() {
    (async function loop() {
        if(!heartbeatTimer) return;
        await generateNormalEvent();
        const nextDelay = 1000 + Math.random() * 3000; // 1 to 4 seconds
        heartbeatTimer = setTimeout(loop, nextDelay);
    })();
}

function toggleHeartbeat() {
    const btn = document.getElementById('toggle-heartbeat');
    if(heartbeatTimer) {
        clearTimeout(heartbeatTimer);
        heartbeatTimer = null;
        btn.classList.remove('active');
        btn.innerText = "Enable Background Heartbeat";
        logToOutput("Heartbeat Disabled", "var(--warning)");
    } else {
        heartbeatTimer = setTimeout(() => {}, 0); // dummy init
        btn.classList.add('active');
        btn.innerText = "Disable Background Heartbeat";
        logToOutput("Heartbeat Enabled - Generating normal traffic...", "var(--success)");
        startHeartbeat();
    }
}

document.getElementById('toggle-heartbeat').addEventListener('click', toggleHeartbeat);

// --- SCENARIO TRIGGERS ---

window.toggleContinuous = async function(scenario) {
    const btn = document.getElementById(`loop-${scenario}`);
    if (continuousLoops[scenario]) {
        continuousLoops[scenario] = false;
        btn.classList.remove('active', 'btn-primary');
        btn.classList.add('btn-outline');
        btn.innerText = "Continuous";
        logToOutput(`<<< STOPPED CONTINUOUS: ${scenario.toUpperCase()}`, "#ec4899");
    } else {
        continuousLoops[scenario] = true;
        btn.classList.add('active', 'btn-primary');
        btn.classList.remove('btn-outline');
        btn.innerText = "Running...";
        logToOutput(`>>> STARTING CONTINUOUS: ${scenario.toUpperCase()}`, "#ec4899");
        
        while (continuousLoops[scenario]) {
            await runScenarioLogic(scenario);
            if (continuousLoops[scenario]) {
                await sleep(5000); // 5 sec gap between loops
            }
        }
    }
}

window.triggerScenario = async function(scenario) {
    logToOutput(`>>> INITIATING SCENARIO (ONCE): ${scenario.toUpperCase()}`, "#ec4899");
    await runScenarioLogic(scenario);
    logToOutput(`<<< SCENARIO COMPLETE`, "#ec4899");
}

async function runScenarioLogic(scenario) {
    if (scenario === 'password_attack') {
        const host = randomChoice(WORKSTATIONS);
        const targetUser = randomChoice(["bwayne", "pwilson", "jsmith"]);
        const attackerIp = "192.168." + Math.floor(Math.random() * 255) + "." + Math.floor(Math.random() * 255);
        await sendLog(host, "successful_login", `User ${randomChoice(USERS)} logged in successfully.`);
        await sleep(1000);
        for(let i=0; i<6; i++) {
            await sendLog(host, "failed_login", `Repeated authentication failure for user ${targetUser} from IP ${attackerIp}`);
            await sleep(300);
        }
        
    } else if (scenario === 'server_failure') {
        const host = randomChoice(WEB_HOSTS);
        const errs = ["Database connection lost", "Gateway timeout 504", "Out of memory error", "Disk read failure on volume 1"];
        await sendLog(host, "page_view", "User loaded the dashboard successfully.");
        await sleep(1000);
        for(let i=0; i<6; i++) {
            await sendLog(host, "error", `Critical service timeout: ${randomChoice(errs)} (${i+1})`);
            await sleep(400);
        }
        
    } else if (scenario === 'file_access') {
        const host = randomChoice(WORKSTATIONS);
        const files = ["/etc/shadow", "HR_Payroll_2026.xlsx", "Customer_Data_Dump.csv", "SSH_private_keys", "/var/log/auth.log"];
        await sendLog(host, "file_access", "User accessed public document /docs/policy.pdf");
        await sleep(1000);
        for(let i=0; i<6; i++) {
            await sendLog(host, "file_access", `Restricted file access: Read attempt on ${randomChoice(files)} (${i+1})`);
            await sleep(300);
        }
        
    } else if (scenario === 'traffic_surge') {
        const host = randomChoice(WEB_HOSTS);
        const targetApi = `/api/v1/data-${Math.floor(Math.random()*100)}`;
        for(let i=0; i<2; i++) {
            await sendLog(host, "api_request", "Normal API request /api/v1/health");
            await sleep(500);
        }
        for(let i=0; i<16; i++) {
            await sendLog(host, "api_request", `Overwhelming API request flood from single origin targeting ${targetApi} (${i+1})`);
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
        await sendLog(host, "successful_login", `Standard user ${user} logged in.`);
        await sleep(1000);
        for(let i=0; i<4; i++) {
            await sendLog(host, "admin_action", `Admin-only action executed: ${user} ${randomChoice(actions)}.`);
            await sleep(500);
        }
    }
}

window.onload = () => {
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
        if(e.key === 'theme') {
            document.body.className = e.newValue;
            currentThemeIndex = themes.indexOf(e.newValue) !== -1 ? themes.indexOf(e.newValue) : 0;
            document.getElementById('theme-toggle-btn').innerText = `Theme: ${e.newValue.replace('theme-', '')}`;
        }
    });
};

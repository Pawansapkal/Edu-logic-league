function resolveApiBase() {
    const configuredBase = localStorage.getItem('apiBaseUrl');
    if (configuredBase) {
        return `${configuredBase.replace(/\/+$/, '')}/api`;
    }

    const { hostname, origin, port, protocol } = window.location;
    if (port === '5000') {
        return `${origin}/api`;
    }

    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return `${protocol}//${hostname}:5000/api`;
    }

    // Production: Use deployed Render backend
    return 'https://edu-logic-league-backend.onrender.com/api';
}

const API_BASE = resolveApiBase();

// Keep-alive mechanism to prevent Render backend from sleeping
function startHealthCheck() {
    setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
            if (!response.ok) {
                console.warn('Health check failed:', response.status);
            }
        } catch (error) {
            // Silently fail - this is just to keep backend awake
            console.debug('Health check error (expected):', error.message);
        }
    }, 4 * 60 * 1000); // Check every 4 minutes
}

// Start health check on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startHealthCheck);
} else {
    startHealthCheck();
}

async function requestJson(path, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${path}`, options);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const message = data.error || 'Request failed.';
            throw new Error(message);
        }

        return data;
    } catch (error) {
        // Check if this is a network error (backend unreachable)
        if (error instanceof TypeError || error.message.includes('Failed to fetch')) {
            const errorMsg = `Backend unreachable: ${API_BASE}\nMake sure the backend is deployed and running on Render.com`;
            console.error(errorMsg);
            throw new Error('Login failed: Backend is not accessible. Make sure it\'s deployed on Render.com.');
        }
        throw error;
    }
}

async function createUser(username) {
    return requestJson('/user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
    });
}

async function fetchUserData(username) {
    try {
        return await requestJson(`/user/${encodeURIComponent(username)}`);
    } catch (error) {
        if (error.message === 'User not found') {
            return createUser(username);
        }
        console.error('Error fetching user:', error);
        throw error;
    }
}

async function fetchChallenge() {
    try {
        return await requestJson('/challenge');
    } catch (error) {
        console.error('Error fetching challenge:', error);
        throw error;
    }
}

async function submitAnswerAPI(username, challengeId, answer) {
    try {
        return await requestJson('/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                challenge_id: challengeId,
                answer
            })
        });
    } catch (error) {
        console.error('Error submitting answer:', error);
        throw error;
    }
}

async function fetchDashboardData(username) {
    try {
        return await requestJson(`/dashboard/${encodeURIComponent(username)}`);
    } catch (error) {
        console.error('Error fetching dashboard:', error);
        throw error;
    }
}

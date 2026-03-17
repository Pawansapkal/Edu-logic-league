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

    return `${origin}/api`;
}

const API_BASE = resolveApiBase();

async function requestJson(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const message = data.error || 'Request failed.';
        throw new Error(message);
    }

    return data;
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

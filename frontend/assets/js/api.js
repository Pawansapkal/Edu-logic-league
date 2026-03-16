// This file handles all communication with the Python backend
const API_BASE = 'http://localhost:5000/api';

async function fetchUserData(username) {
    try {
        const response = await fetch(`${API_BASE}/user/${username}`);
        return await response.json();
    } catch (error) {
        console.error("Error fetching user:", error);
    }
}

async function fetchChallenge() {
    try {
        const response = await fetch(`${API_BASE}/challenge`);
        return await response.json();
    } catch (error) {
        console.error("Error fetching challenge:", error);
    }
}

async function submitAnswerAPI(username, challengeId, answer) {
    try {
        const response = await fetch(`${API_BASE}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                challenge_id: challengeId,
                answer: answer
            })
        });
        return await response.json();
    } catch (error) {
        console.error("Error submitting answer:", error);
    }
}

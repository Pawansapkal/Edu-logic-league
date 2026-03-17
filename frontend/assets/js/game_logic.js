// Check if user is logged in
const currentUser = localStorage.getItem('currentUser');
if (!currentUser) window.location.href = 'index.html';

let currentChallengeId = null;

// Initialize the Arena
async function initArena() {
    const feedbackEl = document.getElementById('feedback');

    try {
        // 1. Load User Stats
        const user = await fetchUserData(currentUser);
        document.getElementById('playerName').innerText = user.username;
        document.getElementById('playerXP').innerText = user.xp;
        document.getElementById('playerLevel').innerText = user.level;

        // 2. Load Challenge
        const challenge = await fetchChallenge();
        currentChallengeId = challenge.id;
        document.getElementById('subjectLabel').innerText = challenge.subject;
        document.getElementById('questionText').innerText = challenge.question;

        // 3. Render Buttons
        const optionsContainer = document.getElementById('optionsContainer');
        optionsContainer.innerHTML = '';

        challenge.options.forEach(option => {
            const btn = document.createElement('button');
            btn.innerText = option;
            btn.className = 'bg-slate-700 hover:bg-slate-600 border border-slate-600 text-white font-bold py-4 px-6 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg';
            btn.onclick = () => handleAnswerClick(option);
            optionsContainer.appendChild(btn);
        });

        feedbackEl.classList.add('hidden');
    } catch (error) {
        feedbackEl.classList.remove('hidden');
        feedbackEl.classList.add('text-red-400');
        feedbackEl.innerText = error.message || 'Unable to load the arena.';
    }
}

// Handle User Clicking an Answer
async function handleAnswerClick(selectedOption) {
    const feedbackEl = document.getElementById('feedback');
    feedbackEl.classList.remove('hidden', 'text-emerald-400', 'text-red-400');
    feedbackEl.innerText = 'Checking...';

    try {
        const result = await submitAnswerAPI(currentUser, currentChallengeId, selectedOption);

        if (result.correct) {
            feedbackEl.classList.add('text-emerald-400');
            feedbackEl.innerText = `🔥 ${result.message}`;

            document.getElementById('playerXP').innerText = result.new_xp;
            document.getElementById('playerLevel').innerText = result.new_level;

            setTimeout(initArena, 2000);
        } else {
            feedbackEl.classList.add('text-red-400');
            feedbackEl.innerText = `❌ ${result.message}`;
        }
    } catch (error) {
        feedbackEl.classList.add('text-red-400');
        feedbackEl.innerText = error.message || 'Unable to submit answer.';
    }
}

// Start the game when page loads
window.onload = initArena;

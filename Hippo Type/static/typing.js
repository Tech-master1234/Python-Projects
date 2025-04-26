const wordsEl = document.getElementById("words");
const gameEl = document.getElementById("game");
const infoEl = document.getElementById("info");
const newGameBtn = document.getElementById("newGameBtn");
const gameControlsEl = document.getElementById("game-controls");
const tryAgainBtn = document.getElementById("tryAgainBtn");
const nextBtn = document.getElementById("nextBtn");
const resultsEl = document.getElementById("results");
const statsEl = document.getElementById("stats");
const averageWpmEl = document.getElementById("average-wpm");

let words = [];
let currentWordIndex = 0;
let currentLetterIndex = 0;
let startTime = null;
let gameEnded = false;

let totalTyped = 0;
let correctTyped = 0;

// Get words and level from the template
const wordList = JSON.parse(document.getElementById('words').dataset.words || '[]');
const currentLevel = parseInt(document.getElementById('words').dataset.level || '1');

function renderWords() {
    wordsEl.innerHTML = "";
    words = [];

    for (let i = 0; i < 25; i++) {
        const wordText = wordList[Math.floor(Math.random() * wordList.length)];
        const wordEl = document.createElement("div");
        wordEl.className = "word";

        const letters = [];
        // Add space after word if it's not the last word
        const textToRender = i < 24 ? wordText + " " : wordText;

        for (let char of textToRender) {
            const span = document.createElement("span");
            span.textContent = char;
            span.className = "letter";
            span.setAttribute('data-char', char);
            wordEl.appendChild(span);
            letters.push(span);
        }

        words.push({ wordText: textToRender, letters });
        wordsEl.appendChild(wordEl);
    }
}

function resetGame() {
    currentWordIndex = 0;
    currentLetterIndex = 0;
    totalTyped = 0;
    correctTyped = 0;
    startTime = null;
    gameEnded = false;
    infoEl.textContent = "Current WPM: 0";
    gameEl.classList.remove("over");
    gameControlsEl.style.display = "none";
    resultsEl.style.display = "none";

    renderWords();

    // Initialize average WPM if it doesn't exist
    if (!localStorage.getItem("averageWpm")) {
        localStorage.setItem("averageWpm", "0");
    }
    if (!localStorage.getItem("gamesPlayed")) {
        localStorage.setItem("gamesPlayed", "0");
    }
}

function endGame() {
    gameEnded = true;
    gameEl.classList.add("over");

    // Calculate duration in minutes
    const duration = (Date.now() - startTime) / 1000 / 60;
    
    // Calculate current WPM (5 characters = 1 word)
    const currentWpm = Math.round((correctTyped / 5) / duration);
    
    // Calculate accuracy
    const accuracy = Math.round((correctTyped / totalTyped) * 100) || 0;

    // Calculate score
    const score = Math.round(currentWpm * (accuracy / 100));

    // Get current stats
    const oldAverage = parseFloat(localStorage.getItem("averageWpm")) || 0;
    const gamesPlayed = parseInt(localStorage.getItem("gamesPlayed")) || 0;
    
    // Calculate new average
    let newAverage;
    if (gamesPlayed === 0) {
        newAverage = currentWpm;
    } else {
        newAverage = (oldAverage * gamesPlayed + currentWpm) / (gamesPlayed + 1);
    }
    
    // Save new values
    localStorage.setItem("averageWpm", newAverage.toFixed(2));
    localStorage.setItem("gamesPlayed", (gamesPlayed + 1).toString());

    // Display stats
    statsEl.textContent = `Average WPM: ${Math.round(newAverage)} | Accuracy: ${accuracy}%`;
    averageWpmEl.textContent = `Score: ${score}`;
    
    // Show results and controls
    resultsEl.style.display = "block";
    gameControlsEl.style.display = "flex";
    infoEl.textContent = "";

    // Save score to server
    fetch('/save_score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            wpm: currentWpm,
            accuracy: accuracy
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update leaderboard without page reload
            fetch('/')
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newLeaderboard = doc.querySelector('#leaderboard');
                    if (newLeaderboard) {
                        document.querySelector('#leaderboard').innerHTML = newLeaderboard.innerHTML;
                    }
                });
        }
    })
    .catch(error => console.error('Error saving score:', error));

    // If playing a level, submit the score
    if (currentLevel) {
        submitLevelScore(score);
    }
}

function updateWpmDisplay() {
    if (!startTime) return;
    
    const duration = (Date.now() - startTime) / 1000 / 60;
    if (duration === 0) return;
    
    const currentWpm = Math.round((correctTyped / 5) / duration);
    infoEl.textContent = `Current WPM: ${currentWpm}`;
}

gameEl.addEventListener("keydown", (e) => {
    if (gameEnded) return;

    // Prevent space bar from scrolling
    if (e.code === "Space") {
        e.preventDefault();
    }

    // Start timer on first keypress
    if (!startTime) {
        startTime = Date.now();
    }

    // Backspace logic
    if (e.key === "Backspace") {
        e.preventDefault();
        if (currentLetterIndex > 0) {
            currentLetterIndex--;
            const letterSpan = words[currentWordIndex].letters[currentLetterIndex];
            if (letterSpan) {
                letterSpan.classList.remove("correct", "incorrect");
            }
        } else if (currentWordIndex > 0) {
            currentWordIndex--;
            currentLetterIndex = words[currentWordIndex].letters.length - 1;
            const letterSpan = words[currentWordIndex].letters[currentLetterIndex];
            if (letterSpan) {
                letterSpan.classList.remove("correct", "incorrect");
            }
        }
        return;
    }

    // Skip non-character keys
    if (e.key.length !== 1) return;

    const wordObj = words[currentWordIndex];
    const currentLetter = wordObj.letters[currentLetterIndex];

    // Typing logic
    if (e.key === wordObj.wordText[currentLetterIndex]) {
        currentLetter.classList.add("correct");
        currentLetter.classList.remove("incorrect");
        correctTyped++;
    } else {
        currentLetter.classList.add("incorrect");
        currentLetter.classList.remove("correct");
    }
    totalTyped++;
    currentLetterIndex++;

    // Word transition
    if (currentLetterIndex >= wordObj.letters.length) {
        currentWordIndex++;
        currentLetterIndex = 0;
        if (currentWordIndex >= words.length) {
            endGame();
        }
    }

    // Update WPM display
    updateWpmDisplay();
});

gameEl.addEventListener("click", () => {
    gameEl.focus();
});

newGameBtn.addEventListener("click", () => {
    resetGame();
    gameEl.focus();
});

// Add event listeners for the new buttons
tryAgainBtn.addEventListener("click", () => {
    resetGame();
    gameEl.focus();
});

nextBtn.addEventListener("click", () => {
    // Go to next level
    window.location.href = `/play/${currentLevel + 1}`;
});

// Initialize the game
resetGame();

// Prevent scrolling when space is pressed
document.addEventListener('keydown', function(e) {
    if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
    }
});

async function submitLevelScore(score) {
    try {
        // Calculate duration in minutes
        const duration = (Date.now() - startTime) / 1000 / 60;
        
        // Calculate current WPM (5 characters = 1 word)
        const currentWpm = Math.round((correctTyped / 5) / duration);
        
        // Calculate accuracy
        const accuracy = Math.round((correctTyped / totalTyped) * 100) || 0;

        const response = await fetch('/complete_level', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                level: currentLevel,
                score: score,
                accuracy: accuracy,
                wpm: currentWpm
            })
        });
        
        const data = await response.json();
        if (data.success) {
            // Enable the next level button
            nextBtn.style.display = 'block';
        } else if (data.error === 'Level requirements not met') {
            // Show error message to user
            alert(data.message);
            nextBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error submitting score:', error);
        nextBtn.style.display = 'none';
    }
}

function updateLeaderboard() {
    // Implementation of updateLeaderboard function
}

document.addEventListener('keydown', function(event) {
    // Check if the spacebar is pressed
    if (event.code === 'Space' && (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA')) {
        event.preventDefault(); // Prevent the default scrolling behavior
    }
});
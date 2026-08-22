const API_BASE = "http://127.0.0.1:8000/multimedia";
const OUTPUT_BASE = "http://127.0.0.1:8000";

const content = document.getElementById("content");
const question = document.getElementById("question");
const audioFile = document.getElementById("audioFile");

const output = document.getElementById("output");
const audioPlayer = document.getElementById("audioPlayer");
const generatedImage = document.getElementById("generatedImage");

// -------------------------------------
// Helper Functions
// -------------------------------------

function showLoading(message = "Processing...") {
    output.textContent = message;
}

function showError(error) {
    output.textContent = "❌ " + error;
}

// -------------------------------------
// Generate Summary
// -------------------------------------

document.getElementById("summaryBtn").onclick = async () => {

    if (!content.value.trim()) {
        alert("Please enter educational content.");
        return;
    }

    showLoading("Generating summary...");

    try {

        const response = await fetch(`${API_BASE}/summary`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: content.value
            })
        });

        const data = await response.json();

        output.textContent = data.summary;

    } catch (error) {

        showError(error.message);

    }

};

// -------------------------------------
// Text To Speech
// -------------------------------------

document.getElementById("audioBtn").onclick = async () => {

    if (!content.value.trim()) {
        alert("Please enter educational content.");
        return;
    }

    showLoading("Generating audio...");

    try {

        const response = await fetch(`${API_BASE}/tts`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: content.value
            })

        });

        const data = await response.json();

        output.textContent = data.message;

        // Backend returns backend/outputs/audio/file.mp3
        // Convert to browser URL

        const fileName = data.audio_path.split("/").pop();

        audioPlayer.src =
            `${OUTPUT_BASE}/outputs/audio/${fileName}`;

        audioPlayer.load();

    }

    catch (error) {

        showError(error.message);

    }

};

// -------------------------------------
// Speech To Text
// -------------------------------------

document.getElementById("sttBtn").onclick = async () => {

    output.textContent =
        "Speech-to-Text endpoint will be updated to support UploadFile.";

};

// -------------------------------------
// Ask AI
// -------------------------------------

document.getElementById("askBtn").onclick = async () => {

    if (!question.value.trim()) {

        alert("Please enter a question.");

        return;
    }

    showLoading("Generating answer...");

    try {

        const response = await fetch(`${API_BASE}/ask`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                question: question.value,

                context: content.value

            })

        });

        const data = await response.json();

        output.textContent = data.answer;

    }

    catch (error) {

        showError(error.message);

    }

};

// -------------------------------------
// Generate Image
// -------------------------------------

document.getElementById("imageBtn").onclick = async () => {

    if (!content.value.trim()) {
        alert("Please enter educational content.");
        return;
    }

    showLoading("Generating image...");

    try {

        const response = await fetch(

            `${API_BASE}/image?prompt=${encodeURIComponent(content.value)}`,

            {
                method: "POST"
            }

        );

        const data = await response.json();

        output.textContent = data.message;

        const fileName = data.image_path.split("/").pop();

        generatedImage.src =
            `${OUTPUT_BASE}/outputs/images/${fileName}`;

        generatedImage.style.display = "block";

    }

    catch (error) {

        showError(error.message);

    }

};

// -------------------------------------
// Generate Video Script
// -------------------------------------

document.getElementById("videoBtn").onclick = async () => {

    if (!content.value.trim()) {
        alert("Please enter educational content.");
        return;
    }

    showLoading("Generating video script...");

    try {

        const response = await fetch(

            `${API_BASE}/video?topic=${encodeURIComponent(content.value)}`,

            {
                method: "POST"
            }

        );

        const data = await response.json();

        output.textContent = data.script;

    }

    catch (error) {

        showError(error.message);

    }

};
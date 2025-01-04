function scrollToBottom() {
    var chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;
}

window.onload = scrollToBottom;

function updateSelectedTopic() {
    const selectedOption = document.querySelector('input[name="topic"]:checked');
    const selectedTopicField = document.getElementById("selected_topic");
    const customTopicInput = document.querySelector('input[name="custom_topic_input"]');

    if (selectedOption && selectedOption.value === "other") {
        selectedTopicField.value = customTopicInput.value;
    } else if (selectedOption) {
        selectedTopicField.value = selectedOption.value;
    } 
}

document.addEventListener("DOMContentLoaded", function() {
    // listener for topic
    document.querySelectorAll('input[name="topic"]').forEach(radio => {
        radio.addEventListener("change", updateSelectedTopic);
    });
    
    // listener for "Other" input field
    document.querySelector('input[name="custom_topic_input"]').addEventListener("input", function() {
        const selectedOption = document.querySelector('input[name="topic"]:checked');
        if (selectedOption && selectedOption.value === "other") {
            updateSelectedTopic();
        }
    });

    // populate all fields on form submission
    document.querySelector("form").addEventListener("submit", function() {
        updateSelectedTopic();
        setTimeout(scrollToBottom, 100);
    });

    document.getElementById("news-button").addEventListener("click", function() {
        fetch('/test_emit');
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Add click listeners to bold, clickable words
    document.getElementById("chat-box").addEventListener("click", function (event) {
        if (event.target.classList.contains("clickable-word")) {
            const word = event.target.innerText; // Get the clicked bolded word
            fetchImageForWord(word); // Fetch image for the clicked word
        }
    });
});

function fetchImageForWord(word) {
    // Example of sending the bolded word to the backend for image description
    // fetch("/generate-image-description", {
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json",
    //     },
    //     body: JSON.stringify({ word: word }),
    // })
    //     .then((response) => response.json())
    //     .then((data) => {
    //         const imageUrl = data.image_url; // Get image URL from response
    //         displayImagePopup(word, imageUrl); // Show image popup
    //     })
    //     .catch((error) => console.error("Error fetching image:", error));
    console.log("made it here")
}

function displayImagePopup(word, imageUrl) {
    const popup = document.createElement("div");
    popup.classList.add("image-popup");
    popup.innerHTML = `
        <h3>${word}</h3>
        <img src="${imageUrl}" alt="${word}">
        <button onclick="this.parentElement.remove()">Close</button>
    `;
    document.body.appendChild(popup);
}
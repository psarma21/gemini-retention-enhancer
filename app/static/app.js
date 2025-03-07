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
    document.querySelectorAll('input[name="topic"]').forEach(radio => {
        radio.addEventListener("change", updateSelectedTopic);
    });
    
    document.querySelector('input[name="custom_topic_input"]').addEventListener("input", function() {
        const selectedOption = document.querySelector('input[name="topic"]:checked');
        if (selectedOption && selectedOption.value === "other") {
            updateSelectedTopic();
        }
    });

    document.querySelector("form").addEventListener("submit", function() {
        updateSelectedTopic();
        setTimeout(scrollToBottom, 100);
    });

    document.getElementById("news-button").addEventListener("click", function() {
        fetch('/test_emit');
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("chat-box").addEventListener("click", function (event) {
        if (event.target.classList.contains("clickable-word")) {
            const word = event.target.innerText; 
            fetchImageForWord(word); 
        }
    });
});

function fetchImageForWord(word) {
    fetch("/generate-image-description", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ word: word }),
    })
        .then((response) => response.json())
        .then((data) => {
            const imageUrl = data.image_url; 
            const caption = data.caption; 
            displayImagePopup(word, imageUrl, caption); 
        })
        .catch((error) => console.error("Error fetching image:", error));
}

function displayImagePopup(word, imageUrl, caption) {
    const overlay = document.createElement("div");
    overlay.classList.add("image-popup-overlay");
    
    const popup = document.createElement("div");
    popup.classList.add("image-popup");
    
    popup.innerHTML = `
        <button class="close-button" aria-label="Close popup">×</button>
        <h3>${caption}</h3>
        <img src="${imageUrl}" alt="${word}" loading="lazy">
    `;
    
    const closePopup = () => {
        overlay.remove();
        popup.remove();
    };
    
    popup.querySelector('.close-button').addEventListener('click', closePopup);
    
    overlay.addEventListener('click', closePopup);
    
    popup.addEventListener('click', (e) => {
        e.stopPropagation();
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopup();
        }
    });
    
    document.body.appendChild(overlay);
    document.body.appendChild(popup);
}

// Metrics

// #1 - Number of clicks by user
let clickCount = localStorage.getItem("clickCount") ? parseInt(localStorage.getItem("clickCount")) : 0;
console.log("Number of clicks (saved):", clickCount); // Display initial count in console
document.addEventListener("click", () => {
    clickCount++;  
    localStorage.setItem("clickCount", clickCount); // Save updated count
    console.log("Number of clicks:", clickCount);
});
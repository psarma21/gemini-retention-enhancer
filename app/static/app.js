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
});
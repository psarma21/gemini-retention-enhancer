from flask import Flask, request, render_template_string, session
from wrapper.main import get_gemini_response
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Define the HTML template with updated styling for scrollable chat history
html_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chat with Gemini AI</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f7f7f8;
            color: #1c1e21;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container {
            display: flex;
            flex-direction: column;
            width: 100%;
            height: 100%;
            box-shadow: none;
            padding: 0;
            margin: 0;
        }
        .chat-box {
            flex-grow: 1;
            overflow-y: auto;
            border-top: 1px solid #e0e0e0;
            padding: 20px;
            background-color: #f7f7f7;
            display: flex;
            flex-direction: column;
        }
        h1 {
            color: #3a3b3c;
            font-weight: 600;
            text-align: center;
            margin: 20px 0;
        }
        form {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px;
            background-color: #ffffff;
            border-top: 1px solid #ddd;
        }
        input[type="text"] {
            flex-grow: 1;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        input[type="submit"] {
            padding: 15px 25px;
            border: none;
            border-radius: 6px;
            background-color: #007bff;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .message {
            max-width: 75%;
            padding: 12px 18px;
            margin: 10px 0;
            border-radius: 15px;
            line-height: 1.6;
            word-wrap: break-word;
            font-size: 16px;
        }
        .message.user {
            align-self: flex-end;
            background-color: #e1ffc7;
        }
        .message.ai {
            align-self: flex-start;
            background-color: #dbeafe;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chat with Gemini AI</h1>
        <div class="chat-box" id="chat-box">
            {% for message in chat_history %}
                <div class="message {{ message.type }}">{% autoescape false %}{{ message.text }}{% endautoescape %}</div>
            {% endfor %}
        </div>
        <form method="post" action="/">
            <input type="text" name="user_input" placeholder="Enter your query" required autofocus>
            <input type="submit" value="Send">
        </form>
    </div>
</body>
</html>
"""

def format_text(text):
    # Replace **text** with <b>text</b> for bold formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Replace *text* with <i>text</i> for italic formatting
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Convert newlines to <br> for line breaks
    text = text.replace("\n", "<br>")

    # Handle bullet points by replacing "* " at the start of lines with an HTML list item
    text = re.sub(r'(\* .+)', r'<li>\1</li>', text)  # Wrap bullet points in <li> tags
    text = text.replace("<li>* ", "<li>")  # Remove the "*" from the bullet points

    # Add <ul> tags around the list items
    if "<li>" in text:
        text = "<ul>" + text + "</ul>"

    # Handle code blocks enclosed in triple backticks ``` with <pre><code> tags
    text = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)

    # Escape special HTML characters inside code blocks
    text = re.sub(r'(<pre><code>)(.*?)(</code></pre>)', 
                  lambda match: match.group(1) + match.group(2).replace('<', '&lt;').replace('>', '&gt;') + match.group(3), 
                  text, flags=re.DOTALL)
    
    return text


@app.route("/", methods=["GET", "POST"])
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == "POST":
        user_input = request.form.get("user_input")
        ai_response = get_gemini_response(user_input)

        # Format the AI response text
        formatted_response = format_text(ai_response)

        # Save user input and formatted AI response to chat history
        session['chat_history'].append({'type': 'user', 'text': user_input})
        session['chat_history'].append({'type': 'ai', 'text': formatted_response})

    # Only show the last 10 messages
    limited_chat_history = session['chat_history'][-10:]

    # Render the page with chat history
    return render_template_string(html_template, chat_history=limited_chat_history)

if __name__ == "__main__":
    app.run(debug=True)

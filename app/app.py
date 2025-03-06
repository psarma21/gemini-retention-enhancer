from flask import Flask, request, render_template, jsonify
from wrapper.main import get_gemini_response, get_related_news, get_image_description_and_image
import re
from flask_socketio import SocketIO
import sqlite3
import html

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # required for session management
socketio = SocketIO(app, async_mode='eventlet')

# init_and_clear_db clears existing data and create sqlite db on startup
def init_and_clear_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_type TEXT,
            message_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """) # create table if it doesn't exist
    
    cursor.execute("DELETE FROM chat_history") # delete any data from the table
    conn.commit()
    conn.close()
    
# save_message_to_db saves a message in the database
def save_message_to_db(message_type, message_text):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (message_type, message_text) VALUES (?, ?)",
                   (message_type, message_text))
    conn.commit()
    conn.close()

def format_gemini_response(text):
    # Process mermaid code blocks
    mermaid_match = re.search(r'```mermaid\s*(.*?)```', text, flags=re.DOTALL)
    
    if mermaid_match:
        mermaid_code = mermaid_match.group(1).strip()
        print("Extracted Mermaid Code:", mermaid_code)  # Debugging
        
        # Split the text into parts: before, mermaid, and after
        before_mermaid = text[:mermaid_match.start()]
        after_mermaid = text[mermaid_match.end():]
        
        # Format the parts separately and then recombine
        before_formatted = before_mermaid.replace("\n", "<br>")
        mermaid_formatted = f'<div class="mermaid">{mermaid_code}</div>'
        after_formatted = after_mermaid.replace("\n", "<br>")
        
        # Recombine the text
        text = before_formatted + mermaid_formatted + after_formatted
    else:
        # If no mermaid diagram, just replace all newlines
        text = text.replace("\n", "<br>")

    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" target="_blank">\1</a>', text) # Convert Markdown links to HTML <a> tags
    text = re.sub(r'```(.*?)```', r'<pre class="code-block"><code>\1</code></pre>', text, flags=re.DOTALL) # Format generic code blocks
    text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)  # Handle inline code (text within single backticks)
    text = re.sub(r'`([^`]+)`', lambda m: f'<code class="inline-code">{html.escape(m.group(1))}</code>', text) # Handle inline code (text within single backticks)
    text = re.sub(r'<br>\s*<br>+', '<br><br>', text) # Remove extra blank lines (convert multiple <br> to just one)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b class="bold-text clickable-word">\1</b>', text)     # Bold formatting
    text = re.sub(r'\*(.*?)\*', r'<i class="italic-text">\1</i>', text) # Italic formatting
    text = re.sub(r'^\* (.*)', r'<li>\1</li>', text, flags=re.MULTILINE) # Ensure bullet points are converted properly 
    return text

# format_gemini_response_text formats Gemini response from Gemini's news output
def format_gemini_response_text(text):
    text = re.sub(r'```(.*?)```', r'<pre class="code-block"><code>\1</code></pre>', text, flags=re.S)
    text = re.sub(r'\n\s*\n+', '\n\n', text)  
    text = re.sub(r'\*\*(.*?)\*\*', r'<b class="bold-text">\1</b>', text)  
    text = re.sub(r'\*(.*?)\*', r'<i class="italic-text">\1</i>', text)    
    text = re.sub(r'^\* ', r'<span class="bullet">•</span> ', text, flags=re.M)
    text = text.replace("\n", "<br>")  
    return text

# get_chat_history retrieve chat history from the database
def get_chat_history(limit):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT message_type, message_text FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"type": row[0], "text": row[1]} for row in rows][::-1]  # reverse to maintain order

# image API
@app.route("/generate-image-description", methods=["POST"])
def generate_image():
    data = request.get_json()
    word = data.get("word")

    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT message_type, message_text FROM chat_history ORDER BY id DESC LIMIT 2")
    messages = cursor.fetchall()
    conn.close()
        
    last_user_prompt = messages[1][1]
    last_gemini_response = messages[0][1]

    url, caption = get_image_description_and_image(
        last_gemini_response=last_gemini_response,
        last_user_query=last_user_prompt,
        key_word=word
    )
    return jsonify({"image_url": url, "caption": caption})

# news API
@app.route("/test_emit")
def test_emit():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT message_type, message_text FROM chat_history ORDER BY id DESC LIMIT 2")
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) >= 2:
        last_gemini_response = rows[0][1]  
        last_user_query = rows[1][1]  
        news = get_related_news(last_gemini_response, last_user_query)
        formatted_news = format_gemini_response_text(news)
        save_message_to_db('ai', formatted_news)
        socketio.emit('additional_response', {'text': formatted_news})
        return "Emit sent!"
    else:
        return "Not enough chat history to generate a response", 400

# main response from Gemini
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        topic = request.form.get("topic")
        custom_topic = request.form.get("custom_topic_input")

        selected_topic = custom_topic if topic == "other" else topic

        chat_history = get_chat_history(limit=4)
        last_user_prompt = chat_history[-2]['text'] if len(chat_history) >= 2 else None
        last_gemini_response = chat_history[-1]['text'] if len(chat_history) >= 1 else None
        second_to_last_user_prompt = chat_history[-4]['text'] if len(chat_history) >= 4 else None
        ai_response = get_gemini_response(user_input, selected_topic, last_user_prompt, last_gemini_response, second_to_last_user_prompt)
        formatted_response = format_gemini_response(ai_response)

        save_message_to_db('user', user_input)
        save_message_to_db('ai', formatted_response)

    chat_history = get_chat_history(limit=10)
    return render_template("app.html", chat_history=chat_history)

if __name__ == "__main__":
    init_and_clear_db()
    socketio.run(app, debug=True)
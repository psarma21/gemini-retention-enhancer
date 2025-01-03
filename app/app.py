from flask import Flask, request, render_template, session
from wrapper.main import get_gemini_response, get_related_news
import re
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
socketio = SocketIO(app, async_mode='eventlet')

def format_gemini_response(text):
    text = re.sub(r'```(.*?)```', r'<pre class="code-block"><code>\1</code></pre>', text, flags=re.S)
    text = re.sub(r'\n\s*\n+', '\n\n', text)  # Remove extra blank lines
    text = re.sub(r'\*\*(.*?)\*\*', r'<b class="bold-text">\1</b>', text)  # Bold formatting
    text = re.sub(r'\*(.*?)\*', r'<i class="italic-text">\1</i>', text)    # Italic formatting
    text = re.sub(r'^\* ', r'<span class="bullet">•</span> ', text, flags=re.M)
    text = text.replace("\n", "<br>")  # Line breaks outside code blocks
    return text

@app.route("/test_emit")
def test_emit():
    if session.get('chat_history') and len(session['chat_history']) >= 2:
        last_gemini_response = session['chat_history'][-1]['text']
        last_user_query = session['chat_history'][-2]['text']
        news = get_related_news(last_gemini_response, last_user_query)
        formatted_news = format_gemini_response(news)
        session['chat_history'].append({'type': 'ai', 'text': formatted_news})
    socketio.emit('additional_response', {'text': formatted_news})
    return "Emit sent!"

@app.route("/", methods=["GET", "POST"])
def index():
    if 'chat_history' not in session:
        session['chat_history'] = [] # Start with an empty chat history

    if request.method == "POST":
        user_input = request.form.get("user_input")
        topic = request.form.get("topic")
        custom_topic = request.form.get("custom_topic_input")  # Adjusted to match HTML name attribute
                
        last_user_prompt, last_gemini_response, second_to_last_user_prompt = None, None, None
        if session.get('chat_history') and len(session['chat_history']) >= 2:
            last_user_prompt = session['chat_history'][-2]['text']
            last_gemini_response = session['chat_history'][-1]['text']
            if len(session['chat_history']) >= 4:
                second_to_last_user_prompt = session['chat_history'][-4]['text']
            
        selected_topic = custom_topic if topic == "other" else topic

        ai_response = get_gemini_response(user_input, selected_topic, last_user_prompt, last_gemini_response, second_to_last_user_prompt)
        formatted_response = format_gemini_response(ai_response)

        session['chat_history'].append({'type': 'user', 'text': user_input})
        session['chat_history'].append({'type': 'ai', 'text': formatted_response})
        session.modified = True

    limited_chat_history = session['chat_history'][-10:]
    return render_template("app.html", chat_history=limited_chat_history)

if __name__ == "__main__":
    socketio.run(app, debug=True)
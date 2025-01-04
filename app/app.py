from flask import Flask, request, render_template, session, jsonify
from wrapper.main import get_gemini_response, get_related_news, get_image_description_and_image
import re
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
socketio = SocketIO(app, async_mode='eventlet')

@app.route("/generate-image-description", methods=["POST"])
def generate_image():
    data = request.get_json()
    word = data.get("word")
    if not word:
        return jsonify({"error": "No word provided"}), 400
    
    last_user_prompt = session['chat_history'][-2]['text']
    last_gemini_response = session['chat_history'][-1]['text']
    
    url = get_image_description_and_image(last_gemini_response=last_gemini_response, last_user_query=last_user_prompt, key_word=word)
    return jsonify({"image_url": url})


def format_gemini_response(text):
    def convert_table(match):
        table_text = match.group(0)
        rows = [row.strip() for row in table_text.split('\n') if row.strip()]
        
        if len(rows) < 2 or not all('|' in row for row in rows[:2]):
            return table_text
            
        if not rows[1].replace('|', '').replace('-', '').replace(':', '').strip() == '':
            return table_text
            
        header = [cell.strip() for cell in rows[0].strip('|').split('|') if cell.strip()]
        
        data_rows = []
        for row in rows[2:]:  # Skip header and separator
            cells = [cell.strip() for cell in row.strip('|').split('|') if cell.strip()]
            if cells:
                data_rows.append(cells)
        
        html_parts = []
        html_parts.append('<div class="table-wrapper"><table class="gemini-table">')
        html_parts.append('<thead><tr>')
        for cell in header:
            html_parts.append(f'<th>{cell}</th>')
        html_parts.append('</tr></thead>')
        html_parts.append('<tbody>')
        
        for row in data_rows:
            html_parts.append('<tr>')
            while len(row) < len(header):
                row.append('')
            for cell in row[:len(header)]:
                html_parts.append(f'<td>{cell}</td>')
            html_parts.append('</tr>')
        
        html_parts.append('</tbody></table></div>')
        return ''.join(html_parts)  # Join without newlines

    parts = []
    last_end = 0
    
    pattern = r'(?:\n|\A)\|[^\n]+\|\n\|[-:|]+\|\n(?:\|[^\n]+\|\n?)+(?=\n[^|]|\Z)'
    
    for match in re.finditer(pattern, text, re.MULTILINE):
        start = match.start()
        if start > 0 and text[start-1] == '\n':
            start -= 1
        parts.append(text[last_end:start])
        parts.append(convert_table(match))
        last_end = match.end()
    
    parts.append(text[last_end:])
    
    text = ''.join(parts)
    
    # Apply other formatting
    text = re.sub(r'```(.*?)```', r'<pre class="code-block"><code>\1</code></pre>', text, flags=re.S)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b class="bold-text clickable-word">\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i class="italic-text">\1</i>', text)
    text = re.sub(r'^\* ', r'<span class="bullet">•</span> ', text, flags=re.M)
    text = text.replace("\n", "<br>")
    
    return text

def format_gemini_response_text(text):
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
        formatted_news = format_gemini_response_text(news)
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
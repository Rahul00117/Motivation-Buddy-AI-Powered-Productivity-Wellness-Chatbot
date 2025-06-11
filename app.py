import requests
from bs4 import BeautifulSoup
import gradio as gr
import random
import google.generativeai as genai

GEMINI_API_KEY = "Hide"
genai.configure(api_key=GEMINI_API_KEY)

# --- Motivational Quote Scraper ---
def get_motivation():
    try:
        url = "https://www.brainyquote.com/quote_of_the_day"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        quote = soup.select_one('.qotd-q-cntr .qotd-q-container .qotd-q-text')
        author = soup.select_one('.qotd-q-cntr .qotd-q-container .qotd-q-author')
        if quote and author:
            return f"🌟 \"{quote.text.strip()}\" — {author.text.strip()}"
        else:
            return "🌟 Stay positive and keep moving forward!"
    except Exception:
        return "🌟 Stay positive and keep moving forward!"

# --- Affirmation Generator ---
def get_affirmation(mood):
    affirmations = {
        "Happy": ["You are unstoppable!", "Keep shining!", "Your energy is contagious!"],
        "Sad": ["You are stronger than you think.", "Every day is a new beginning.", "You matter!"],
        "Stressed": ["Breathe. You’ve got this.", "One step at a time.", "Progress, not perfection."],
        "Motivated": ["Let’s crush those goals!", "You’re on fire!", "Keep up the momentum!"],
        "Neutral": ["Today is a blank page. Make it awesome!", "Small steps lead to big results.", "Believe in yourself!"]
    }
    return random.choice(affirmations.get(mood, affirmations["Neutral"]))

# --- Productivity Badge Generator ---
def get_badge():
    badges = [
        "🏅 Focus Champ", "🚀 Starter Star", "🎯 Task Master", "🌟 Productivity Pro", "🔥 Momentum Maker"
    ]
    return random.choice(badges)

# --- Prompt Builder ---
def build_prompt(user_question, quote, affirmation, badge, user_name, mood):
    prompt = (
        f"Today's motivational quote: {quote}\n"
        f"Affirmation for you: {affirmation}\n"
        f"Productivity Badge: {badge}\n"
    )
    if user_name:
        prompt += f"User Name (for streaks): {user_name}\n"
    prompt += (
        f"User's mood: {mood}\n"
        f"User's question: {user_question}\n"
        "Your answer (friendly, practical, and positive):"
    )
    return prompt

# --- Chatbot Logic ---
def chat(user_message, history, mood, user_name):
    quote = get_motivation()
    affirmation = get_affirmation(mood)
    badge = get_badge()
    prompt = build_prompt(user_message, quote, affirmation, badge, user_name, mood)
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat_session = model.start_chat(history=[])
    try:
        response = chat_session.send_message(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error from Gemini API: {e}"
    history = history or []
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": answer})
    return history, "", "", ""

# --- Gradio UI ---
with gr.Blocks(title="Unique Productivity & Motivation Buddy") as demo:
    gr.Markdown("""
    <div style="text-align:center">
        <h1>🚀 Unique Productivity & Motivation Buddy</h1>
        <p style="font-size:1.2em;">
            <b>Mood-based motivation, Badges, Affirmations, Streaks & more!</b><br>
            <span style="color:#888;">Hindi/English both supported.</span>
        </p>
    </div>
    """)
    chatbot = gr.Chatbot(type="messages", label="Motivation Buddy")
    mood = gr.Radio(
        ["Happy", "Sad", "Stressed", "Motivated", "Neutral"],
        label="How are you feeling today?",
        value="Neutral"
    )
    user_name = gr.Textbox(
        label="Your Name (for streaks)",
        placeholder="Enter your name to track your motivation streaks!",
        elem_id="user-name-box"
    )
    msg = gr.Textbox(
        label="Type your question or ask for motivation...",
        placeholder="e.g. Give me a productivity tip, Motivate me, How to avoid procrastination?"
    )
    send = gr.Button("Send")
    clear = gr.Button("Clear")

    def respond(message, history, mood, user_name):
        return chat(message, history, mood, user_name)

    msg.submit(respond, [msg, chatbot, mood, user_name], [chatbot, msg, user_name, mood])
    send.click(respond, [msg, chatbot, mood, user_name], [chatbot, msg, user_name, mood])
    clear.click(lambda: ([], "", "", ""), None, [chatbot, msg, user_name, mood])

    gr.Markdown("""
    ---
    <ul>
        <li>Try: <i>"Give me a productivity tip", "Help me plan my day", "Motivate me", "How to avoid procrastination?"</i></li>
        <li>Every answer is unique to your mood and name streak!</li>
        <li>🏅 <b>Badges:</b> Get a fun badge with every interaction!</li>
        <li>⏲️ <b>Pomodoro Timer:</b> <a href="https://pomofocus.io/" target="_blank">Start a 25-min focus session</a></li>
    </ul>
    <div style="text-align:center;color:#888;">
        <b>Tip:</b> Enter your name above to track your motivation streaks!
    </div>
    """)

if __name__ == "__main__":
    demo.launch(share=True, inbrowser=True, debug=False)

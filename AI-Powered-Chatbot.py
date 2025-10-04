# app.py (Main Flask application)
from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from datetime import datetime
import nltk
from nltk.chat.util import Chat, reflections

# Download required NLTK data
nltk.download('punkt')

app = Flask(__name__)

# Define chatbot patterns and responses
pairs = [
    [
        r"my name is (.*)",
        ["Hello %1, how can I help you today?",]
    ],
    [
        r"what is your name?",
        ["I'm a chatbot created to assist you. You can call me ChatBot!",]
    ],
    [
        r"how are you?",
        ["I'm doing well, thank you! How can I assist you?", "I'm great! What can I help you with today?"]
    ],
    [
        r"(.*) (help|support)",
        ["I'd be happy to help! What do you need assistance with?",]
    ],
    [
        r"(.*) (price|cost)",
        ["Please contact our sales team at sales@company.com for pricing information.",]
    ],
    [
        r"(.*) (hours|time|open)",
        ["We're open Monday to Friday, 9 AM to 6 PM.",]
    ],
    [
        r"(.*) (contact|email|phone)",
        ["You can reach us at contact@company.com or call +1-555-0123.",]
    ],
    [
        r"(.*) (product|service)",
        ["We offer various products and services. Could you be more specific about what you're looking for?",]
    ],
    [
        r"quit",
        ["Thank you for chatting! Have a great day!",]
    ],
    [
        r"(.*)",
        ["I'm sorry, I didn't understand that. Could you please rephrase?", "That's interesting! Could you tell me more?"]
    ]
]

chatbot = Chat(pairs, reflections)

def init_db():
    conn = sqlite3.connect('chat_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_input TEXT,
                  bot_response TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def log_chat(user_input, bot_response):
    conn = sqlite3.connect('chat_logs.db')
    c = conn.cursor()
    c.execute("INSERT INTO chat_logs (user_input, bot_response, timestamp) VALUES (?, ?, ?)",
              (user_input, bot_response, datetime.now()))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    bot_response = chatbot.respond(user_input)
    
    if not bot_response:
        bot_response = "I'm still learning. Could you try asking something else?"
    
    log_chat(user_input, bot_response)
    
    return jsonify({'response': bot_response})

@app.route('/logs')
def show_logs():
    conn = sqlite3.connect('chat_logs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM chat_logs ORDER BY timestamp DESC LIMIT 50")
    logs = c.fetchall()
    conn.close()
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

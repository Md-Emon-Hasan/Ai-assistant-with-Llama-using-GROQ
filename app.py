'''
   Author  : Emon Hasan
   Email   : iconicemon01@gmail.com
   GitHub  : https://github.com/Md-Emon-Hasan
   LinkedIn: https://www.linkedin.com/in/emon-hasan/
   Date    : 01/14/2025
   Time    : 21:08
   Project : building ai chatbot using llama
   Purpose : bulding a simple chatbot using llama model and groq
'''

import os
from typing import List, Dict
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from groq import Groq
from flask_cors import CORS

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("API key for Groq is missing. Please set the GROQ_API_KEY in the .env file.")

app = Flask(__name__)
CORS(app)

client = Groq(api_key=GROQ_API_KEY)

conversations: Dict[str, List[Dict[str, str]]] = {}

def query_groq_api(conversation: List[Dict[str, str]]) -> str:
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70B-specdec",
            messages=conversation,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        
        return response
    
    except Exception as e:
        return f"Error with Groq API: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat/', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    role = data.get('role', 'user')
    conversation_id = data.get('conversation_id')

    if not conversation_id:
        return jsonify({"error": "conversation_id is required"}), 400

    if conversation_id not in conversations:
        conversations[conversation_id] = [{"role": "system", "content": "You are a useful AI assistant."}]

    conversation = conversations[conversation_id]

    conversation.append({"role": role, "content": message})

    response = query_groq_api(conversation)

    conversation.append({"role": "assistant", "content": response})

    return jsonify({"response": response, "conversation_id": conversation_id})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

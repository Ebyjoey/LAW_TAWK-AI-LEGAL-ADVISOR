from flask import Flask, request, jsonify
import torch
import ollama
import os
from check import checklegal, generalconvo

app = Flask(__name__)

# Load your vault and embeddings here
vault_content = open("vault.txt", "r", encoding='utf-8').readlines() if os.path.exists("vault.txt") else []
vault_embeddings = torch.tensor([ollama.embeddings(model='mxbai-embed-large', prompt=content)["embedding"] for content in vault_content])

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    history = data.get('history', [])

    # Determine if the message is legal-related or general conversation
    flag = checklegal(user_message)
    
    if "YES" in flag:
        response = ollama_chat(user_message, history)
    else:
        response = generalconvo(user_message)

    return jsonify({"response": response})

def ollama_chat(user_input, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    
    # Call the function that fetches relevant content based on input
    rewritten_query = user_input if len(conversation_history) == 1 else user_input
    
    # Get the relevant context
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        rewritten_query += "\n\nRelevant Context:\n" + "\n".join(relevant_context)

    conversation_history[-1]["content"] = rewritten_query
    response = ollama_model_chat(conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    return response

def ollama_model_chat(conversation_history):
    # Use your existing method to get a response from Ollama
    response = ollama.chat(conversation_history)
    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Make Flask listen on all interfaces

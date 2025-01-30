import torch
import ollama
import os
import json
import argparse
from openai import OpenAI
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from check import checklegal,generalconvo

# ANSI escape codes for colors
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'


# Get relevant context from the vault
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if not vault_embeddings.nelement():
        return []
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    top_indices = torch.topk(cos_scores, k=min(top_k, len(cos_scores)))[1].tolist()
    return [vault_content[idx].strip() for idx in top_indices]

# Rewrite user query based on conversation history
def rewrite_query(user_input, conversation_history, ollama_model):
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-2:]])
    prompt = f"""As a legal advisor, please rewrite the following query by incorporating relevant details from the conversation history. Your revised query should:

- Ensure clarity and completeness: Confirm that all necessary details are included, and ask for any additional information if required to provide a more accurate response.
- Stay aligned with the original intent: Maintain the core purpose and meaning of the original query, while expanding it to make it more specific and relevant.
- Avoid introducing new topics: Ensure that the query remains focused on the original issue without deviating to unrelated matters.
- Be clear and polite: Phrase your revised query in a professional, courteous, and easily understandable manner.
- Use bullet points if necessary: When helpful, use concise bullet points to highlight key points or clarify complex matters.

Please do not answer the original query. Focus solely on rephrasing and expanding it into a new query for further clarity.

Return only the rewritten query text—no extra formatting or explanations.

Conversation History:
{context}

Original query:
[{user_input}]

Rewritten query:
"""
    
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()

# Main chat function
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    rewritten_query = rewrite_query(user_input, conversation_history, ollama_model) if len(conversation_history) > 1 else user_input
    
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        rewritten_query += "\n\nRelevant Context:\n" + "\n".join(relevant_context)
    
    conversation_history[-1]["content"] = rewritten_query
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": system_message}, *conversation_history],
        max_tokens=2000,
    )
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content



# Command-line arguments
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="mistral", help="Ollama model to use (default: mistral)")
args = parser.parse_args()

# Initialize client and load vault
client = OpenAI(base_url='http://localhost:11434/v1', api_key='mistral')
vault_content = open("vault.txt", "r", encoding='utf-8').readlines() if os.path.exists("vault.txt") else []
vault_embeddings = torch.tensor([ollama.embeddings(model='mxbai-embed-large', prompt=content)["embedding"] for content in vault_content])

# Chat loop
conversation_history = []
system_message = "You are a helpful assistant, providing relevant context and expertise."

while True:
    user_input = input(YELLOW + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
    '''user_input = input("Ask a query about your documents (or type 'quit' to exit): ")'''
    if user_input.lower() == 'quit':
        break
    flag=checklegal(user_input)
    if "YES" in flag:
        response = ollama_chat(user_input, system_message, vault_embeddings, vault_content, args.model, conversation_history)
    elif "NOT" in flag:
        response=generalconvo(user_input)
        
    print(NEON_GREEN + f"User: {user_input}" + RESET_COLOR)
    print(NEON_GREEN + f"Assistant: {response}" + RESET_COLOR)
    conversation_history=[]
    '''print(f"User: {user_input}")
    print(f"Assistant: {response}")'''
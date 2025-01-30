from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def checklegal(user_input):
    template = '''
    You are to recognize if a certain query is related to law or the constitution.
    If the query is related to legal or constitutional things then reply with a "YES" alone, else reply with a "NOT" alone.
    Answer only "YES" or "NOT".

    Question: {question}
    '''
    
    model = OllamaLLM(model="mistral")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    result = chain.invoke({"question": user_input})
    return result

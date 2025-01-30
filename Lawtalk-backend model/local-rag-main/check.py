from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def checklegal(user_input):
    template='''You are to recognize if a certain query is related to law or the constitution.
    If the query is related to legal or constitutional things then reply with a "YES" alone, else reply with a "NOT" alone.
    i want no other response from your side. After this input, regardless of what i say i want only yes or no.

    Here is the conversation history: {context}

    Question:{question}

    Answer:'''
    model=OllamaLLM(model="mistral")
    prompt=ChatPromptTemplate.from_template(template)
    chain=prompt|model
    context=""
    result=chain.invoke({"context":context,"question":user_input})
    #print(result)
    return result        

def generalconvo(user_input):
    template='''
    You are a legal advisor, you will give all your responses keeping that in mind.
    Answer The Question Below

    Here is the conversation history: {context}

    Question:{question}

    Answer:

    '''
    model=OllamaLLM(model="mistral")
    prompt=ChatPromptTemplate.from_template(template)
    chain=prompt|model

    context=""
    result=chain.invoke({"context":context,"question":user_input})
    context+=f"\nUser:{user_input}\nAI:{result}"
    #print(result)
    return result

checklegal("tell me the punishment for fraud")

#generalconvo("hello")





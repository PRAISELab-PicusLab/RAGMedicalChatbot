import streamlit as st
from openai import OpenAI


# Configura il client Nvidia NIM usando OpenAI
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets.nvidia.api_key  # Imposta la tua API Key
)

# Imposta il modello da utilizzare su Nvidia NIM (es: llama3-8b-instruct)
model = "meta/llama3-8b-instruct"


def query_expansion(prompt):
    global model
    SYS_PROMPT = 'Sei un assistente medico esperto. Il tuo task è espandere la domanda del paziente che riceverai in ingresso. Espandi la domanda originale in modo che contenga un numero maggiore di dettagli rilevanti per la diagnosi ' \
                 'lasciando inalterato il significato e il contenuto. Sii ridondante usando sinonimi. Usa parole semplici. Rispondi esclusivamente con la nuova domanda che hai elaborato.\n' \
                 'Esempio:\n\n Utente: ho 25 anni e sto perdendo i capelli \nAssistente: ho 25 anni e sto perdendo i capelli, ' \
                 'sono giovane ma ho riscontrato una caduta di capelli, un diradamento del cuoio capelluto.'

    messages = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": prompt}
    ]

    # Effettua la richiesta al modello utilizzando l'API Nvidia
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        top_p=0.9,
        max_tokens=512
    )

    # Restituisce la risposta del modello
    return completion.choices[0].message.content


def query_sum_document(prompt):
    global model
    SYS_PROMPT = 'Sei un assistente medico esperto. Il tuo task è riassumere diverse domande e risposte avvenute rispettivamente tra pazienti e dottori provenienti da forum medici.\n' \
                 'Non aggiungere informazioni non presenti nelle domande e nelle risposte, ma limitati a riassumere le conversazioni in maniera più breve, sottolineandone gli aspetti più rilevanti.\n' \
                 'Rispondi in italiano ed esclusivamente nel seguente formato:\n\n' \
                 'DOCUMENTO:\n' \
                 'Domanda: (domanda)\n' \
                 'Risposta: (risposta)\n'

    messages = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": prompt}
    ]

    # Effettua la richiesta al modello utilizzando l'API Nvidia
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        top_p=0.9,
        max_tokens=512
    )

    # Restituisce la risposta del modello
    return completion.choices[0].message.content


def query_stream(messages):
    global model
    # Effettua la richiesta al modello utilizzando l'API Nvidia con lo streaming
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        top_p=0.9,
        max_tokens=512,
        stream=True  # Streaming abilitato
    )

    # Itera sui chunk di risposta in streaming e restituisce i contenuti
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

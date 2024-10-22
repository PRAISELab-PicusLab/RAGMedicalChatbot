import streamlit as st
from llm_functions import query_stream
from chroma_functions import process_query
from pprint import pprint


if 'layout' not in st.session_state:
    st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
    st.session_state['layout'] = True

else:
    if not st.session_state['layout']:
        st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
        st.session_state['layout'] = True


SYS_PROMPT = 'Sei un chatbot medico italiano. Il tuo compito è assistere il paziente, comprendendo i suoi dubbi, fornendo una diagnosi e possibili trattamenti sulla base dei suoi sintomi. ' \
             'Se il paziente cita pochi sintomi non forzare la diagnosi. Non citare nella tua diagnosi altri dottori. Ignora i documenti non pertinenti.'


conversations = ['chat_messages']

def collect_generator(generator):
    global final_string
    output = []
    for chunk in generator:
        output.append(chunk)
        yield chunk
    final_string = ''.join(output)

def on_btn_click():
    for conversation in conversations:
        del st.session_state[conversation]

def switch_off_mode():
    if st.session_state['humanitas_toggle']:
        st.session_state['mode_toggle'] = False

# CSS
st.markdown(
    """
    <style>
    .stButton > button {
        position: fixed;
        bottom: 10px;
        right: 80px;
        z-index: 9999;
    }
    .st-key-mode_toggle {
        position: fixed;
        bottom: 15px;
        margin-right: 180px;
        z-index: 9999;
    }
    .st-key-humanitas_toggle {
        position: fixed;
        bottom: 15px;
        margin-left: 180px;
        z-index: 9999;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# header
st.title("💬 Medical Chatbot")
st.caption("Descrivi i tuoi sintomi")


# conversazioni separate: messages da mostrare (senza documenti), rag_messages per llm
if conversations[0] not in st.session_state:
    st.session_state[conversations[0]] = [{'role': 'system', 'content': SYS_PROMPT},
                                      {"role": "assistant", "content": "Come posso aiutarti?"}
                                     ]


# inizio rendering pagina
for msg in st.session_state[conversations[0]][1:]:
        st.chat_message(msg["role"]).write(msg["content"])


# toggle modalità
default_mode = False
mode = st.toggle(label='Modalità precisa', value=default_mode,
                help='Questa modalità rallenta i tempi di risposta e va scelta prima di iniziare la conversazione.',
                key='mode_toggle')

humanitas_mode = st.toggle(label='Usa Humanitas', value=default_mode,
                help='Questa modalità usa le fonti dell\'enciclopedia medica Humanitas e va scelta prima di iniziare la conversazione.',
                key='humanitas_toggle', on_change=switch_off_mode)


# bottone per pulire la chat
button = st.button("Cancella chat", on_click=on_btn_click, key='restart', type="primary")

# evento prompt ricevuto
if prompt := st.chat_input(placeholder="Scrivi qui il tuo messaggio..."):
    urls = []
    current_query = [{'role': 'system', 'content': SYS_PROMPT},
                      {"role": "assistant", "content": "Come posso aiutarti?"}
                     ]

    # prompt da mostrare nella chat (senza testo dei documenti)
    st.session_state[conversations[0]].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # placeholder per la risposta del modello
    response_placeholder = st.chat_message("assistant")

    # selezione della modalità di generazione
    if humanitas_mode:
        rag_prompt, urls = process_query(prompt, 'humanitas') # no expansion, rerank and summarization
    else:
        rag_prompt, urls = process_query(prompt, 'RAG', expansion=True, rerank=True, summarize=mode) # RAG
        # rag_prompt, urls = prompt, [] # NO RAG

    # prompt con i documenti per il modello
    current_query.append({"role": "user", "content": rag_prompt})

    final_string = ''
    with response_placeholder:
        print('DEBUG: Inizio generazione')
        generator = query_stream(current_query)
        wrapped = collect_generator(generator)
        response_placeholder.write_stream(wrapped)

    # riferimenti agli URL dei retrieved documents
    riferimenti = 'Riferimenti: \n\n'
    for url in urls:
        riferimenti += url + '\n\n'
    if urls:
        st.chat_message("assistant").write(riferimenti)

    # salvataggio della risposta del modello e dei riferimenti usati
    st.session_state[conversations[0]].append({"role": "assistant", "content": final_string})
    if urls:
        st.session_state[conversations[0]].append({"role": "assistant", "content": riferimenti})

    print('\n')
    pprint(current_query)
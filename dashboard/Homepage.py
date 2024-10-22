import streamlit as st


if 'layout' not in st.session_state:
    st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
    st.session_state['layout'] = True
else:
    if not st.session_state['layout']:
        st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
        st.session_state['layout'] = True


st.title('💊 Medical App')

st.subheader('Benvenuti!')
st.write('Nell\'apposita pagina "Q&A Chatbot" è possibile testare il chatbot medico, disponibile in due modalità di generazione.')
st.write('I dati utilizzati per il RAG provengono dai siti web ' \
         '[dica33.it](https://www.dica33.it/esperto-risponde/) e [medicitalia.it](https://www.medicitalia.it/consulti/) ed è possibile esplorarli attraverso le dashboard presenti nelle pagine "Analytics" e "Doctors".')
st.write('Inoltre nella pagina "Q&A Chatbot" è possibile testare un ulteriore chatbot medico che utilizza una base di conoscenza medica di tipo enciclopedico proveniente da [humanitas.it](https://www.humanitas.it/enciclopedia/)')
st.write('\n')
import pandas as pd
import streamlit as st
import plotly.express as px

from mongodb_functions import *


if 'layout' not in st.session_state:
    st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
    st.session_state['layout'] = True
else:
    if not st.session_state['layout']:
        st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
        st.session_state['layout'] = True


st.title('Dashboard')
st.subheader("📈 Insights relative ai dati ottenuti dallo scraping dei Medical Forums")

sources = ['Tutte', 'Dica33', 'Medicitalia']


col1, _, _, col4 = st.columns(4)

with col1:
    st.write('📊 Numero di post per sorgente')
    df = {"Sorgente": [], "Numero di domande": []}
    for site in sources:
        df["Sorgente"].append(site)
        df["Numero di domande"].append(get_size_of_collection(site))
    st.dataframe(df,
                column_order=("Sorgente", "Numero di domande"),
                hide_index=True,
                width=None,
                column_config={
                "Sorgente": st.column_config.TextColumn(
                    "Sorgente",
                ),
                "Numero di domande": st.column_config.ProgressColumn(
                    "Numero di post",
                    min_value=0,
                    format="%f",
                    max_value=max(df['Numero di domande'])
                    )}
                )


_, _, _, col4 = st.columns(4)

with col4:
    source1 = st.selectbox('Seleziona una sorgente', sources, key="donut")

data = get_num_documents_by_category(source1)

fig = px.pie(data, names='Categories', values='Counts', hole=0.5,
             width=700,
             height=700,
             title='📊 Numero di post per categoria',
             labels={
                 'Categories': 'Categoria',
                 'Counts': '# domande'
             })
st.plotly_chart(fig, use_container_width=True)


_, _, _, col4 = st.columns(4)
with col4:
    source2 = st.selectbox('Seleziona una sorgente', sources, key="barplot")

data = get_avg_response_time(source2)

fig = px.bar(data, x='Categories', y='responseTimes', title='📊 Tempi di risposta medi in ore per categoria', height=700,
             labels={
                 'Categories': 'Categoria',
                 'responseTimes': 'Tempo di risposta medio (ore)'
             })
st.plotly_chart(fig)


col1, _, _, col4 = st.columns(4)

with col4:
    source3 = st.selectbox('Seleziona una sorgente', sources, key="barplot2")

category_list = get_distinct_categories()


with col1:
    category = st.selectbox('Seleziona una categoria', category_list)

data = pd.DataFrame(get_category_questions_trend(category, source3))
data['date'] = data.apply(lambda x: str(x['month'])+'-'+str(x['year']), axis=1)
data['date'] = data['date'].apply(lambda x: pd.to_datetime(x, format='%m-%Y'))

fig = px.bar(data, x='date', y='count', title=f'📊 Popolarità della categoria {category} nel tempo', height=700,
             labels={
                 'date': 'Periodo',
                 'count': 'Numero di post'
             })

st.plotly_chart(fig)
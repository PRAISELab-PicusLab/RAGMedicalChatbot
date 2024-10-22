import io
import base64
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from mongodb_functions import *
from streamlit_star_rating import st_star_rating


def decode_image(image64):
    try:
        image_data = base64.b64decode(image64)
        image = io.BytesIO(image_data)
        return image
    except:
        return './dashboard/assets/esperto_medico.png'
    
    
if 'layout' not in st.session_state:
    st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
    st.session_state['layout'] = True
else:
    if not st.session_state['layout']:
        st.set_page_config(page_title='MedicalChat', page_icon='💊', layout='wide')
        st.session_state['layout'] = True


st.title('Dashboard')
st.subheader("👨‍⚕️ Insights relative ai medici")


# rendering pagina
col1, categoria = st.columns([4,9])

c1, c2 = st.columns([4,9])
with c1:
    st.write('📊 Numero di medici per specializzazione')


data = get_doctors_count()

col1, col2 = st.columns([4,9])
with col1:
    st.dataframe(data,
                column_order=("Specialization", "Count"),
                hide_index=True,
                width=None,
                height=500,
                column_config={
                "Specialization": st.column_config.TextColumn(
                    "Specializzazione",
                ),
                "Count": st.column_config.ProgressColumn(
                    "# Medici",
                    min_value=0,
                    format="%f",
                    max_value=max(data['Count'])
                    )}
                )


specializations = get_distinct_specializations()
with categoria:
    st.write('🏅 Top 10 medici consigliati dagli utenti')
    spec = st.selectbox('Seleziona o cerca la categoria', specializations)
    data = get_doctors_ranked(spec)

    df = pd.DataFrame(columns=['picture', 'name', 'location', 'ranking', 'n_likes'])
    df = df._append(data, ignore_index=True)
    
    locations = ['Tutte'] + df['location'].dropna().unique().tolist()
    location = st.selectbox('Seleziona o cerca la posizione', locations)
    

table_column_sizes = [1,1,1,1,1]

with c2:
    if(location != 'Tutte'):
        df = df[df['location'] == location]
    header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns(table_column_sizes)
    with header_col1:
        st.write('Foto')
    with header_col2:
        st.write('Nome')
    with header_col3:
        st.write('Sede')
    with header_col4:
        st.write('Valutazione')
    with header_col5:
        st.write('Numero di recensioni')

with col2:
    container = st.container(height=500)
    with container:
        for _, dottore in df.head(10).iterrows():
            col1, col2, col3, col4, col5 = st.columns(table_column_sizes)
            
            with col1:
                try:
                    if(pd.isnull(dottore['picture'])):
                        st.image(decode_image(None), width=100)
                    else:
                        st.image(decode_image(dottore['picture']), width=100)
                except:
                    st.image(decode_image(None), width=100)

            with col2:
                try:
                    if(pd.isnull(dottore['name'])):
                        st.write('Non disponibile')
                    else:
                        st.write(f"[{dottore['name']}]({dottore['_id']})")
                except:
                    st.write('Non disponibile')

            with col3:
                try:
                    if(pd.isnull(dottore['location'])):
                        st.write('Non disponibile')
                    else:
                        st.write(dottore['location'])
                except:
                    st.write('Non disponibile')
                    
            with col4:
                try:
                    if(pd.isnull(dottore['ranking'])):
                        st.write('Non disponibile')
                    else:
                        st_star_rating("", maxValue=5, defaultValue=dottore['ranking'], read_only = True, customCSS = "div { width:300px; transform: scale(0.7); transform-origin: 0% 0% 0px;}")
                        #st.write(dottore['ranking'])
                except:
                    st.write('Non disponibile')
            
            with col5:
                try:
                    if(pd.isnull(dottore['n_likes'])):
                        st.write('Non disponibile')
                    else:
                        st.write(int(dottore['n_likes']))
                except:
                    st.write('Non disponibile')
            
            st.markdown("---")


st.divider()
# get tutte le location con numero di dottori per location
num_docts_on_location = get_distinct_locations()
df_locations = pd.DataFrame(columns=['location', 'Count'])
df_locations = df_locations._append(num_docts_on_location)

specializations2 = ['Tutte'] + specializations

st.write('🌍 Distribuzione geografica dei medici')
spec2 = st.selectbox('Seleziona o cerca la specializzazione', specializations2)

# get tutti i dottori
doctors = get_doctors_coordinates(spec2)
df = pd.DataFrame(columns=['coordinates', 'location'])
df = df._append(doctors)

locations_merged = pd.DataFrame(columns=['location', 'latitude', 'longitude', 'Count'])
if(doctors):
    df['latitude'] = df['coordinates'].apply(lambda x: x[0] if x[0] != 0.0 else None)
    df['longitude'] = df['coordinates'].apply(lambda x: x[1] if x[1] != 0.0 else None)
    df = df.dropna(how='any', subset=['latitude', 'longitude'])

    locations_merged = locations_merged._append(df_locations.merge(df, how='inner', left_on='location', right_on='location'))
    locations_merged = locations_merged[['location', 'latitude', 'longitude', 'Count']]

st.map(locations_merged,
    latitude='latitude',
    longitude='longitude',
    size='Count')
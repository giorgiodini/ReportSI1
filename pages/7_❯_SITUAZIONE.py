import os
import pandas as pd
import streamlit as st



# ----------------------------------------------------------
# Configurazione Pandas

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# ----------------------------------------------------------
# Configurazione Streamlit

st.set_page_config(page_title="Pacchi provvisori")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

with open(r'pages/style.css') as f:
    st.markdown(f'<style>{f.read()}</style', unsafe_allow_html=True)

# ----------------------------------------------------------
# Loading di tutti i dataset dalla cartella

directory = r'Data/Situazione'

elenco_file = [
    f for f in os.listdir(directory) if f.endswith('xlsx')
]

df = pd.DataFrame()

for file in elenco_file:
    percorso_file = os.path.join(directory,file)
    dfTemp = pd.read_excel(percorso_file)

    # Salvataggio del nome del file
    file_name = os.path.basename(file)
    date_file = os.path.splitext(file_name)[0]  # Export data dal nome del file
    date_file = date_file[11:21]  # Salvataggio dei primi 10 caratteri del nome file

    # Aggiungo la colonna data
    dfTemp['DATA'] = date_file
    dfTemp["DATA"] = pd.to_datetime(dfTemp["DATA"], dayfirst=True)
    dfTemp["DATA"] = dfTemp["DATA"].dt.strftime('%d-%m-%Y')
    dfTemp['DATA'] = pd.to_datetime(dfTemp['DATA'], format='%d-%m-%Y').dt.strftime('%d/%m/%Y')

    df = pd.concat([df, dfTemp], ignore_index=True)

    df["DATA"] = pd.to_datetime(df["DATA"], format='%d/%m/%Y')
    df["Day"] = df["DATA"].dt.day
    df["Month"] = df["DATA"].dt.month


# ----------------------------------------------------------
# Markdown titolo

st.header("SITUAZIONE", divider='orange')

# Ordinamento per ultima data
df = df.sort_values(by=['Month', 'Day'], ascending=False)

df_date = df["DATA"]
aggiornamento = df_date.max()
st.markdown(f'''
:gray[Ultimo aggiornamento: {aggiornamento}]''')

'''
---

'''

# ----------------------------------------------------------
# Situazione generale

st.markdown(f":orange[Andamento mancate consegne/mancate letture di guardaroba]")

'''
Tramite lo scatterplot è possibile visualizzare la situazione all'ultimo aggiornamento del rapporto tra
mancate consegne e mancate letture per i Guardaroba. I Guardaroba più performanti si posizionano nel primo quadrante in basso a sinistra. 
(Minori "Mancate Consegne" e "Mancate Letture"). Al contrario, i Guardaroba 
meno performanti si posizionano a distanza della distribuzione degli altri Guardaroba e dal primo quadrante.
'''
'''

'''

df_vega = df.loc[df["DATA"]==df["DATA"].max()]
df_vega = df_vega.groupby(by=["DESCRIZIONE GUARDAROBA"], as_index=False)[["MANCATE CONSEGNE", "MANCATE LETTURE DI GUARDAROBA"]].sum()

st.vega_lite_chart(df_vega, {
    'mark': {'type': 'circle', 'tooltip':True},
    'encoding': {
        'x': {'field': 'MANCATE CONSEGNE', 'type': 'quantitative'},
        'y': {'field': 'MANCATE LETTURE DI GUARDAROBA', 'type': 'quantitative'},
        'color': {'field': 'DESCRIZIONE GUARDAROBA', 'type': 'nominal', },
    }
}, use_container_width=True, legends=False)


# ----------------------------------------------------------
# Dettaglio guardaroba

'''
---
'''

st.markdown("### Dettaglio guardaroba")

elenco_guardaroba = df["DESCRIZIONE GUARDAROBA"].unique()
option = st.selectbox("Seleziona il guardaroba",elenco_guardaroba)

df_guardaroba = df.loc[df["DESCRIZIONE GUARDAROBA"]==option]
df_guardaroba2 = df_guardaroba.groupby(by=["DATA"], as_index=False)[["MANCATE CONSEGNE", "MANCATE LETTURE DI GUARDAROBA"]].sum()

df_calc = df_guardaroba.groupby(by=["DATA"], as_index=False)[["SPEDITO DA LAVANDERIA", "CARICATO IN GUARDAROBA"]].sum()
df_calc["DIFFERENZA"] = df_calc["SPEDITO DA LAVANDERIA"]-df_calc["CARICATO IN GUARDAROBA"]

ultimi_dati_guardaroba = df_guardaroba2.loc[df_guardaroba2["DATA"]==df_guardaroba2["DATA"].max()]
ultime_consegne = ultimi_dati_guardaroba["MANCATE CONSEGNE"].sum()
ultime_letture = ultimi_dati_guardaroba["MANCATE LETTURE DI GUARDAROBA"].sum()

ultimi_dati_calc = df_calc.loc[df_calc["DATA"]==df_calc["DATA"].max()]
ultima_diff = ultimi_dati_calc["DIFFERENZA"].sum()

col1, col2, col3 = st.columns(3)

df_delta = df_guardaroba2.sort_values(by="DATA", ascending=False)

delta_consegne = round(((ultime_consegne-df_delta["MANCATE CONSEGNE"].iloc[1])/df_delta["MANCATE CONSEGNE"].iloc[1])*100,2)
delta_letture = round(((ultime_letture-df_delta["MANCATE LETTURE DI GUARDAROBA"].iloc[1])/df_delta["MANCATE LETTURE DI GUARDAROBA"].iloc[1])*100,2)

df_calc_delta = df_calc.sort_values(by="DATA", ascending=False)

delta_diff = ultima_diff-df_calc_delta["DIFFERENZA"].iloc[1]

col1.metric(label=":orange[Mancate consegne settimanali]", value=ultime_consegne, delta=f"{delta_consegne} %", delta_color="inverse")
col2.metric(label=":orange[Mancate letture settimanali]", value=ultime_letture, delta=f"{delta_letture} %", delta_color="inverse")
col3.metric(label=":orange[Diff Spedito/Caricato Guardaroba]", value=ultima_diff,delta=f"{delta_diff}")

st.line_chart(df_guardaroba2, x="DATA", y=["MANCATE CONSEGNE", "MANCATE LETTURE DI GUARDAROBA"])

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
import pandas as pd
import os
import numpy as np
import streamlit as st
from PIL import Image
from vega_datasets import data



# ----------------------------------------------------------
# Configurazione Pandas

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# ----------------------------------------------------------
# Configurazione Streamlit

st.set_page_config(page_title="Uscite Stabilimento")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#with open(r'pages/style.css') as f:
#    st.markdown(f'<style>{f.read()}</style', unsafe_allow_html=True)

# ----------------------------------------------------------
# Loading di tutti i dataset dalla cartella

directory = r'Data/UsciteStabilimento'
#directory = r'C:\\Users\\vincenzo.citignola\\Documents\\GitHub\\reportSI\\Data\\UsciteStabilimento'

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
    date_file = date_file[:10]  # Salvataggio dei primi 10 caratteri del nome file

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
# Nome report

st.header("USCITE STABILIMENTO ", divider='orange')

# ----------------------------------------------------------
# Markdown ultimo aggiornamento


# Ordinamento per ultima data
df = df.sort_values(by=['Month', 'Day'], ascending=False)

df_date = df["DATA"]
aggiornamento = df_date.max()
st.markdown(f'''
:gray[Ultimo aggiornamento: {aggiornamento}]''')

'''
---

'''

# Uscite da tutti gli stabilimenti

st.markdown('### :orange[Andamento Generale]')
'''
Andamento temporale delle uscite di pacchi/pezzi per tutti gli stabilimenti. 
Le metriche "Numero pacchi/pezzi settimana corrente" presentano la variazione percentuale
rispetto alla settimana precedente.
'''
'''

'''

df_tuttiStabilimenti = df.groupby(by=["DATA"],as_index=False)[['NUMERO PACCHI', 'NUMERO PEZZI']].sum()
df_tuttiStabilimenti = df_tuttiStabilimenti.sort_values(by="DATA", ascending=False)

delta_pacchi = round((df_tuttiStabilimenti["NUMERO PACCHI"].iloc[0]-df_tuttiStabilimenti["NUMERO PACCHI"].iloc[1])/df_tuttiStabilimenti["NUMERO PACCHI"].iloc[1],2)
delta_pezzi = round((df_tuttiStabilimenti["NUMERO PEZZI"].iloc[0]-df_tuttiStabilimenti["NUMERO PEZZI"].iloc[1])/df_tuttiStabilimenti["NUMERO PEZZI"].iloc[1],2)

col1, col2 = st.columns(2)

col1.metric(label=":orange[Numero pacchi settimana corrente]", value=df_tuttiStabilimenti["NUMERO PACCHI"].iloc[0], delta=f'{delta_pacchi} %')
col2.metric(label=":orange[Numero pezzi settimana corrente]", value=df_tuttiStabilimenti["NUMERO PEZZI"].iloc[0], delta=f'{delta_pezzi} %')


st.line_chart(df_tuttiStabilimenti,x="DATA", y=["NUMERO PACCHI", "NUMERO PEZZI"])

'''
---
'''
st.markdown("### :orange[Elenco Stabilimenti]")
'''
Elenco in ordine decrescente del numero di pacchi/pezzi in uscita per ogni Stabilimento
'''

# Elenco Stabilimenti

df_elencoStabilimentiLast = df.loc[df["DATA"]==df["DATA"].max()]
df_elencoStabilimentiLast = df_elencoStabilimentiLast.groupby(by=["DESCRIZIONE STABILIMENTO"], as_index=False)[["NUMERO PACCHI", "NUMERO PEZZI"]].sum()
df_elencoStabilimentiLast = df_elencoStabilimentiLast.sort_values(by="NUMERO PACCHI", ascending=False)


st.dataframe(df_elencoStabilimentiLast, hide_index=True)

'''
---
'''

# ----------------------------------------------------------
# Dettaglio per stabilimento
st.markdown("### :orange[Dettaglio per Stabilimento]")
elenco_stabilimenti = df["DESCRIZIONE STABILIMENTO"].unique()
option = st.selectbox("Seleziona lo stabilimento",elenco_stabilimenti)

df_filter = df.loc[df["DESCRIZIONE STABILIMENTO"]==option]
df_filter2 = df_filter.groupby(by=["DATA"], as_index=False)[["NUMERO PACCHI", "NUMERO PEZZI"]].sum()

col3, col4 = st.columns(2)

col3.metric(label=":orange[Media Pacchi in uscita]", value=int(df_filter2["NUMERO PACCHI"].mean()))
col4.metric(label=":orange[Media Pezzi in uscita]", value=int(df_filter2["NUMERO PEZZI"].mean()))

st.line_chart(df_filter2, x="DATA", y=["NUMERO PACCHI", "NUMERO PEZZI"])

df_filter3 = df_filter.loc[df_filter["DATA"]==df_filter["DATA"].max()]
df_filter3 = df_filter3.groupby(by=["DATA","DESCRIZIONE GUARDAROBA"], as_index=False)[["NUMERO PACCHI", "NUMERO PEZZI"]].sum()
df_filter3 = df_filter3.sort_values(by="NUMERO PACCHI", ascending=False)

'''
Elenco dei Guardaroba di riferimento
'''

st.dataframe(df_filter3, hide_index=True, column_config={"DATA":None})

# ----------------------------------------------------------
# Ulteriore dettaglio per guardaroba
st.markdown("### :orange[Dettaglio Articoli per Guardaroba]")
df_filter_guardaroba = df_filter.loc[df_filter["DATA"]==df_filter["DATA"].max()]
elenco_guardaroba = df_filter_guardaroba["DESCRIZIONE GUARDAROBA"].unique()
option = st.selectbox("Seleziona il guardaroba",elenco_guardaroba)

df_filterOption = df_filter.loc[df_filter["DESCRIZIONE GUARDAROBA"] == option]
df_articoliGuardaroba = df_filterOption.loc[df_filterOption["DATA"]==df_filterOption["DATA"].max()]
df_articoliGuardaroba = df_articoliGuardaroba.groupby(by=["DATA","CODICE ARTICOLO", "DESCRIZIONE ARTICOLO"], as_index=False)[["NUMERO PACCHI", "NUMERO PEZZI"]].sum()


'''
Elenco articoli in uscita nell'ultima settimana
'''

st.dataframe(df_articoliGuardaroba.sort_values(by="NUMERO PACCHI", ascending=False), hide_index=True, column_config={"DATA": None})


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
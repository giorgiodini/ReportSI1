import os
import pandas as pd
import streamlit as st
import warnings

warnings.simplefilter("ignore")



# ----------------------------------------------------------
# Configurazione Pandas

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# ----------------------------------------------------------
# Configurazione Streamlit

st.set_page_config(page_title="Sovra Scorta")

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

directory = r'Data/VariazioniSovraScorta'
#directory = r'C:\\Users\\vincenzo.citignola\\Documents\\GitHub\\reportSI\\Data\\VariazioniSovraScorta'

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

st.header("SOVRA SCORTA", divider='orange')

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

# Line chart che indica il numero totale di articoli in sovrascorta (stock > 7)

df = df[df["STOCK IN GUARDAROBA"]>7]
df_count_articoli_sovrascorta = df.groupby(by="DATA", as_index=False)["STOCK IN GUARDAROBA"].mean()

'''
Andamento medio di articoli in sovrascorta per ogni giorno. 
Il sovrascorta sono tutti gli STOCK > 7
'''

st.line_chart(df_count_articoli_sovrascorta, x="DATA", y="STOCK IN GUARDAROBA")



####################
st.markdown("### :orange[Situazione Generale negli ultimi 7 giorni]")
'''
Situazione attuale dei guardaroba.
In tale sezione è possibile verificare il rapporto tra "Spedito da Lavanderia" e "Caricato in Guardaroba" negli ultimi 7 giorni
'''


# Spedito da Lavanderia e Caricato in guardaroba

df1 = df[df["STOCK IN GUARDAROBA"]>7]
df_vega = df1.loc[df1["DATA"]==df1["DATA"].max()]
df_vega = df_vega.groupby(by=["DESCRIZIONE GUARDAROBA"], as_index=False)[["SPEDITO DA LAVANDERIA ULTIMI 7 GIORNI", "CARICATO IN GUARDAROBA ULTIMI 7 GIORNI"]].sum()

st.vega_lite_chart(df_vega, {
    'mark': {'type': 'circle', 'tooltip':True},
    'encoding': {
        'x': {'field': 'SPEDITO DA LAVANDERIA ULTIMI 7 GIORNI', 'type': 'quantitative'},
        'y': {'field': 'CARICATO IN GUARDAROBA ULTIMI 7 GIORNI', 'type': 'quantitative'},
        'color': {'field': 'DESCRIZIONE GUARDAROBA', 'type': 'nominal', },
    }
}, use_container_width=True, legends=False)


# ----------------------------------------------------------------------
# TABELLA SOVRASCORTA
# ----------------------------------------------------------------------


df_sovrascorta = df1.loc[df1["DATA"]==df1["DATA"].max()]


df_sovrascorta2 = df_sovrascorta.groupby(by="DESCRIZIONE GUARDAROBA", as_index=False)["STOCK IN GUARDAROBA"].count() # Numero di articoli in sovrascorta

'''
In questa sezione è il riportato il numero di articoli in Sovrascorta per ogni Guardaroba alla data di ultimo aggiornamento.
Si intende sovrascorta quando lo stock (tenuto conto del consegnato medio e della giacenza presente) è maggiore di 7
'''

#df_sovrascorta2 = df_sovrascorta2.loc[df_sovrascorta2["STOCK IN GUARDAROBA"]>7]
df_sovrascorta2 = df_sovrascorta2.sort_values(by="STOCK IN GUARDAROBA", ascending=False)
st.dataframe(df_sovrascorta2, hide_index=True, column_order=("DESCRIZIONE GUARDAROBA", "STOCK IN GUARDAROBA"),
                                                            column_config={"CARICATO IN GUARDAROBA ULTIMI 7 GIORNI": None,
                                                                           "SPEDITO DA LAVANDERIA ULTIMI 7 GIORNI": None,
                                                                           "STOCK IN GUARDAROBA": st.column_config.TextColumn("ARTICOLI IN SOVRASC")
                                                                           })

'''
---
'''
st.markdown('### :orange[Sovrascorta medio per Guardaroba]')

'''
Numero medio di articoli in Sovrascorta per ogni Guardaroba.
La media è data dal numero totale di articoli in sovrascorta per ogni giorno di rilevazione.
'''

df3 = df[df["STOCK IN GUARDAROBA"]>7]
df_medio = df3.groupby(by=["DATA","DESCRIZIONE GUARDAROBA"], as_index=False)[["STOCK IN GUARDAROBA"]].count()
df_medio2 = df_medio.groupby(by="DESCRIZIONE GUARDAROBA", as_index=False)[["STOCK IN GUARDAROBA"]].mean()
df_medio2 = df_medio2[df_medio2["STOCK IN GUARDAROBA"]>7]
df_medio2["STOCK IN GUARDAROBA"] = df_medio2["STOCK IN GUARDAROBA"].astype(int)
df_medio2 = df_medio2.sort_values(by="STOCK IN GUARDAROBA", ascending=False)
#df_medio2["SOVRASCORTA"] = df_medio2["STOCK IN GUARDAROBA"]-7
#df_medio2["SOVRASCORTA"] = df_medio2["SOVRASCORTA"].astype(int)
#df_medio2 = df_medio2.loc[df_medio2["SOVRASCORTA"]>0]
#df_medio2 = df_medio2.sort_values(by="SOVRASCORTA", ascending=True)

st.dataframe(df_medio2, hide_index=True,column_config={"STOCK IN GUARDAROBA": st.column_config.TextColumn("NUM. ARTICOLI IN SOVRASCORTA IN MEDIA"),"CARICATO IN GUARDAROBA ULTIMI 7 GIORNI": None,
                                       "SPEDITO DA LAVANDERIA ULTIMI 7 GIORNI": None})

'''
---
'''
# ----------------------------------------------------------
# Dettaglio per guardaroba
st.markdown("### :orange[Dettaglio per Guardaroba]")
elenco_guardaroba = df["DESCRIZIONE GUARDAROBA"].unique()
option = st.selectbox("Seleziona il guardaroba",elenco_guardaroba)

df_guardaroba = df1.loc[df1["DESCRIZIONE GUARDAROBA"]==option]

df_guardaroba2 = df_guardaroba.groupby(by="DATA", as_index=False)[["STOCK IN GUARDAROBA"]].count()

df_sovrascorta_today= df_guardaroba2.loc[df_guardaroba2["DATA"]==df_guardaroba2["DATA"].max()]


col1, col2 = st.columns(2)
col1.metric(label=":orange[Sovrascorta odierno]", value=int(df_sovrascorta_today["STOCK IN GUARDAROBA"]))
col2.metric(label=":orange[Sovrascorta Medio]", value=int(df_guardaroba2["STOCK IN GUARDAROBA"].mean()))

st.line_chart(df_guardaroba2, x="DATA", y="STOCK IN GUARDAROBA")

'''
---
'''


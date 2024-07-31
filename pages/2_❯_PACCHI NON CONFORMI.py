import os
import pandas as pd
import streamlit as st
import plost


# ----------------------------------------------------------
# Configurazione Pandas

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# ----------------------------------------------------------
# Configurazione Streamlit

st.set_page_config(page_title="Pacchi non conformi")

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

directory = r'Data/PacchiNonConformi'

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
    df = df.loc[df["NON CONFORMITA'"]!="Destinatario Sconosciuto"]

    df["DATA"] = pd.to_datetime(df["DATA"], format='%d/%m/%Y')
    df["Day"] = df["DATA"].dt.day
    df["Month"] = df["DATA"].dt.month


# ----------------------------------------------------------
# Markdown titolo

st.header("PACCHI NON CONFORMI", divider='orange')

df_date = df["DATA"]
aggiornamento = df_date.max()
st.markdown(f'''
:gray[Ultimo aggiornamento: {aggiornamento}]''')

'''
---

'''

# ----------------------------------------------------------
# Pacchi non conformi generale

st.markdown("### :orange[Andamento generale]")
'''
Andamento temporale dei pacchi che presentano una "non conformità".
La metrica "Settimana Corrente" presenta la variazione
percentuale rispetto alla settimana precedente
'''
'''

'''
col1,col2,col3 = st.columns(3)

nconf_totale = df.loc[df["DATA"]==df["DATA"].max()]
totale_nconf = nconf_totale["NUMERO PACCHI"].sum()

delta_df = df.groupby(by=["DATA"], as_index=False)["NUMERO PACCHI"].sum()
delta_df = delta_df.sort_values(by="DATA", ascending=False)
delta = round(((totale_nconf-delta_df["NUMERO PACCHI"].iloc[1])/delta_df["NUMERO PACCHI"].iloc[1])*100,2)
settimana_precedente = delta_df["NUMERO PACCHI"].iloc[1]


col1.metric(label=":orange[Pacchi Settimana precedente]", value='{:,}'.format(settimana_precedente).replace(',', '.'))
col2.metric(label=":orange[Pacchi Settimana corrente]", value='{:,}'.format(totale_nconf).replace(',', '.'), delta=f"{delta} %", delta_color="inverse")
col3.metric(label="", value="")

'''
---

'''
''' :orange[Andamento settimanale] '''

st.line_chart(delta_df, x="DATA", y="NUMERO PACCHI")




'''
---

'''

# ----------------------------------------------------------
# Pacchi non standard - statistica generale

st.markdown("### :orange[Non conformità - suddivisione per stabilimento]")
'''
Suddivisione in termini percentuali del numero di non conformità presenti in tutti gli stabilimenti
'''

col4,col5 = st.columns(2)

nconf_group = nconf_totale.groupby(by=["NON CONFORMITA'"], as_index=False)["NUMERO PACCHI"].sum()
nconf_group["%"] = round((nconf_group["NUMERO PACCHI"]/totale_nconf)*100,2)
nconf_group = nconf_group.sort_values(by="%", ascending=False)
nconf_group["NON CONFORMITA"] = nconf_group["NON CONFORMITA'"]

nconf_group2 = nconf_totale.groupby(by=["DESCRIZIONE STABILIMENTO"], as_index=False)["NUMERO PACCHI"].sum()
nconf_group2["%"] = round((nconf_group2["NUMERO PACCHI"]/totale_nconf)*100,2)
nconf_group2 = nconf_group2.sort_values(by="%", ascending=False)

with col4:
    plost.donut_chart(nconf_group, theta="%", color="NON CONFORMITA", legend=None, title="Non conformità")

col5.dataframe(nconf_group2, hide_index=True, column_config={"NUMERO PACCHI": None}, width=None, use_container_width=False, column_order=("%","DESCRIZIONE STABILIMENTO"))

# ----------------------------------------------------------
# Pacchi non conformi per sito produttivo

'''
---
'''

st.markdown("### :orange[Dettaglio per Stabilimento]")

elenco_nonconf_dett = df.groupby(["DESCRIZIONE STABILIMENTO","NON CONFORMITA'"], as_index=False)["NUMERO PACCHI"].sum()
option = st.selectbox("Seleziona lo stabilimento",nconf_group2["DESCRIZIONE STABILIMENTO"])

col6, col7 = st.columns(2)

elenco_nonconf_dett2 = elenco_nonconf_dett.loc[elenco_nonconf_dett["DESCRIZIONE STABILIMENTO"]==option]
elenco_nonconf_dett2 = elenco_nonconf_dett2.groupby(by=["NON CONFORMITA'"], as_index=False)["NUMERO PACCHI"].sum()
elenco_nonconf_dett2 = elenco_nonconf_dett2.sort_values(by="NUMERO PACCHI", ascending=False)
col6.dataframe(elenco_nonconf_dett2, hide_index=True, column_order=("NUMERO PACCHI", "NON CONFORMITA'"),
               column_config={"DESCRIZIONE STABILIMENTO":None, "NUMERO PACCHI": st.column_config.TextColumn("PACCHI")}
               )

# Filtro per Donuts
df_don_stabilimento = df.loc[df["DATA"]==df["DATA"].max()]
df_don_stabilimento = df_don_stabilimento.loc[df_don_stabilimento["DESCRIZIONE STABILIMENTO"]==option]
df_don_stabilimento = df_don_stabilimento.sort_values(by="NUMERO PACCHI", ascending=False)
totale_don_stabilimento = df_don_stabilimento["NUMERO PACCHI"].sum()
df_don_stabilimento["%"] = round((df_don_stabilimento["NUMERO PACCHI"]/totale_don_stabilimento)*100,2)
df_don_stabilimento["NON CONFORMITA"] = df_don_stabilimento["NON CONFORMITA'"]


with col7:
    plost.donut_chart(df_don_stabilimento, theta="%", color="NON CONFORMITA", legend=None, title="Non conformità")



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
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

directory = r'Data/PacchiProvvisori'

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
# Markdown titolo

st.header("PACCHI PROVVISORI", divider='orange')

df_date = df["DATA"]
aggiornamento = df_date.max()
st.markdown(f'''
:gray[Ultimo aggiornamento: {aggiornamento}]''')

'''
---

'''
# ----------------------------------------------------------
# Situazione generale

st.markdown("### :orange[Andamento generale]")
'''
Andamento temporale del numero di Capi/Pacchi creati dalla lavanderia da 5-15 giorni e oltre 15 giorni.
'''
'''
La variazione percentuale è espressa in riferimento alla settimana precedente di rilevazione.
'''
'''

'''

df = df.sort_values(by=["Month", "Day"])

df_filter_ultima_data = df.loc[df["DATA"]==df["DATA"].max()]

n_pacchi_515 = df_filter_ultima_data["NUMERO PACCHI DA 5 A 15 GIORNI"].sum()
n_pacchi_over = df_filter_ultima_data["NUMERO PACCHI OLTRE 15 GIORNI"].sum()
n_capi_515 = df_filter_ultima_data["NUMERO CAPI DA 5 A 15 GIORNI"].sum()
n_capi_over = df_filter_ultima_data["NUMERO CAPI OLTRE 15 GIORNI"].sum()


delta_df = df.groupby(by=["DATA"], as_index=False)[["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI", "NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"]].sum()
delta_df = delta_df.sort_values(by="DATA", ascending=False)

delta_pacchi515 = round(((n_pacchi_515-delta_df["NUMERO PACCHI DA 5 A 15 GIORNI"].iloc[1])/delta_df["NUMERO PACCHI DA 5 A 15 GIORNI"].iloc[1])*100,2)
delta_pacchi_over = round(((n_pacchi_over-delta_df["NUMERO PACCHI OLTRE 15 GIORNI"].iloc[1])/delta_df["NUMERO PACCHI OLTRE 15 GIORNI"].iloc[1])*100,2)
delta_capi515 = round(((n_capi_515-delta_df["NUMERO CAPI DA 5 A 15 GIORNI"].iloc[1])/delta_df["NUMERO CAPI DA 5 A 15 GIORNI"].iloc[1])*100,2)
delta_capi_over = round(((n_capi_over-delta_df["NUMERO CAPI OLTRE 15 GIORNI"].iloc[1])/delta_df["NUMERO CAPI OLTRE 15 GIORNI"].iloc[1])*100,2)

col1, col2, col3, col4 = st.columns(4)

col1.metric(label=":orange[Pacchi da 5 a 15 giorni]", value=n_pacchi_515, delta=f"{delta_pacchi515} %", delta_color="inverse")
col2.metric(label=":orange[Pacchi oltre 15 giorni]", value=n_pacchi_over, delta=f"{delta_pacchi_over} %", delta_color="inverse")
col3.metric(label=":orange[Capi da 5 a 15 giorni]", value=n_capi_515, delta=f"{delta_capi515} %", delta_color="inverse")
col4.metric(label=":orange[Capi oltre 15 giorni]", value=n_capi_over, delta=f"{delta_capi_over} %", delta_color="inverse")

# ----------------------------------------------------------
# Andamento Pacchi/Capi


df_pack = df.groupby(by="DATA", as_index=False)[["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"]].sum()
st.line_chart(df_pack, x="DATA", y=["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"])

# ----------------------------------------------------------
# Scatterplot situazione generale - ultima data
st.markdown(':orange[Rapporto numero Pacchi/Capi provvisori]')
'''
Tramite lo scatterplot è possibile visualizzare la situazione all'ultimo aggiornamento del rapporto tra
numero pacchi da 5-15 e oltre 15 giorni e il numero capi da 5-15 e oltre 15 giorni.
L'x-score è dato dal numero di pacchi, mentre l'y-score è dato dal numero di capi.
Gli stabilimenti più performanti si posizionano nel primo quadrante in basso a sinistra. Al contrario, gli Stabilimenti 
meno performanti si posizionano a distanza della distribuzione degli altri Stabilimenti
'''

df_vega = df.loc[df["DATA"]==df["DATA"].max()]
df_vega_x = df_vega.groupby(by="DESCRIZIONE LAVANDERIA", as_index=False)[["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI"]].sum()
df_vega_y = df_vega.groupby(by="DESCRIZIONE LAVANDERIA", as_index=False)[["NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"]].sum()

# Standardizzazione tra 0 e 1 dei valori
df_vega_x["value_x"] = df_vega_x["NUMERO PACCHI DA 5 A 15 GIORNI"]+(2*df_vega_x["NUMERO PACCHI OLTRE 15 GIORNI"])
df_vega_x["zscore_x"] = (df_vega_x["value_x"]-df_vega_x["value_x"].min())/(df_vega_x["value_x"].max()-df_vega_x["value_x"].min())

df_vega_y["value_y"] = df_vega_y["NUMERO CAPI DA 5 A 15 GIORNI"]+(2*df_vega_y["NUMERO CAPI OLTRE 15 GIORNI"])
df_vega_y["zscore_y"] = (df_vega_y["value_y"]-df_vega_y["value_y"].min())/(df_vega_y["value_y"].max()-df_vega_y["value_y"].min())
df_vega_x["zscore_y"] = df_vega_y["zscore_y"]


st.vega_lite_chart(df_vega_x, {
    'mark': {'type': 'circle', 'tooltip':True},
    'encoding': {
        'x': {'field': 'zscore_x', 'type': 'quantitative'},
        'y': {'field': 'zscore_y', 'type': 'quantitative'},
        'color': {'field': 'DESCRIZIONE LAVANDERIA', 'type': 'nominal', },
    }
}, use_container_width=True)

# ----------------------------------------------------------
# Situazione lavanderie

'''
---

'''

st.markdown("### :orange[Elenco Stabilimenti]")

st.markdown("Numero pacchi da 5 a 15 giorni / Numero pacchi oltre 15 giorni")

col1,col2 = st.columns(2)

# ----------------------------------------------------------
# Situazione lavanderie - pacchi


# Pacchi da 5 a 15 giorni
ultima_data = df["DATA"].max()
provvisori_last = df.loc[df["DATA"]==ultima_data]
pacchi_last = provvisori_last.groupby(by=["DESCRIZIONE LAVANDERIA"], as_index=False)["NUMERO PACCHI DA 5 A 15 GIORNI"].sum()
pacchi_last = pacchi_last.loc[pacchi_last["NUMERO PACCHI DA 5 A 15 GIORNI"]>0]

# Pacchi oltre 15 giorni
pacchi_last2 = provvisori_last.groupby(by="DESCRIZIONE LAVANDERIA", as_index=False)["NUMERO PACCHI OLTRE 15 GIORNI"].sum()
pacchi_last2 = pacchi_last2.loc[pacchi_last2["NUMERO PACCHI OLTRE 15 GIORNI"]>0]

col1.dataframe(pacchi_last.sort_values(by="NUMERO PACCHI DA 5 A 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO PACCHI DA 5 A 15 GIORNI','DESCRIZIONE LAVANDERIA'),
               column_config={"NUMERO PACCHI DA 5 A 15 GIORNI": st.column_config.TextColumn("PACCHI")})
col2.dataframe(pacchi_last2.sort_values(by="NUMERO PACCHI OLTRE 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO PACCHI OLTRE 15 GIORNI','DESCRIZIONE LAVANDERIA'),
               column_config={"NUMERO PACCHI OLTRE 15 GIORNI": st.column_config.TextColumn("PACCHI")})

# ----------------------------------------------------------
# Situazione lavanderia - pacchi


st.markdown("Numero capi da 5 a 15 giorni / Numero capi oltre 15 giorni")

col3,col4 = st.columns(2)

# Capi da 5 a 15 giorni
capi_last = provvisori_last.groupby(by=["DESCRIZIONE LAVANDERIA"], as_index=False)["NUMERO CAPI DA 5 A 15 GIORNI"].sum()
capi_last = capi_last.loc[capi_last["NUMERO CAPI DA 5 A 15 GIORNI"]>0]

# Capi oltre 15 giorni
capi_last2 = provvisori_last.groupby(by="DESCRIZIONE LAVANDERIA", as_index=False)["NUMERO CAPI OLTRE 15 GIORNI"].sum()
capi_last2 = capi_last2.loc[capi_last2["NUMERO CAPI OLTRE 15 GIORNI"]>0]

col3.dataframe(capi_last.sort_values(by="NUMERO CAPI DA 5 A 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO CAPI DA 5 A 15 GIORNI','DESCRIZIONE LAVANDERIA'),
               column_config={"NUMERO CAPI DA 5 A 15 GIORNI": st.column_config.TextColumn("CAPI")})
col4.dataframe(capi_last2.sort_values(by="NUMERO CAPI OLTRE 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO CAPI OLTRE 15 GIORNI','DESCRIZIONE LAVANDERIA'),
               column_config={"NUMERO CAPI OLTRE 15 GIORNI": st.column_config.TextColumn("CAPI")})

# ----------------------------------------------------------
# Situazione clienti

'''
---

'''

st.markdown("### :orange[Elenco Destinatari]")

# ----------------------------------------------------------
# Situazione clienti - pacchi

st.markdown("Numero pacchi da 5 a 15 giorni / Numero pacchi oltre 15 giorni")

col5, col6 =st.columns(2)

# Pacchi da 5 a 15 giorni

pacchi_last_cliente = provvisori_last.groupby(by=["DESCRIZIONE DESTINATARIO"], as_index=False)["NUMERO PACCHI DA 5 A 15 GIORNI"].sum()
pacchi_last_cliente = pacchi_last_cliente.loc[pacchi_last_cliente["NUMERO PACCHI DA 5 A 15 GIORNI"]>0]

# Pacchi oltre 15 giorni
pacchi_last2_cliente = provvisori_last.groupby(by="DESCRIZIONE DESTINATARIO", as_index=False)["NUMERO PACCHI OLTRE 15 GIORNI"].sum()
pacchi_last2_cliente = pacchi_last2_cliente.loc[pacchi_last2_cliente["NUMERO PACCHI OLTRE 15 GIORNI"]>0]

col5.dataframe(pacchi_last_cliente.sort_values(by="NUMERO PACCHI DA 5 A 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO PACCHI DA 5 A 15 GIORNI','DESCRIZIONE DESTINATARIO'),
               column_config={"NUMERO PACCHI DA 5 A 15 GIORNI": st.column_config.TextColumn("PACCHI")})
col6.dataframe(pacchi_last2_cliente.sort_values(by="NUMERO PACCHI OLTRE 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO PACCHI OLTRE 15 GIORNI','DESCRIZIONE DESTINATARIO'),
               column_config={"NUMERO PACCHI OLTRE 15 GIORNI": st.column_config.TextColumn("PACCHI")})


# ----------------------------------------------------------
# Situazione clienti - capi

st.markdown("Numero capi da 5 a 15 giorni / Numero capi oltre 15 giorni")

col7, col8 =st.columns(2)

# Pacchi da 5 a 15 giorni

capi_last_cliente = provvisori_last.groupby(by=["DESCRIZIONE DESTINATARIO"], as_index=False)["NUMERO CAPI DA 5 A 15 GIORNI"].sum()
capi_last_cliente = capi_last_cliente.loc[capi_last_cliente["NUMERO CAPI DA 5 A 15 GIORNI"]>0]

# Pacchi oltre 15 giorni
capi_last2_cliente = provvisori_last.groupby(by="DESCRIZIONE DESTINATARIO", as_index=False)["NUMERO CAPI OLTRE 15 GIORNI"].sum()
capi_last2_cliente = capi_last2_cliente.loc[capi_last2_cliente["NUMERO CAPI OLTRE 15 GIORNI"]>0]

col7.dataframe(capi_last_cliente.sort_values(by="NUMERO CAPI DA 5 A 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO CAPI DA 5 A 15 GIORNI','DESCRIZIONE DESTINATARIO'),
               column_config={"NUMERO CAPI DA 5 A 15 GIORNI": st.column_config.TextColumn("CAPI")})
col8.dataframe(capi_last2_cliente.sort_values(by="NUMERO CAPI OLTRE 15 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO CAPI OLTRE 15 GIORNI','DESCRIZIONE DESTINATARIO'),
               column_config={"NUMERO CAPI OLTRE 15 GIORNI": st.column_config.TextColumn("CAPI")})

# ----------------------------------------------------------
# Dettaglio lavanderie

'''
---

'''

st.markdown("### :orange[Dettaglio per Stabilimento]")

option = st.selectbox("Seleziona lo stabilimento",df["DESCRIZIONE LAVANDERIA"].unique())

df2 = df.loc[df["DESCRIZIONE LAVANDERIA"]==option]
df3 = df2.groupby(by="DATA", as_index=False)[["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"]].sum()
st.line_chart(df3, x="DATA", y=["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"])


'''
Elenco degli articoli prodotti 
'''
# Dettaglio capi

df_articoli = df2.loc[df2["DATA"]==df2["DATA"].max()]
df_articoli = df_articoli.groupby(by=["DESCRIZIONE ARTICOLO","CODICE ARTICOLO"], as_index=False)[["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"]].sum()
df_articoli = df_articoli.sort_values(by=["NUMERO PACCHI OLTRE 15 GIORNI", "NUMERO CAPI OLTRE 15 GIORNI", "NUMERO PACCHI DA 5 A 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI"], ascending=False)

st.dataframe(df_articoli, hide_index=True,
             column_order=("CODICE ARTICOLO","DESCRIZIONE ARTICOLO","NUMERO PACCHI OLTRE 15 GIORNI", "NUMERO CAPI OLTRE 15 GIORNI", "NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO CAPI DA 5 A 15 GIORNI"),
             column_config={
                 "CODICE ARTICOLO" : st.column_config.TextColumn("CODICE"),
                 "NUMERO PACCHI OLTRE 15 GIORNI": st.column_config.TextColumn("PACCHI 15+"),
                 "NUMERO CAPI OLTRE 15 GIORNI": st.column_config.TextColumn("CAPI 15+"),
                 "NUMERO PACCHI DA 5 A 15 GIORNI": st.column_config.TextColumn("PACCHI 5-15"),
                 "NUMERO CAPI DA 5 A 15 GIORNI": st.column_config.TextColumn("CAPI 5-15")
             })

# Dettaglio destinatari

df_destinatari = df2.loc[df2["DATA"]==df2["DATA"].max()]
df_destinatari = df_destinatari.groupby(by="DESCRIZIONE DESTINATARIO", as_index=False)[["NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO PACCHI OLTRE 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI","NUMERO CAPI OLTRE 15 GIORNI"]].sum()
df_destinatari = df_destinatari.sort_values(by=["NUMERO PACCHI OLTRE 15 GIORNI", "NUMERO CAPI OLTRE 15 GIORNI", "NUMERO PACCHI DA 5 A 15 GIORNI","NUMERO CAPI DA 5 A 15 GIORNI"], ascending=False)

''' 
Elenco dei destinatari di produzione
'''

st.dataframe(df_destinatari, hide_index=True,
column_order=("DESCRIZIONE DESTINATARIO","NUMERO PACCHI OLTRE 15 GIORNI", "NUMERO CAPI OLTRE 15 GIORNI", "NUMERO PACCHI DA 5 A 15 GIORNI", "NUMERO CAPI DA 5 A 15 GIORNI"),
             column_config={
                 "NUMERO PACCHI OLTRE 15 GIORNI": st.column_config.TextColumn("PACCHI 15+"),
                 "NUMERO CAPI OLTRE 15 GIORNI": st.column_config.TextColumn("CAPI 15+"),
                 "NUMERO PACCHI DA 5 A 15 GIORNI": st.column_config.TextColumn("PACCHI 5-15"),
                 "NUMERO CAPI DA 5 A 15 GIORNI": st.column_config.TextColumn("CAPI 5-15")
             })


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


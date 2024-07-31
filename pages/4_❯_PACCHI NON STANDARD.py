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

st.set_page_config(page_title="Pacchi non standard")

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

directory = r'Data/PacchiNonStandard'

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

st.header("PACCHI NON STANDARD", divider='orange')

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
# Pacchi non standard - statistica generale

st.markdown("### :orange[Andamento generale]")
'''
Raporto percentuale dei pacchi Non Standard in rapporto ai pacchi per tutti gli stabilimenti
'''
'''

'''

nstandard_generale = df.groupby(by=["DESCRIZIONE STABILIMENTO"], as_index=False)["%"].mean() # Da filtrare prima per ultima data
nstandard_generale = nstandard_generale.sort_values(by=["%"], ascending=False)
nstandard_generale["%"] = round(nstandard_generale["%"],2)

col1,col2 = st.columns(2)

col1.metric(label=":orange[Media % pacchi non standard]", value=round(nstandard_generale["%"].mean(),2))
col2.dataframe(nstandard_generale, hide_index=True, column_order=("%", "DESCRIZIONE STABILIMENTO"))

# ----------------------------------------------------------
# Pacchi non standard - per stabilimento - filtro
'''
---

'''

st.markdown('### :orange[Dettaglio per Stabilimento]')

stabilimenti = df["DESCRIZIONE STABILIMENTO"].unique()
option = st.selectbox("Seleziona lo stabilimento",stabilimenti)

df_filter = df.loc[df["DESCRIZIONE STABILIMENTO"]==option]
df_filter_stabilimento = df_filter.groupby(by=["DATA"],as_index=False)["%"].mean()

mean_stabilimentoNonStandard = round(df_filter_stabilimento['%'].mean(),1)

st.metric(label=":orange[Media % dei pacchi non Standard]", value=f'{mean_stabilimentoNonStandard} %')

st.line_chart(df_filter_stabilimento, x="DATA", y="%")

df_filter_articolo = df_filter.groupby(by=["DESCRIZIONE ARTICOLO", "CODICE ARTICOLO"], as_index=False)["%"].mean()
df_filter_articolo = df_filter_articolo.loc[df_filter_articolo["%"]>0]
df_filter_articolo["%"] = round(df_filter_articolo["%"],2)


'''
Elenco degli articoli identificati come Non Standard
'''
st.dataframe(df_filter_articolo.sort_values(by="%", ascending=False), hide_index=True, column_order=("%", "CODICE ARTICOLO","DESCRIZIONE ARTICOLO"),
             column_config={'%': st.column_config.ProgressColumn("%", min_value=0, max_value=100, format="%f")})



'''
---
'''
articolo_code = st.text_input("Dettaglio articolo")

if articolo_code:
    df_articolo_code = df.loc[df["CODICE ARTICOLO"]==articolo_code]
    df_articolo_code = df_articolo_code.loc[df_articolo_code["DESCRIZIONE STABILIMENTO"] == option]
    df_articolo_code = df_articolo_code.groupby(by="DATA", as_index=False)['%'].mean()
    df_articolo_code = df_articolo_code.sort_values(by="DATA", ascending=False)

    mean_nonStandard = round(df_articolo_code["%"].mean(),1)

    st.metric(label=":orange[In media non standard]", value=f'{mean_nonStandard} %')

    st.line_chart(df_articolo_code, x="DATA", y=["%"])

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
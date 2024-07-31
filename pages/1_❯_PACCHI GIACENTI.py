import pandas as pd
import os
import numpy as np
import streamlit as st
from ReportPy.Giacenze_report import load_graph
from io import BytesIO
import matplotlib.pyplot as plt
from fpdf import FPDF



# ----------------------------------------------------------
# Configurazione Pandas

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# ----------------------------------------------------------
# Configurazione Streamlit

st.set_page_config(page_title="Giacenza Pacchi/Pezzi 30+")

with open(r'pages/style.css') as f:
    st.markdown(f'<style>{f.read()}</style', unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




# ----------------------------------------------------------
# Nome report

st.header("PACCHI GIACENTI", divider='orange')


# ----------------------------------------------------------
# Loading di tutti i dataset dalla cartella

directory = r'Data/PacchiGiacenti'

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
# Markdown ultimo aggiornamento

df_date = df["DATA"]
aggiornamento = df_date.max()
st.markdown(f'''
:gray[Ultimo aggiornamento: {aggiornamento}]''')


'''
---

'''

# ----------------------------------------------------------
# Somma di tutti i pacchi/pezzi in giacenza - metriche


st.markdown("### :orange[Andamento generale]")
'''
Andamento temporale dei pacchi in carico oltre 30 giorni di tutti i Guardaroba.
Le metriche "Totale Giacenza Pacchi" e "Totale Giacenza Pezzi" presentano la variazione
percentuale rispetto alla settimana precedente
'''


totale_giacenze = df.loc[df["DATA"]==df["DATA"].max()]
totale_pacchi = totale_giacenze["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].sum()
totale_pezzi = totale_giacenze["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].sum()

delta_df = df.groupby(by=["DATA"], as_index=False)[["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"]].sum()
delta_df = delta_df.sort_values(by=["DATA"], ascending=False)

delta_pacchi = round(((totale_pacchi-delta_df["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[1])/delta_df["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[1])*100,2)
delta_pezzi = round(((totale_pezzi-delta_df["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[1])/delta_df["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[1])*100,2)


col1, col2 = st.columns(2)
col1.metric(label=":orange[Totale giacenza pacchi oltre 30g]", value='{:,}'.format(totale_pacchi).replace(',', '.'), delta=f"{delta_pacchi} %", delta_color="inverse")
col2.metric(label=":orange[Totale giacenza pezzi oltre 30g]", value='{:,}'.format(totale_pezzi).replace(',', '.'), delta=f"{delta_pezzi} %", delta_color="inverse")

'''
---

'''


# ----------------------------------------------------------
# Andamento medio giacenza

'''
:orange[Andamento giacenza pacchi/pezzi oltre 30 giorni]

'''

totale_pacchi_daily = df.groupby(by=["DATA", "Month", "Day"], as_index=False)[["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI","NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"]].sum()
totale_pacchi_daily = totale_pacchi_daily.sort_values(by=["Month", "Day"])
st.line_chart(totale_pacchi_daily, x="DATA", y=["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI","NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"], use_container_width=True)

'''
---

'''

st.markdown(':orange[Rapporto numero Pacchi/Pezzi in carico oltre 30 giorni]')
'''
Tramite lo scatterplot è possibile visualizzare la situazione all'ultimo aggiornamento del rapporto tra
numero pacchi e pezzi in carico oltre 30 giorni. 
I Guardaroba più performanti si posizionano nel primo quadrante in basso a sinistra. Al contrario, i Guardaroba 
meno performanti si posizionano a distanza della distribuzione degli altri Guardaroba
'''


df_vega = df.loc[df["DATA"]==df["DATA"].max()]
df_vega = df_vega.groupby(by=["DESCRIZIONE GUARDAROBA"], as_index=False)[["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"]].sum()


st.vega_lite_chart(df_vega, {
    'mark': {'type': 'circle', 'tooltip':True},
    'encoding': {
        'x': {'field': 'NUMERO PACCHI IN CARICO OLTRE 30 GIORNI', 'type': 'quantitative'},
        'y': {'field': 'NUMERO PEZZI IN CARICO OLTRE 30 GIORNI', 'type': 'quantitative'},
        'color': {'field': 'DESCRIZIONE GUARDAROBA', 'type': 'nominal', },
    }
}, use_container_width=True, legends=False)


# ----------------------------------------------------------
# Ranking peggiore

'''
---

'''

'''
:orange[Classifica Guardaroba per pacchi/pezzi fermi 30+ giorni]

'''
'''
Elenco dei Guardaroba con il numero maggiore di Pacchi e Pezzi in giacenza oltre 30 giorni all'ultimo aggiornamento disponibile
'''


rank_pacchi = df.loc[df["DATA"]==df["DATA"].max()]
rank_pacchi = rank_pacchi.groupby(by=["DATA", "DESCRIZIONE GUARDAROBA"], as_index=False)["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].sum()
rank_pacchi = rank_pacchi.sort_values(by="NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", ascending=False).head(5)

rank_pezzi = df.loc[df["DATA"]==df["DATA"].max()]
rank_pezzi = rank_pezzi.groupby(by=["DATA", "DESCRIZIONE GUARDAROBA"], as_index=False)["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].sum()
rank_pezzi = rank_pezzi.sort_values(by="NUMERO PEZZI IN CARICO OLTRE 30 GIORNI", ascending=False).head(5)


col1,col2 =st.columns(2)
col1.dataframe(rank_pacchi, hide_index=True, column_config={"DATA": None, "NUMERO PACCHI IN CARICO OLTRE 30 GIORNI": st.column_config.TextColumn("PACCHI")})
col2.dataframe(rank_pezzi, hide_index=True, column_config={"DATA": None, "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI": st.column_config.TextColumn("PEZZI")})

'''
---
'''
# ----------------------------------------------------------
# Dettaglio per guardaroba
st.markdown("### :orange[Dettaglio per Guardaroba]")
elenco_guardaroba = df["DESCRIZIONE GUARDAROBA"].unique()
option = st.selectbox("Seleziona il guardaroba",elenco_guardaroba)

df_guardaroba = df.loc[df["DESCRIZIONE GUARDAROBA"]==option]
df_guardaroba2 = df_guardaroba.groupby(by=["DATA"], as_index=False)[["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"]].sum()


ultimi_dati_guardaroba = df_guardaroba2.loc[df_guardaroba2["DATA"]==df_guardaroba2["DATA"].max()]
ultimi_pacchi_guardaroba = ultimi_dati_guardaroba["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].sum()
ultimi_pezzi_guardaroba = ultimi_dati_guardaroba["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].sum()

df_delta = df_guardaroba2.sort_values(by="DATA", ascending=False)

delta_pacchi_guardaroba = round(((ultimi_pacchi_guardaroba-df_delta["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[1])/df_delta["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[1])*100,2)
delta_pezzi_guardaroba = round(((ultimi_pezzi_guardaroba-df_delta["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[1])/df_delta["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[1])*100,2)

col1, col2 = st.columns(2)

col1.metric(label="Pacchi in carico oltre 30 giorni", value=ultimi_pacchi_guardaroba, delta=f"{delta_pacchi_guardaroba} %", delta_color="inverse")
col2.metric(label="Pezzi in carico oltre 30 giorni", value=ultimi_pezzi_guardaroba, delta=f"{delta_pezzi_guardaroba} %", delta_color="inverse")


st.line_chart(df_guardaroba2, x="DATA", y=["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"])

# Dettaglio articoli

'''
Elenco degli articoli (in Pacchi/Pezzi) in giacenza oltre 30 giorni per ogni guardaroba
'''

df_articoli = df_guardaroba.loc[df_guardaroba["DATA"]==df_guardaroba["DATA"].max()]
df_articoli_pacchi = df_articoli.groupby(by=["DESCRIZIONE ARTICOLO", "CODICE ARTICOLO"], as_index=False)["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].sum()
df_articoli_pezzi = df_articoli.groupby(by=["DESCRIZIONE ARTICOLO", "CODICE ARTICOLO"], as_index=False)["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].sum()

# ------------------------------------------------------------------------------------------------------------------------------
# Serve per stampare il report correttamente - Pacchi
report_articolipacchi = df_articoli_pacchi[["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "CODICE ARTICOLO", "DESCRIZIONE ARTICOLO"]]
report_articolipacchi.rename(columns={'NUMERO PACCHI IN CARICO OLTRE 30 GIORNI': 'NUMERO PACCHI'}, inplace=True)
report_articolipacchi = report_articolipacchi.sort_values(by="NUMERO PACCHI", ascending=False)

# Serve per stampare il report correttamente - Pezzi
report_articolipezzi = df_articoli_pezzi[["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI", "CODICE ARTICOLO", "DESCRIZIONE ARTICOLO"]]
report_articolipezzi.rename(columns={'NUMERO PEZZI IN CARICO OLTRE 30 GIORNI': 'NUMERO PEZZI'}, inplace=True)
report_articolipezzi = report_articolipezzi.sort_values(by="NUMERO PEZZI", ascending=False)
# ------------------------------------------------------------------------------------------------------------------------------

sum_pacchi = df_articoli_pacchi["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].sum()
sum_pacchi = int(sum_pacchi)

sum_pezzi = df_articoli_pezzi["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].sum()
sum_pezzi = int(sum_pezzi)

st.dataframe(df_articoli_pacchi.sort_values(by="NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO PACCHI IN CARICO OLTRE 30 GIORNI', "CHECK",'CODICE ARTICOLO','DESCRIZIONE ARTICOLO'),
               column_config={"NUMERO PACCHI IN CARICO OLTRE 30 GIORNI": st.column_config.ProgressColumn(
                   "PACCHI",min_value=0, max_value=sum_pacchi,format="%f"
               )})
st.dataframe(df_articoli_pezzi.sort_values(by="NUMERO PEZZI IN CARICO OLTRE 30 GIORNI", ascending=False), hide_index=True, column_order=('NUMERO PEZZI IN CARICO OLTRE 30 GIORNI', "CHECK",'CODICE ARTICOLO','DESCRIZIONE ARTICOLO'),
               column_config={"NUMERO PEZZI IN CARICO OLTRE 30 GIORNI": st.column_config.ProgressColumn(
                   "PEZZI", min_value=0, max_value=sum_pezzi, format="%f"
               )})


# ----------------------------------------------------------------------------------------------------------------------------
# REPORT ALERT
# ----------------------------------------------------------------------------------------------------------------------------
def create_title(pdf,guardaroba):
    pdf.set_font('Arial', '', 24)
    pdf.ln(120)
    pdf.cell(w=0, h=5, txt=f'Report Pacchi Giacenti', align="R")
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    pdf.cell(w=0, h=5, txt=guardaroba, align="R")
    pdf.ln(10)

def load_graph(guardaroba,x,y,pacchi, delta_pack, pezzi, delta_pezzi, pdf_fn, data, data2):
    pdf = FPDF('P', 'mm', 'A4')

   # Prima pagina
    pdf.add_page()
    pdf.image(r'ReportPy/fronte_image.png', x=0, y=0, w=0, h=0)
    create_title(pdf,guardaroba)

    # Seconda pagina

    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(w=0, h=5, txt="Andamento Settimanale Pacchi Giacenti", align="C")
    pdf.ln(20)
    plt.plot(x, y)  # Creazione bar chart
    plt.gcf().autofmt_xdate()
    plt.savefig(r'ReportPy/graph.png')

    # Caricamento del primo grafico
    pdf.image(r'ReportPy/graph.png', 0, 30, w=0)

    # Terza Pagina

    pdf.add_page()
    pdf.ln(10)
    pdf.cell(w=0, h=5, txt="Situazione settimana corrente", align="C")
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=0, h=5, txt="Pacchi in carico oltre 30 giorni:", align="L")
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    pdf.cell(w=0, h=5, txt=f'{pacchi} ({delta_pack} % - Rispetto la settimana precedente)', align="L")
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=0, h=5, txt="Pezzi in carico oltre 30 giorni:", align="L")
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    pdf.cell(w=0, h=5, txt=f'{pezzi} ({delta_pezzi} % - Rispetto la settimana precedente)', align="L")
    pdf.ln(20)

    # Quarta pagina
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=0, h=5, txt="Articoli (espressi in Pacchi) in giacenza oltre 30 giorni ", align="C")
    pdf.ln(10)
    df = pd.DataFrame(data)

    titoli = df.columns.tolist()
    altezza_riga = 10

    pdf.set_font('Arial', '', 8)
    for titolo in titoli:
        pdf.cell(60, altezza_riga, str(titolo), border=1)
    pdf.ln()

    for indice, riga in df.iterrows():
        for dato in riga:
            pdf.cell(60, altezza_riga, str(dato), border=1)
        pdf.ln()

    # Quinta pagina
    pdf.add_page()
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=0, h=5, txt="Articoli (espressi in Pezzi) in giacenza oltre 30 giorni ", align="C")
    pdf.ln(10)
    df1 = pd.DataFrame(data2)

    titoli2 = df1.columns.tolist()
    altezza_riga2 = 10

    pdf.set_font('Arial', '', 8)
    for titolo in titoli2:
        pdf.cell(60, altezza_riga2, str(titolo), border=1)
    pdf.ln()

    for indice, riga in df1.iterrows():
        for dato in riga:
            pdf.cell(60, altezza_riga2, str(dato), border=1)
        pdf.ln()


    # Salva il pdf in una variabile BytesIO
    pdf.output(pdf_fn)


# ------------------------------------------------------------------------------------------------------------------------------------------

# Bottone Alert
if st.button(label="GENERA ALERT REPORT", type="primary"):
    name = "test.pdf"
    load_graph(option, df_guardaroba2["DATA"], df_guardaroba2[["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"]],str(ultimi_pacchi_guardaroba), str(delta_pacchi_guardaroba), str(ultimi_pezzi_guardaroba), str(delta_pezzi_guardaroba), name, report_articolipacchi,report_articolipezzi)
    with open(name, 'rb') as h_pdf:
        st.download_button(label="Clicca per scaricare", data=h_pdf, file_name=f"Pacchi giacenti_{option}.pdf", mime='application/pdf')



'''
---
'''

articolo_code = st.text_input("Dettaglio articolo")

'''
Selezionare l'articolo di interesse per vederne il dettaglio
'''
if articolo_code:

    df_articolo_code = df.loc[df["CODICE ARTICOLO"]==articolo_code]
    df_articolo_code = df_articolo_code.loc[df_articolo_code["DESCRIZIONE GUARDAROBA"]==option]
    df_articolo_code = df_articolo_code.groupby(by="DATA", as_index=False)[["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"]].sum()
    df_articolo_code = df_articolo_code.sort_values(by="DATA", ascending=False)

    prec_articolo_pacchi = df_articolo_code["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[1]
    prec_articolo_pezzi = df_articolo_code["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[1]

    today_articolo_pacchi = df_articolo_code["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[0]
    today_articolo_pezzi = df_articolo_code["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[0]

    delta_articolo_pacchi = round(((df_articolo_code["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[0]-df_articolo_code["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[1])/df_articolo_code["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI"].iloc[1])*100,2)
    delta_articolo_pezzi = round(((df_articolo_code["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[0]-df_articolo_code["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[1])/df_articolo_code["NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"].iloc[1])*100,2)


    col3, col4, col5, col6 = st.columns(4)

    col3.metric(label="PACCHI SETTIMANA PREC", value=prec_articolo_pacchi)
    col4.metric(label="PACCHI SETTIMANA CORR", value=today_articolo_pacchi, delta=f"{delta_articolo_pacchi} %", delta_color="inverse")
    col5.metric(label="PEZZI SETTIMANA PREC", value=prec_articolo_pezzi)
    col6.metric(label="PEZZI SETTIMANA CORR", value=today_articolo_pezzi, delta=f"{delta_articolo_pezzi} %", delta_color="inverse")


    st.line_chart(df_articolo_code, x="DATA", y=["NUMERO PACCHI IN CARICO OLTRE 30 GIORNI", "NUMERO PEZZI IN CARICO OLTRE 30 GIORNI"])



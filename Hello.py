import streamlit as st



st.set_page_config(page_title="Benvenuti")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("### SI Monitoring Production System")
'''
v. beta3
'''

st.markdown("🔧:orange[Release Notes]")
'''
---
'''

st.markdown("🆕 :orange[1.0 beta 3 - 06/11/2023]")
'''
- Caricamento dei nuovi dati per i report Pacchi Giacenti, Non Conformi, Non Standard, Provvisori, Situazione
- Creazione sezione per i report: Uscite Stabilimento, Sotto Scorta, Sovra Scorta
- Bug fixing di un problema relativo al formato Data che impediva la corretta Analisi dei dati
- Rilascio pulsante "Genera Alert" in versione Beta per i report "Pacchi Giacenti"
'''

st.markdown("🆕 :orange[1.0 beta 2 - 04/10/2023]")
'''
- Sospensione del Report "Pacchi non standard"
- Rettifica metriche
- Bug fixing per il sistema di generazione di Alert e sospensione momentanea dell'uso
'''

st.markdown("🆕 :orange[1.0 beta 1]")
'''
- Caricamento e Data Analysis dei report forniti
- Rilascio dei moduli: Pacchi giacenti, Sotto scorta, Pacchi non conformi, Pacchi Provvisori, Pacchi non standard
- Generazione Software beta per creazione di un sistema di Alert in pdf per il modulo "Pacchi Giacenti"
'''

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


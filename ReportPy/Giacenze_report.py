import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

def create_title(pdf,guardaroba):


    pdf.set_font('Arial', '', 24)
    pdf.ln(100)
    pdf.cell(w=0, h=5, txt=f'Report Pacchi Giacenti', align="R")
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    pdf.cell(w=0, h=5, txt=guardaroba, align="R")
    pdf.ln(10)

def load_graph(guardaroba,x,y,pacchi, pezzi):
    pdf = FPDF('P', 'mm', 'A4')

    ''' Prima Pagina '''
    pdf.add_page()
    pdf.image(r'C:\\Users\\vincenzo.citignola\\Documents\\GitHub\\reportSI\\ReportPy\\fronte_image.png', x=0, y=0, w=0, h=0)
    create_title(pdf,guardaroba)

    ''' Seconda Pagina - line chart '''
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(w=0, h=5, txt="Andamento Settimanale Pacchi Giacenti", align="C")
    pdf.ln(20)
    plt.plot(x, y)  # Creazione bar chart
    plt.gcf().autofmt_xdate()
    plt.savefig(r'C:\\Users\\vincenzo.citignola\\Documents\\GitHub\\reportSI\\ReportPy\\graph.png')

    # Caricamento del primo grafico
    pdf.image(r'C:\\Users\\vincenzo.citignola\\Documents\\GitHub\\reportSI\\ReportPy\\graph.png', 0, 30, w=0)

    ''' Terza Pagina - metriche '''
    pdf.add_page()
    pdf.ln(10)
    pdf.cell(w=0, h=5, txt="Situazione settimana corrente", align="C")
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=0, h=5, txt="Pacchi in carico oltre 30 giorni:", align="L")
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    pdf.cell(w=0, h=5, txt=pacchi, align="L")
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=0, h=5, txt="Pezzi in carico oltre 30 giorni:", align="L")
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    pdf.cell(w=0, h=5, txt=pezzi, align="L")
    pdf.ln(20)

    # Salva il pdf in una variabile BytesIO
    pdf_output = BytesIO()
    pdf.output(pdf_output).encode('latin-1')
    pdf_bytes = pdf_output.getvalue()
    pdf_output.close()

    return pdf_bytes





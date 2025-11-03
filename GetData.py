# archivo: app.py
import streamlit as st
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfMerger

# Clase Escenario
class Escenario:
    def __init__(self, ID, title, description, test_result, images):
        self.ID = ID
        self.title = title
        self.description = description
        self.test_result = test_result
        self.images = images

# Lista de escenarios (almacenada en sesión para mantener entre interacciones)
if "escenarios" not in st.session_state:
    st.session_state.escenarios = []

st.title("Generador Automático de Reportes QA")

# Información del reporte
tester = st.text_input("Tester:")
proyecto = st.text_input("Proyecto:")
documento = st.text_input("Nombre del Documento:")
empresa = st.text_input("Empresa:")

st.subheader("Agregar Escenario de Prueba")
col1, col2 = st.columns(2)
with col1:
    ID = st.text_input("ID del Escenario", key="id")
    title = st.text_input("Título", key="title")
with col2:
    test_result = st.selectbox("Resultado", ["Tested", "Test Failed", "on Hold","Rejected"], key="resultado")
description = st.text_area("Descripción", key="desc")
images = st.file_uploader("Subir imágenes de evidencia", accept_multiple_files=True, type=["png","jpg","jpeg","bmp","gif"])

if st.button("Agregar Escenario"):
    if not (ID and title and description and test_result):
        st.warning("Por favor llena todos los campos del escenario.")
    else:
        image_paths = []
        for img in images:
            path = f"temp_{img.name}"
            with open(path, "wb") as f:
                f.write(img.getbuffer())
            image_paths.append(path)
        escenario = Escenario(ID, title, description, test_result, image_paths)
        st.session_state.escenarios.append(escenario)
        st.success(f"Escenario '{title}' agregado correctamente!")

# Mostrar tabla de escenarios agregados
if st.session_state.escenarios:
    st.subheader("Escenarios Agregados")
    for e in st.session_state.escenarios:
        st.write(f"ID: {e.ID} | Título: {e.title} | Resultado: {e.test_result}")

# Generar PDF
def generar_pdf():
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nombre_pdf = f"{documento.replace(' ', '_')}.pdf"
    c = canvas.Canvas(nombre_pdf, pagesize=A4)
    width, height = A4

    # Encabezado
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, f"Reporte de QA - {empresa}")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Proyecto: {proyecto}")
    c.drawString(50, height - 85, f"Tester: {tester}")
    c.drawString(50, height - 100, f"Fecha: {fecha}")
    c.drawString(50, height - 115, f"Documento: {documento}")

    y = height - 150
    for e in st.session_state.escenarios:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"ID: {e.ID} - {e.title}")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Descripción: {e.description[:90]}")
        y -= 15
        c.drawString(50, y, f"Resultado: {e.test_result}")
        y -= 30

        for img in e.images:
            try:
                image = ImageReader(img)
                c.drawImage(image, 60, y - 120, width=200, height=120)
                y -= 140
                if y < 150:
                    c.showPage()
                    y = height - 100
            except Exception:
                c.drawString(60, y, f"Error al cargar imagen: {os.path.basename(img)}")
                y -= 20
        y -= 20
        if y < 150:
            c.showPage()
            y = height - 100
    c.save()
    st.success(f"PDF generado: {nombre_pdf}")
    st.download_button("Descargar PDF", data=open(nombre_pdf, "rb").read(), file_name=nombre_pdf)

if st.button("Generar PDF del Reporte"):
    if not (tester and proyecto and documento and empresa):
        st.warning("Por favor completa los datos del reporte.")
    elif not st.session_state.escenarios:
        st.warning("Debes agregar al menos un escenario.")
    else:
        generar_pdf()


#streamlit run GetData.py -- para correr el archivo    



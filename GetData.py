import os
import importlib.util
import sys
import subprocess

# 🔹 Verificar si matplotlib está instalado, si no, instalarlo antes de importarlo
if importlib.util.find_spec("matplotlib") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])

# Ahora sí se pueden hacer los imports normalmente
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfMerger
import matplotlib.pyplot as plt
import numpy as np

# Clase Escenario
class Escenario:
    def __init__(self, ID, title, description, test_result, images):
        self.ID = ID
        self.title = title
        self.description = description
        self.test_result = test_result
        self.images = images

# Inicializar lista de escenarios
if "escenarios" not in st.session_state:
    st.session_state.escenarios = []

st.title("Generador Automático de Reportes QA")

# Información del reporte
tester = st.text_input("Tester:")
proyecto = st.text_input("Proyecto:")
documento = st.text_input("Nombre del Documento:")
empresa = st.text_input("Empresa:")

# Sección para agregar escenarios
st.subheader("Agregar Escenario de Prueba")
col1, col2 = st.columns(2)
with col1:
    ID = st.text_input("ID del Escenario", key="id")
    title = st.text_input("Título", key="title")
with col2:
    test_result = st.selectbox("Resultado", ["Tested", "Test Failed", "On Hold", "Rejected"], key="resultado")

description = st.text_area("Descripción", key="desc", height=250, max_chars=450, placeholder="Coloca aquí la descripción del escenario")

images = st.file_uploader("Subir imágenes de evidencia", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

# Mostrar imágenes
if images:
    for x in images:
        if x.type not in ["image/png", "image/jpeg", "image/jpg"]:
            st.warning("Solo se permiten archivos de imagen (PNG, JPG, JPEG).")
        else:
            st.image(x, caption=x.name, use_container_width=True)

# Botón para agregar escenario
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

# Mostrar escenarios
if st.session_state.escenarios:
    st.subheader("Escenarios Agregados")
    for e in st.session_state.escenarios:
        st.write(f"**ID:** {e.ID} | **Título:** {e.title} | **Resultado:** {e.test_result}")

# Eliminar escenarios
if st.button("Eliminar Escenarios"):
    if not st.session_state.escenarios:
        st.warning("No hay escenarios para eliminar.")
    else:
        st.session_state.escenarios.clear()
        st.success("Escenarios eliminados correctamente!")
        st.rerun()

# --- 📊 Generar y mostrar gráfica ---
def generarGrafica():
    resultados = [e.test_result for e in st.session_state.escenarios]
    if not resultados:
        st.warning("No hay datos para generar la gráfica.")
        return None

    valores, conteos = np.unique(resultados, return_counts=True)

    fig, ax = plt.subplots()
    ax.pie(conteos, labels=valores, autopct='%1.1f%%', startangle=90)
    ax.set_title("Distribución de Resultados de Escenarios")

    plt.savefig("grafica.png")
    st.pyplot(fig)
    return "grafica.png"

# --- 🧾 Generar PDF del contenido ---
def generar_pdf_contenido(nombre_pdf, grafica_path=None):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
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
        if y < 200:
            c.showPage()
            y = height - 100

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"ID: {e.ID} - {e.title}")
        y -= 20

        c.setFont("Helvetica", 10)
        descripcion = e.description
        max_chars = 90
        for i in range(0, len(descripcion), max_chars):
            c.drawString(60, y, descripcion[i:i+max_chars])
            y -= 15

        c.drawString(60, y, f"Resultado: {e.test_result}")
        y -= 30

        for img in e.images:
            try:
                image = ImageReader(img)
                img_width, img_height = 450, 250
                if y - img_height < 100:
                    c.showPage()
                    y = height - 100
                c.drawImage(image, 60, y - img_height, width=img_width, height=img_height)
                y -= img_height + 30
            except Exception:
                c.drawString(60, y, f"Error al cargar imagen: {os.path.basename(img)}")
                y -= 20

        y -= 30
        if y < 150:
            c.showPage()
            y = height - 100

    # Añadir gráfica si existe
    if grafica_path and os.path.exists(grafica_path):
        c.showPage()
        c.drawImage(grafica_path, 60, height - 450, width=450, height=350)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(180, height - 470, "Gráfica de Resultados QA")

    c.save()

# --- 📚 Unir portada + reporte ---
def unir_portada_con_reporte(nombre_pdf):
    merger = PdfMerger()
    portada_path = "portada.pdf"

    if os.path.exists(portada_path):
        merger.append(portada_path)
    else:
        st.warning("⚠️ No se encontró el archivo 'portada.pdf' en el mismo directorio.")

    merger.append(nombre_pdf)
    final_name = f"Reporte_QA_{documento.replace(' ', '_')}.pdf"
    merger.write(final_name)
    merger.close()
    return final_name

# --- 🎯 Botón para generar reporte ---
if st.button("Generar PDF del Reporte"):
    if not (tester and proyecto and documento and empresa):
        st.warning("Por favor completa los datos del reporte.")
    elif not st.session_state.escenarios:
        st.warning("Debes agregar al menos un escenario.")
    else:
        grafica_path = generarGrafica()
        nombre_pdf = f"{documento.replace(' ', '_')}_contenido.pdf"
        generar_pdf_contenido(nombre_pdf, grafica_path)
        final_pdf = unir_portada_con_reporte(nombre_pdf)

        st.success(f"✅ PDF generado: {final_pdf}")
        with open(final_pdf, "rb") as f:
            st.download_button("📄 Descargar PDF Final", data=f.read(), file_name=final_pdf)

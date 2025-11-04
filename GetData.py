import streamlit as st
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Clase Escenario
class Escenario:
    def __init__(self, ID, title, description, test_result, images):
        self.ID = ID
        self.title = title
        self.description = description
        self.test_result = test_result
        self.images = images

# Inicializar lista de escenarios en la sesión
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

description = st.text_area(
    "Descripción", 
    key="desc",
    height=250, 
    max_chars=450,
    placeholder="Coloca aquí la descripción del escenario"
)

images = st.file_uploader(
    "Subir imágenes de evidencia",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg"]
)

# Mostrar las imágenes cargadas
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

# Mostrar los escenarios agregados
if st.session_state.escenarios:
    st.subheader("Escenarios Agregados")
    for e in st.session_state.escenarios:
        st.write(f"**ID:** {e.ID} | **Título:** {e.title} | **Resultado:** {e.test_result}")

# Botón para eliminar todos los escenarios
if st.button("Eliminar Escenarios"):
    if not st.session_state.escenarios:
        st.warning("No hay escenarios para eliminar.")
    else:
        st.session_state.escenarios.clear()
        st.success("Escenarios eliminados correctamente!")
        st.rerun()
        
# Función para generar el PDF
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

    y = height - 150  # posición inicial del contenido

    for e in st.session_state.escenarios:
        # Verificar si hay espacio antes de escribir un escenario nuevo
        if y < 200:
            c.showPage()
            y = height - 100

        # Título del escenario
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"ID: {e.ID} - {e.title}")
        y -= 20

        # Descripción con salto automático
        c.setFont("Helvetica", 10)
        descripcion = e.description
        max_chars = 90
        for i in range(0, len(descripcion), max_chars):
            c.drawString(60, y, descripcion[i:i+max_chars])
            y -= 15

        # Resultado
        c.drawString(60, y, f"Resultado: {e.test_result}")
        y -= 30

        # Imágenes de evidencia
        for img in e.images:
            try:
                image = ImageReader(img)
                img_width, img_height = 450, 250

                # Si no cabe la imagen, nueva página
                if y - img_height < 100:
                    c.showPage()
                    y = height - 100

                c.drawImage(image, 60, y - img_height, width=img_width, height=img_height)
                y -= img_height + 30  # espacio después de la imagen

            except Exception:
                c.drawString(60, y, f"Error al cargar imagen: {os.path.basename(img)}")
                y -= 20

        # Separación entre escenarios
        y -= 30
        if y < 150:
            c.showPage()
            y = height - 100

    # Guardar PDF
    c.save()
    st.success(f"PDF generado: {nombre_pdf}")
    with open(nombre_pdf, "rb") as f:
        st.download_button("📄 Descargar PDF", data=f.read(), file_name=nombre_pdf)

# Botón para generar el PDF del reporte
if st.button("Generar PDF del Reporte"):
    if not (tester and proyecto and documento and empresa):
        st.warning("Por favor completa los datos del reporte.")
    elif not st.session_state.escenarios:
        st.warning("Debes agregar al menos un escenario.")
    else:
        generar_pdf()

#streamlit run app.py -- para ejecutar la app

#versiones de prueba
#pase a QA
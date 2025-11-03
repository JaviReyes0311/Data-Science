
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfMerger


class Escenario:
    def __init__(self, ID, title, description, test_result, images):
        self.ID = ID
        self.title = title
        self.description = description
        self.test_result = test_result
        self.images = images


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Reportes QA")
        self.geometry("800x600")
        self.resizable(False, False)

        self.escenarios = []
        self._crear_interfaz()

    def _crear_interfaz(self):
        tk.Label(self, text="🧪 Generador Automático de Reportes QA", font=("Helvetica", 16, "bold")).pack(pady=10)

        frame_info = tk.LabelFrame(self, text="Información del Reporte", padx=10, pady=10)
        frame_info.pack(fill="x", padx=20, pady=10)

        # Entradas principales
        self.entry_tester = self._crear_campo(frame_info, "Tester:", 0)
        self.entry_proyecto = self._crear_campo(frame_info, "Proyecto:", 1)
        self.entry_documento = self._crear_campo(frame_info, "Nombre del Documento:", 2)
        self.entry_empresa = self._crear_campo(frame_info, "Empresa:", 3)

        # Frame de escenarios
        frame_esc = tk.LabelFrame(self, text="Escenarios de Prueba", padx=10, pady=10)
        frame_esc.pack(fill="both", expand=True, padx=20, pady=10)

        # Campos de escenario
        tk.Label(frame_esc, text="ID:").grid(row=0, column=0, sticky="w")
        self.entry_id = tk.Entry(frame_esc, width=10)
        self.entry_id.grid(row=0, column=1, padx=5)

        tk.Label(frame_esc, text="Título:").grid(row=0, column=2, sticky="w")
        self.entry_title = tk.Entry(frame_esc, width=30)
        self.entry_title.grid(row=0, column=3, padx=5)

        tk.Label(frame_esc, text="Resultado:").grid(row=0, column=4, sticky="w")
        self.combo_result = ttk.Combobox(frame_esc, values=["Pass", "Fail"], width=10)
        self.combo_result.grid(row=0, column=5, padx=5)

        tk.Label(frame_esc, text="Descripción:").grid(row=1, column=0, sticky="nw", pady=5)
        self.text_desc = tk.Text(frame_esc, width=70, height=3)
        self.text_desc.grid(row=1, column=1, columnspan=5, padx=5, pady=5)

        # Lista de imágenes
        tk.Label(frame_esc, text="Imágenes de evidencia:").grid(row=2, column=0, sticky="nw", pady=5)
        self.listbox_imgs = tk.Listbox(frame_esc, width=70, height=4)
        self.listbox_imgs.grid(row=2, column=1, columnspan=4, padx=5, pady=5)

        tk.Button(frame_esc, text="Agregar imágenes", command=self._agregar_imagenes).grid(row=2, column=5, padx=5)
        tk.Button(frame_esc, text="Agregar escenario", bg="#4CAF50", fg="white", command=self._guardar_escenario).grid(row=3, column=5, padx=5, pady=5)

        # Tabla de escenarios
        self.tree = ttk.Treeview(frame_esc, columns=("ID", "Título", "Resultado"), show="headings", height=5)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Resultado", text="Resultado")
        self.tree.grid(row=4, column=0, columnspan=6, pady=10)

        # Botón de generar reporte
        tk.Button(self, text="📄 Generar PDF", bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"), command=self._generar_pdf).pack(pady=10)

    def _crear_campo(self, parent, label, row):
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        entry = tk.Entry(parent, width=40)
        entry.grid(row=row, column=1, padx=10, pady=3)
        return entry

    def _agregar_imagenes(self):
        rutas = filedialog.askopenfilenames(
            title="Seleccionar imágenes de evidencia",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        for r in rutas:
            self.listbox_imgs.insert(tk.END, r)

    def _guardar_escenario(self):
        ID = self.entry_id.get()
        title = self.entry_title.get()
        description = self.text_desc.get("1.0", tk.END).strip()
        test_result = self.combo_result.get()
        images = list(self.listbox_imgs.get(0, tk.END))

        if not (ID and title and description and test_result):
            messagebox.showwarning("Campos incompletos", "Por favor llena todos los campos del escenario.")
            return

        escenario = Escenario(ID, title, description, test_result, images)
        self.escenarios.append(escenario)

        self.tree.insert("", tk.END, values=(ID, title, test_result))
        self.entry_id.delete(0, tk.END)
        self.entry_title.delete(0, tk.END)
        self.text_desc.delete("1.0", tk.END)
        self.combo_result.set("")
        self.listbox_imgs.delete(0, tk.END)

        messagebox.showinfo("Escenario agregado", "El escenario ha sido agregado correctamente.")

    def _obtener_fecha_internet(self):
        try:
            res = requests.get("http://worldtimeapi.org/api/timezone/America/Mexico_City")
            fecha = res.json()["datetime"]
            return datetime.fromisoformat(fecha[:-1]).strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _generar_pdf(self):
        tester = self.entry_tester.get()
        proyecto = self.entry_proyecto.get()
        documento = self.entry_documento.get()
        empresa = self.entry_empresa.get()

        if not (tester and proyecto and documento and empresa):
            messagebox.showwarning("Datos faltantes", "Por favor completa los datos del reporte.")
            return

        if not self.escenarios:
            messagebox.showwarning("Sin escenarios", "Debes agregar al menos un escenario.")
            return

        fecha = self._obtener_fecha_internet()
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
        for e in self.escenarios:
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
                    c.drawString(60, y, f"⚠️ Error al cargar imagen: {os.path.basename(img)}")
                    y -= 20

            y -= 20
            if y < 150:
                c.showPage()
                y = height - 100

        c.save()
        self._agregar_portada(nombre_pdf)
        messagebox.showinfo("Reporte generado", f"✅ Reporte generado: {nombre_pdf}")

    def _agregar_portada(self, reporte_pdf):
        merger = PdfMerger()
        if os.path.exists("portada.pdf"):
            merger.append("portada.pdf")
        else:
            print("⚠️ No se encontró 'portada.pdf'. Se generará solo el reporte.")
        merger.append(reporte_pdf)
        salida = f"reporte_final_{reporte_pdf}"
        merger.write(salida)
        merger.close()
        os.remove(reporte_pdf)
        os.rename(salida, reporte_pdf)


if __name__ == "__main__":
    app = App()
    app.mainloop()

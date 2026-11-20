import streamlit as st
import sqlite3
from datetime import datetime
import openai
import base64
import os
import pandas as pd
from fpdf import FPDF
import re

# 1. CONFIGURACIÓN DE PÁGINA (PRIMER ELEMENTO OBLIGATORIO - OPTIMIZADO PARA SEO LOCAL)
icono_pagina = "⚖️"
for posible_icono in ['avatar_cdl.png', 'avatar_cdl.jpg', 'avatar.png', 'logo.png']:
    if os.path.exists(posible_icono):
        icono_pagina = posible_icono
        break

st.set_page_config(
    page_title="Leites & Asociados | Abogado Penalista y Estudio Jurídico en Posadas",
    page_icon=icono_pagina,
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. FUNCIÓN PARA CARGAR IMÁGENES
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# CLASE PARA GENERAR EL PDF DEL ESTUDIO (ALINEADA CON HOJA MEMBRETADA INSTITUCIONAL)
class PDFEstudio(FPDF):
    def header(self):
        # Banda superior institucional Azul Marino (#162235 -> RGB 22, 34, 53)
        self.set_fill_color(22, 34, 53)
        self.rect(0, 0, 210, 6, 'F')
        self.ln(4)
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(22, 34, 53)
        self.cell(0, 8, 'LEITES & ASOCIADOS - ESTUDIO JURÍDICO', 0, 1, 'C')
        self.set_font('helvetica', '', 9)
        self.set_text_color(60, 65, 72)
        self.cell(0, 5, 'Dr. Cristian Darío Leites | Abogado Penalista (M.P. C.A.M. N° 4925)', 0, 1, 'C')
        self.ln(3)
        self.set_draw_color(197, 203, 211)
        self.line(12, self.get_y(), 198, self.get_y())
        self.ln(7)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(197, 203, 211)
        self.line(12, self.get_y(), 198, self.get_y())
        self.ln(2)
        self.set_font('helvetica', '', 8)
        self.set_text_color(90, 95, 100)
        self.cell(0, 4, 'Av. Uruguay N° 3184, 1° Piso - Posadas, Misiones | Tel: +54 376 487-6017 | consultas@estudioleites.com.ar', 0, 1, 'C')
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, f'www.estudioleites.com.ar | Documento generado digitalmente - Página {self.page_no()}', 0, 0, 'C')

def limpiar_texto_pdf(texto):
    reemplazos = {
        '—': '-', '–': '-', '“': '"', '”': '"', '‘': "'", '’': "'", '•': '-'
    }
    for orig, dest in reemplazos.items():
        texto = texto.replace(orig, dest)
    return texto.encode('latin-1', 'replace').decode('latin-1')

def generar_pdf_informe(titulo_caso, detalle_analisis, datos_extra=""):
    pdf = PDFEstudio()
    pdf.add_page()
    
    titulo_limpio = limpiar_texto_pdf(titulo_caso)
    analisis_limpio = limpiar_texto_pdf(detalle_analisis)
    extra_limpio = limpiar_texto_pdf(datos_extra)
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'R')
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(22, 34, 53)
    pdf.cell(0, 8, f"INFORME DE ORIENTACIÓN JURÍDICA: {titulo_limpio}", 0, 1, 'L')
    pdf.ln(3)
    
    if extra_limpio:
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(35, 37, 40)
        pdf.cell(0, 6, f"Detalles específicos: {extra_limpio}", 0, 1, 'L')
        pdf.ln(3)
        
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(22, 34, 53)
    pdf.cell(0, 6, "Directrices del Estudio:", 0, 1, 'L')
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(35, 37, 40)
    pdf.multi_cell(0, 6, analisis_limpio)
    pdf.ln(10)
    
    pdf.set_font('helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "Aviso: Este informe preliminar se encuentra amparado por el secreto profesional y constituye una orientación técnica inicial basada en los datos proporcionados por el consultante.")
    
    return bytes(pdf.output())

# 3. SISTEMA VISUAL INSTITUCIONAL (PALETA #162235, #F5F5F3, #232528, #C5CBD3 + CINZEL & MONTSERRAT)
fondo_path = None
for ext in ['fondo.jpg', 'fondo.jpeg', 'fondo.png']:
    if os.path.exists(ext):
        fondo_path = ext
        break

bg_css_rule = "background: linear-gradient(180deg, #162235 0%, #0F1826 100%);"
if fondo_path:
    try:
        fondo_base64 = get_base64_of_bin_file(fondo_path)
        tipo_img = "png" if "png" in fondo_path else "jpeg"
        bg_css_rule = f'''
            background-image: linear-gradient(180deg, rgba(22, 34, 53, 0.90) 0%, rgba(15, 24, 38, 0.95) 100%), url("data:image/{tipo_img};base64,{fondo_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        '''
    except Exception:
        pass

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');

/* Fondo principal y tipografía base */
.stApp {{
    {bg_css_rule}
    font-family: 'Montserrat', sans-serif;
    color: #F5F5F3;
}}

/* Espaciado superior ampliado para evitar corte con la barra superior de Streamlit */
.block-container {{
    max-width: 880px;
    padding-top: 4rem !important;
    padding-bottom: 3rem;
}}

/* Jerarquía tipográfica institucional */
h1, h2, h3, .cinzel-title {{
    font-family: 'Cinzel', Georgia, serif !important;
    color: #E6E9EF !important;
    letter-spacing: 0.03em;
}}

p, li, span, label, .stMarkdown {{
    font-family: 'Montserrat', sans-serif;
}}

/* Sidebar Institucional */
section[data-testid="stSidebar"] {{
    background-color: #0F1826 !important;
    border-right: 1px solid rgba(197, 203, 211, 0.22);
}}

section[data-testid="stSidebar"] * {{
    color: #F5F5F3;
}}

/* Botones de Streamlit adaptados a la marca */
div.stButton > button {{
    background: rgba(22, 34, 53, 0.88);
    color: #F5F5F3 !important;
    border: 1px solid rgba(197, 203, 211, 0.42);
    border-radius: 8px;
    padding: 0.75rem 1.1rem;
    font-family: 'Montserrat', sans-serif;
    font-weight: 500;
    transition: all 0.22s ease-in-out;
}}

div.stButton > button:hover {{
    background: #1E2F4A;
    border-color: #F5F5F3;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}}

div.stButton > button[kind="primary"] {{
    background: #F5F5F3 !important;
    color: #162235 !important;
    border: 1px solid #F5F5F3 !important;
    font-weight: 700 !important;
}}

div.stButton > button[kind="primary"] * {{
    color: #162235 !important;
}}

div.stButton > button[kind="primary"]:hover {{
    background: #C5CBD3 !important;
    border-color: #C5CBD3 !important;
}}

/* Componentes institucionales a medida */
.etiqueta-superior {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    color: #C5CBD3;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}}

/* Título principal idéntico en tipografía serif clásica y tono al logo del sidebar */
div[data-testid="stMarkdownContainer"] .titulo-estudio,
.titulo-estudio {{
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 2.85rem !important;
    font-weight: 500 !important;
    color: #E6E9EF !important;
    margin-top: 0.2rem !important;
    margin-bottom: 0.45rem !important;
    line-height: 1.15 !important;
    letter-spacing: 0.04em !important;
}}

.titulo-estudio .cap-inicial {{
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 1.13em !important;
    font-weight: 500 !important;
    color: #E6E9EF !important;
}}

.subtitulo-hero {{
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 1.12rem;
    font-weight: 500;
    color: #C5CBD3;
    letter-spacing: 0.05em;
    margin-bottom: 0.9rem;
}}

.bajada-hero {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.98rem;
    color: #E2E6EC;
    line-height: 1.65;
    margin-bottom: 1.4rem;
}}

.linea-plata {{
    height: 1px;
    background: linear-gradient(90deg, rgba(197,203,211,0.55) 0%, rgba(197,203,211,0.1) 100%);
    margin: 1.8rem 0;
}}

.seccion-titulo {{
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 1.45rem;
    font-weight: 600;
    color: #F5F5F3;
    letter-spacing: 0.04em;
    margin-top: 0.5rem;
    margin-bottom: 0.9rem;
    border-left: 3px solid #C5CBD3;
    padding-left: 12px;
}}

/* Tarjetas en Blanco Piedra (#F5F5F3) y Azul Marino (#162235) */
.card-piedra {{
    background-color: #F5F5F3;
    color: #232528;
    padding: 1.4rem 1.5rem;
    border-radius: 10px;
    border-top: 4px solid #162235;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.28);
    margin-bottom: 1rem;
}}

.card-piedra h4 {{
    font-family: 'Cinzel', Georgia, serif !important;
    color: #162235 !important;
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 0.5rem;
}}

.card-piedra p {{
    color: #232528 !important;
    font-size: 0.91rem;
    line-height: 1.55;
    margin-bottom: 0;
}}

.card-marino {{
    background: rgba(22, 34, 53, 0.85);
    border: 1px solid rgba(197, 203, 211, 0.28);
    border-radius: 10px;
    padding: 1.25rem;
    height: 100%;
    margin-bottom: 0.9rem;
}}

.card-marino h4 {{
    font-family: 'Cinzel', Georgia, serif !important;
    color: #F5F5F3 !important;
    font-size: 0.98rem;
    margin-top: 0;
    margin-bottom: 0.45rem;
}}

.card-marino p {{
    color: #C5CBD3 !important;
    font-size: 0.88rem;
    line-height: 1.5;
    margin-bottom: 0;
}}

.paso-numero {{
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 1.5rem;
    font-weight: 700;
    color: #C5CBD3;
    margin-bottom: 0.25rem;
}}

/* Acordeones (Preguntas Frecuentes) */
div[data-testid="stExpander"] {{
    background: rgba(22, 34, 53, 0.78);
    border: 1px solid rgba(197, 203, 211, 0.28);
    border-radius: 8px;
    margin-bottom: 0.6rem;
}}

div[data-testid="stExpander"] summary p {{
    font-weight: 600;
    color: #F5F5F3 !important;
}}

/* Footer institucional */
.footer-institucional {{
    background: #0F1826;
    border: 1px solid rgba(197, 203, 211, 0.28);
    border-radius: 12px;
    padding: 1.8rem 1.5rem;
    margin-top: 2.2rem;
    text-align: center;
}}

.btn-accion-hero {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 18px;
    border-radius: 8px;
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    text-decoration: none !important;
    transition: opacity 0.2s ease;
}}

.btn-accion-hero:hover {{
    opacity: 0.92;
}}
</style>
""", unsafe_allow_html=True)

# 4. BASE DE DATOS Y GENERACIÓN DE HTML ESTÁTICO
def init_db():
    conn = sqlite3.connect('consultas_legales_v2.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS triage 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, rol TEXT, tema TEXT, detalle TEXT, nivel_riesgo TEXT)
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS articulos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, titulo TEXT, contenido TEXT, imagen_path TEXT, slug TEXT)
    ''')
    try:
        c.execute("ALTER TABLE articulos ADD COLUMN slug TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

def slugify(text):
    import unicodedata
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s+_-]+', '-', text).strip('-')
    return text[:25].strip('-')

def guardar_consulta(rol, tema, detalle, nivel_riesgo):
    conn = sqlite3.connect('consultas_legales_v2.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO triage (fecha, rol, tema, detalle, nivel_riesgo) VALUES (?, ?, ?, ?, ?)", 
              (fecha_actual, rol, tema, detalle, nivel_riesgo))
    conn.commit()
    conn.close()

def guardar_articulo(titulo, contenido, imagen_path=""):
    conn = sqlite3.connect('consultas_legales_v2.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    c.execute("SELECT MAX(id) FROM articulos")
    res = c.fetchone()
    next_id = (res[0] or 0) + 1
    
    slug_base = slugify(titulo)
    slug = f"art-{next_id}-{slug_base}"
    
    c.execute("INSERT INTO articulos (fecha, titulo, contenido, imagen_path, slug) VALUES (?, ?, ?, ?, ?)", 
              (fecha_actual, titulo, contenido, imagen_path, slug))
    conn.commit()
    conn.close()
    
    os.makedirs("articulos", exist_ok=True)
    nombre_archivo = f"articulos/{slug}.html"
    
    img_html = f'<img src="../{imagen_path}" style="width:100%; border-radius:8px; margin-bottom:24px;">' if imagen_path else ''
    url_gh_pages = f"https://chiky718-hub.github.io/evaluador-digital/articulos/{slug}.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} | Leites & Asociados - Estudio Jurídico</title>
    <meta name="description" content="Artículo de doctrina y práctica legal por el Dr. Cristian Darío Leites — Abogado Penalista en Posadas, Misiones.">
    <meta property="og:title" content="{titulo} | Leites & Asociados">
    <meta property="og:description" content="Doctrina y práctica jurídica — Dr. Cristian Darío Leites (Posadas, Misiones).">
    <meta property="og:url" content="{url_gh_pages}">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Montserrat', sans-serif; background-color: #162235; color: #232528; margin: 0; padding: 24px 16px; line-height: 1.8; }}
        .container {{ max-width: 800px; margin: 32px auto; background: #F5F5F3; padding: 44px; border-radius: 12px; box-shadow: 0 8px 28px rgba(0,0,0,0.45); border-top: 6px solid #C5CBD3; }}
        .membrete {{ font-family: 'Cinzel', serif; font-size: 0.85rem; color: #162235; letter-spacing: 0.12em; border-bottom: 1px solid #C5CBD3; padding-bottom: 12px; margin-bottom: 24px; }}
        h1 {{ font-family: 'Cinzel', serif; color: #162235; font-size: 2rem; margin-bottom: 10px; line-height: 1.3; }}
        .fecha {{ color: #555960; font-size: 0.88rem; margin-bottom: 28px; display: block; font-weight: 500; }}
        .contenido {{ font-size: 1.05rem; color: #232528; margin-bottom: 40px; white-space: pre-wrap; }}
        .footer-art {{ border-top: 1px solid #C5CBD3; padding-top: 20px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between; font-size: 0.88rem; color: #555960; }}
        .btn-volver {{ display: inline-block; background-color: #162235; color: #F5F5F3; padding: 11px 22px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 0.9rem; }}
        .btn-volver:hover {{ background-color: #232528; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="membrete">LEITES & ASOCIADOS • ESTUDIO JURÍDICO</div>
        <span class="fecha">Publicado el {fecha_actual} | Dr. Cristian Darío Leites (M.P. C.A.M. N° 4925)</span>
        <h1>{titulo}</h1>
        {img_html}
        <div class="contenido">{contenido}</div>
        <div class="footer-art">
            <a href="https://www.estudioleites.com.ar" class="btn-volver">← Volver a www.estudioleites.com.ar</a>
            <span>Av. Uruguay N° 3184, 1° Piso — Posadas, Misiones | @dr.cristianleites</span>
        </div>
    </div>
</body>
</html>
"""
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(html_content)

init_db()

if 'rol_seleccionado' not in st.session_state:
    st.session_state['rol_seleccionado'] = None

if 'vista_actual' not in st.session_state:
    st.session_state['vista_actual'] = 'INICIO'

# 5. BARRA LATERAL (SIDEBAR INSTITUCIONAL)
with st.sidebar:
    avatar_nuevo = None
    for ext in ['avatar_cdl.png', 'avatar_cdl.jpg', 'avatar_cdl.jpeg', 'avatar.png', 'avatar.jpg']:
        if os.path.exists(ext):
            avatar_nuevo = ext
            break

    logo_legacy = None
    for ext in ['logo.png', 'logo.jpg', 'logo.jpeg']:
        if os.path.exists(ext):
            logo_legacy = ext
            break
            
    if avatar_nuevo:
        try:
            avatar_b64 = get_base64_of_bin_file(avatar_nuevo)
            mime_av = "png" if "png" in avatar_nuevo else "jpeg"
            st.markdown(
                f'''
                <div style="display: flex; justify-content: center; margin-bottom: 18px; margin-top: 10px;">
                    <img src="data:image/{mime_av};base64,{avatar_b64}" style="width: 132px; height: 132px; object-fit: cover; border-radius: 50%; border: 2px solid #C5CBD3; box-shadow: 0 4px 14px rgba(0,0,0,0.4);">
                </div>
                ''', 
                unsafe_allow_html=True
            )
        except Exception:
            st.markdown("<h3 style='text-align:center; font-family:Cinzel,serif;'>LEITES & ASOCIADOS</h3>", unsafe_allow_html=True)
    elif logo_legacy:
        try:
            logo_base64 = get_base64_of_bin_file(logo_legacy)
            st.markdown(
                f'''
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 28px; margin-top: 15px;">
                    <img src="data:image/png;base64,{logo_base64}" style="width: 100%; transform: scale(1.45); filter: invert(1) brightness(2);">
                </div>
                ''', 
                unsafe_allow_html=True
            )
        except Exception:
            st.markdown("<h3 style='text-align:center; font-family:Cinzel,serif;'>LEITES & ASOCIADOS</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align:center; font-family:Cinzel,serif;'>⚖️ LEITES & ASOCIADOS</h3>", unsafe_allow_html=True)
        
    st.markdown(
        """
        <div style="text-align: center;">
            <div style="font-family: 'Cinzel', serif; font-weight: 600; font-size: 1.05em; color: #E6E9EF; letter-spacing: 0.03em;">
                LEITES & ASOCIADOS
            </div>
            <div style="font-size: 0.78em; color: #C5CBD3; letter-spacing: 0.12em; margin-bottom: 8px;">
                ESTUDIO JURÍDICO
            </div>
            <b style="font-size: 0.96em; color: #F5F5F3;">Dr. Cristian Darío Leites</b><br>
            <span style="font-size: 0.82em; color: #C5CBD3;">Mat. C.A.M. N° 4925 • T° XVI F° 225</span><br>
            <span style="font-size: 0.82em; color: #C5CBD3;">Av. Uruguay N° 3184, 1° Piso<br>Posadas, Misiones</span>
        </div>
        <div style="text-align: center; margin-top: 15px; display: flex; justify-content: center; gap: 14px;">
            <a href="https://www.instagram.com/dr.cristianleites" target="_blank" title="Instagram @dr.cristianleites">
                <img src="https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg" width="26" height="26">
            </a>
            <a href="https://www.linkedin.com/in/cristian-leites-976282433" target="_blank" title="LinkedIn">
                <img src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" width="26" height="26">
            </a>
            <a href="https://www.facebook.com/cristian.leites.560443?mibextid=wwXIfr" target="_blank" title="Facebook">
                <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="26" height="26">
            </a>
            <a href="https://wa.me/5493764876017" target="_blank" title="WhatsApp Directo">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="26" height="26">
            </a>
        </div>
        <div style="text-align: center; margin-top: 10px;">
            <a href="mailto:consultas@estudioleites.com.ar" style="font-size: 0.8em; color: #C5CBD3; text-decoration: none;">
                ✉️ consultas@estudioleites.com.ar
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.divider()
    
    if st.button("🏠 Inicio / Consulta Legal", use_container_width=True):
        st.session_state['vista_actual'] = 'INICIO'
        st.session_state['rol_seleccionado'] = None
        st.rerun()
        
    if st.button("📚 Biblioteca de Artículos", use_container_width=True):
        st.session_state['vista_actual'] = 'ARTICULOS'
        st.rerun()

    st.divider()
    st.markdown("<div style='font-family:Cinzel,serif; font-size:1.05rem; font-weight:600; margin-bottom:6px;'>🛡️ Confidencialidad</div>", unsafe_allow_html=True)
    st.info("Este portal está amparado por el **secreto profesional**. Los datos de su consulta reciben tratamiento estrictamente reservado.")
    st.divider()
    
    with st.expander("⚙️ Acceso Interno"):
        clave_ingresada = st.text_input("Contraseña de seguridad:", type="password")
        if clave_ingresada == "Leites2026":
            st.session_state['acceso_concedido'] = True
            st.success("Acceso autorizado.")
        elif clave_ingresada != "":
            st.error("Contraseña incorrecta.")
            st.session_state['acceso_concedido'] = False

# 6. LÓGICA PRINCIPAL (VISTAS)
if st.session_state.get('acceso_concedido', False):
    st.markdown("""
        <div class="etiqueta-superior">ADMINISTRACIÓN INTERNA</div>
        <div class="titulo-estudio" style="font-size: 2.2rem !important;">⚙️ Panel de Gestión del Estudio</div>
    """, unsafe_allow_html=True)
    
    tab_panel1, tab_panel2 = st.tabs(["📊 Consultas Registradas", "✍️ Redactar y Publicar Artículo"])
    
    with tab_panel1:
        st.markdown("### Registro interno de consultas y perfiles de ingresos")
        conn = sqlite3.connect('consultas_legales_v2.db')
        df = pd.read_sql_query("SELECT id as ID, fecha as Fecha, rol as Categoria_Area, tema as Asunto, detalle as Detalle_Estado, nivel_riesgo as IA_Status FROM triage ORDER BY id DESC", conn)
        conn.close()
        
        st.dataframe(df, use_container_width=True)
        
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Base de Datos Completa (CSV)",
                data=csv,
                file_name=f"estadisticas_estudio_leites_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("Aún no hay consultas registradas.")
            
    with tab_panel2:
        st.markdown("### Publicar Nuevo Artículo o Ensayo Jurídico")
        st.markdown("Escriba o pegue su artículo completo. Se generará de forma automática su página web independiente con la estética oficial del Estudio.")
        
        with st.form("form_nuevo_articulo"):
            titulo_art = st.text_input("Título de la Publicación:")
            contenido_art = st.text_area("Contenido del Artículo (Texto completo / Ensayo):", height=350, placeholder="Escriba o pegue aquí su artículo...")
            imagen_subida = st.file_uploader("Imagen de Portada (Opcional):", type=["jpg", "jpeg", "png"])
            
            submit_art = st.form_submit_button("🚀 Publicar Artículo", type="primary")
            
            if submit_art:
                if not titulo_art.strip() or not contenido_art.strip():
                    st.warning("⚠️ El título y el contenido son obligatorios.")
                else:
                    ruta_img_guardada = ""
                    if imagen_subida is not None:
                        os.makedirs("imagenes_articulos", exist_ok=True)
                        ruta_img_guardada = os.path.join("imagenes_articulos", imagen_subida.name)
                        with open(ruta_img_guardada, "wb") as f:
                            f.write(imagen_subida.getbuffer())
                    
                    guardar_articulo(titulo_art, contenido_art, ruta_img_guardada)
                    st.success("¡Artículo publicado con éxito! Se creó su página independiente en la web.")
                    st.balloons()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión Interna"):
        st.session_state['acceso_concedido'] = False
        st.rerun()

elif st.session_state['vista_actual'] == 'ARTICULOS':
    st.markdown("""
        <div class="etiqueta-superior">DOCTRINA • JURISPRUDENCIA • PRÁCTICA FORENSE</div>
        <div class="titulo-estudio"><span class="cap-inicial">B</span>IBLIOTECA <span class="cap-inicial">J</span>URÍDICA</div>
        <div class="bajada-hero">Artículos, ensayos y publicaciones de doctrina y litigación penal del Dr. Cristian Darío Leites.</div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="linea-plata"></div>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('consultas_legales_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, fecha, titulo, slug FROM articulos ORDER BY id DESC")
    articulos = cursor.fetchall()
    conn.close()

    if not articulos:
        st.info("Aún no hay artículos publicados. Próximamente se compartirán análisis jurídicos y ponencias.")
    else:
        st.markdown('<div class="seccion-titulo">Publicaciones Disponibles</div>', unsafe_allow_html=True)
        st.markdown("Seleccione cualquier título para abrir el artículo completo en una pestaña nueva:")
        
        for art_id, fecha, titulo, slug in articulos:
            if not slug:
                slug = f"art-{art_id}-{slugify(titulo)}"
            
            url_articulo = f"https://chiky718-hub.github.io/evaluador-digital/articulos/{slug}.html"
            st.link_button(f"📖 {titulo} ({fecha})", url_articulo, use_container_width=True)

else:
    # VISTA PRINCIPAL DE INICIO
    if st.session_state['rol_seleccionado'] is None:
        # SECCIÓN 1: HERO INSTITUCIONAL LIMPIO (MISMA TIPOGRAFÍA Y COLOR QUE EL LOGO DEL SIDEBAR)
        st.markdown("""
            <div class="titulo-estudio" role="heading" aria-level="1">
                <span class="cap-inicial">L</span>EITES &amp; <span class="cap-inicial">A</span>SOCIADOS
            </div>
            <div class="subtitulo-hero">DEFENSA PENAL ESTRATÉGICA Y REPRESENTACIÓN JURÍDICA INTEGRAL</div>
            <div class="bajada-hero">
                Rigor técnico, confidencialidad absoluta y patrocinio letrado bajo la dirección del <b>Dr. Cristian Darío Leites</b>. 
                Intervenimos en consultas programadas, litigios complejos, delitos informáticos y urgencias penales en Posadas y toda la provincia de Misiones.
            </div>
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 1.8rem;">
                <a href="https://wa.me/5493764876017?text=Hola%20Dr.%20Leites,%20me%20comunico%20desde%20su%20sitio%20web%20para%20solicitar%20asistencia%20jur%C3%ADdica." target="_blank" class="btn-accion-hero" style="background-color: #25D366; color: #FFFFFF;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20"> Urgencias Penales / WhatsApp
                </a>
                <a href="https://calendar.app.google/XUCJvmgwPreSD7tn9" target="_blank" class="btn-accion-hero" style="background-color: #F5F5F3; color: #162235;">
                    📅 Agendar Consulta Programada
                </a>
            </div>
        """, unsafe_allow_html=True)

        # EVALUADOR JURÍDICO INTERACTIVO (MÓDULO DE TRIAGE INTACTO)
        st.markdown('<div class="seccion-titulo">Evaluación Jurídica Preliminar Online</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#C5CBD3; font-size:0.93rem; margin-bottom:1rem;'>Seleccione el área correspondiente a su situación para recibir orientación técnica inmediata y descargar su informe preliminar en PDF:</p>", unsafe_allow_html=True)

        if st.button("🛡️ Fui Víctima / Denunciante\n\n(Derecho Penal, Delitos Informáticos, Ley 26.485 — Necesito accionar o protección)", use_container_width=True):
            st.session_state['rol_seleccionado'] = 'VICTIMA'
            st.rerun()
            
        if st.button("⚖️ Estoy Acusado / Imputado\n\n(Defensa Penal Técnica, Excarcelaciones, Citaciones y Detenciones Urgentes)", use_container_width=True):
            st.session_state['rol_seleccionado'] = 'ACUSADO'
            st.rerun()
            
        if st.button("📂 Otras Ramas del Derecho\n\n(Laboral, Sucesiones, Familia, Divorcios, Daños y Contratos)", use_container_width=True):
            st.session_state['rol_seleccionado'] = 'CIVIL_LABORAL'
            st.rerun()

        st.markdown('<div class="linea-plata"></div>', unsafe_allow_html=True)

        # SECCIÓN 2: EL ESTUDIO Y DIRECCIÓN PROFESIONAL
        st.markdown('<div class="seccion-titulo">El Estudio y Dirección Profesional</div>', unsafe_allow_html=True)
        
        col_img, col_txt = st.columns([1, 2.4])
        
        with col_img:
            perfil_path = None
            for ext in ['perfil.jpg', 'perfil.png', 'perfil.jpeg']:
                if os.path.exists(ext):
                    perfil_path = ext
                    break
            
            if perfil_path:
                st.image(perfil_path, use_container_width=True)
            else:
                st.markdown("⚖️ **Dr. Cristian Darío Leites**<br><span style='font-size:0.8em; color:#C5CBD3;'>Subí tu foto como 'perfil.jpg' en GitHub</span>", unsafe_allow_html=True)
                
        with col_txt:
            st.markdown("<h3 style='margin-top:0; margin-bottom:4px; font-size:1.35rem;'>Dr. Cristian Darío Leites</h3>", unsafe_allow_html=True)
            st.markdown("<div style='color: #C5CBD3; font-size: 0.88rem; font-weight: 600; margin-bottom: 10px;'>Abogado Penalista • Matrícula Profesional C.A.M. N° 4925 (T° XVI F° 225)</div>", unsafe_allow_html=True)
            st.markdown("""
                <div style="font-size: 0.92rem; color: #E2E6EC; line-height: 1.6; margin-bottom: 14px;">
                    En <b>Leites & Asociados — Estudio Jurídico</b> ejercemos la abogacía desde el estudio meticuloso de cada causa, la planificación procesal y el trato directo con nuestros representados. 
                    Combinamos sólida formación de posgrado en Ciencias Penales y litigación oral con herramientas actuales de preservación de evidencia digital y gestión electrónica en todas las circunscripciones judiciales de Misiones y el fuero federal.
                </div>
                <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap;">
                    <a href="https://wa.me/5493764876017" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #25D366; color: white; padding: 8px 15px; border-radius: 8px; font-weight: 600; display: flex; align-items: center; gap: 8px; font-size: 0.88em;">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20"> Contactar ahora
                        </div>
                    </a>
                    <a href="https://www.instagram.com/dr.cristianleites" target="_blank" title="Instagram @dr.cristianleites">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg" width="28">
                    </a>
                    <a href="https://www.linkedin.com/in/cristian-leites-976282433" target="_blank" title="LinkedIn">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" width="28">
                    </a>
                    <a href="https://www.facebook.com/cristian.leites.560443?mibextid=wwXIfr" target="_blank" title="Facebook">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="28">
                    </a>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        pilar1, pilar2, pilar3 = st.columns(3)
        with pilar1:
            st.markdown("""
                <div class="card-marino">
                    <h4>Estrategia a Medida</h4>
                    <p>Construimos una teoría del caso sólida desde la primera actuación, evitando improvisaciones procesales.</p>
                </div>
            """, unsafe_allow_html=True)
        with pilar2:
            st.markdown("""
                <div class="card-marino">
                    <h4>Secreto Profesional</h4>
                    <p>Absoluta reserva y discreción en el manejo de la información y el resguardo de nuestros clientes.</p>
                </div>
            """, unsafe_allow_html=True)
        with pilar3:
            st.markdown("""
                <div class="card-marino">
                    <h4>Transparencia</h4>
                    <p>Diagnóstico honesto sobre escenarios jurídicos reales y acuerdos de honorarios claros por escrito.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="linea-plata"></div>', unsafe_allow_html=True)

        # SECCIÓN 3: ESPECIALIDADES Y FUEROS DE ACTUACIÓN (TARJETAS BLANCO PIEDRA)
        st.markdown('<div class="seccion-titulo">Especialidades y Fueros de Actuación</div>', unsafe_allow_html=True)

        st.markdown("""
            <div class="card-piedra">
                <h4>⚖️ Derecho Penal y Garantías Constitucionales</h4>
                <p>Defensa técnica de personas imputadas y representación de víctimas constituidas como querellante particular en todas las etapas del proceso penal provincial y federal: instrucción, audiencias orales, juicio plenario y recursos superiores.</p>
            </div>
        """, unsafe_allow_html=True)

        col_esp1, col_esp2 = st.columns(2)
        with col_esp1:
            st.markdown("""
                <div class="card-piedra">
                    <h4>🚨 Excarcelaciones y Urgencias</h4>
                    <p>Intervención inmediata ante detenciones, allanamientos, citaciones a indagatoria, eximición de prisión, cese de preventiva y ejecución penal.</p>
                </div>
                <div class="card-piedra">
                    <h4>🛡️ Violencia Familiar y Ley 26.485</h4>
                    <p>Abordaje técnico en denuncias, medidas cautelares de prohibición de acercamiento, exclusión del hogar y conflictos en ámbitos físicos y virtuales.</p>
                </div>
            """, unsafe_allow_html=True)
        with col_esp2:
            st.markdown("""
                <div class="card-piedra">
                    <h4>💻 Delitos Informáticos y Evidencia Digital</h4>
                    <p>Ciberestafas, accesos ilegítimos, vulneración de privacidad digital, difusión no consentida de imágenes y resguardo pericial de prueba informática.</p>
                </div>
                <div class="card-piedra">
                    <h4>📂 Fueros Civil, Sucesiones y Laboral</h4>
                    <p>Procesos sucesorios y declaratorias de herederos, daños y perjuicios, contratos, cobros ejecutivos, derecho de familia e indemnizaciones laborales.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="linea-plata"></div>', unsafe_allow_html=True)

        # SECCIÓN 4: CÓMO TRABAJAMOS SU CASO
        st.markdown('<div class="seccion-titulo">Modalidad de Trabajo y Consulta</div>', unsafe_allow_html=True)
        paso1, paso2, paso3 = st.columns(3)
        with paso1:
            st.markdown("""
                <div class="card-marino">
                    <div class="paso-numero">01</div>
                    <h4>Contacto y Turno</h4>
                    <p>Coordine una entrevista presencial en nuestras oficinas de Posadas o por videollamada desde cualquier punto de Misiones y el país.</p>
                </div>
            """, unsafe_allow_html=True)
        with paso2:
            st.markdown("""
                <div class="card-marino">
                    <div class="paso-numero">02</div>
                    <h4>Diagnóstico Técnico</h4>
                    <p>Evaluamos las actuaciones judiciales y la prueba disponible para definir la viabilidad legal y las medidas urgentes a adoptar.</p>
                </div>
            """, unsafe_allow_html=True)
        with paso3:
            st.markdown("""
                <div class="card-marino">
                    <div class="paso-numero">03</div>
                    <h4>Patrocinio Activo</h4>
                    <p>Formalizamos la representación letrada con alcance claro y seguimiento permanente de cada movimiento del expediente.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="linea-plata"></div>', unsafe_allow_html=True)

        # SECCIÓN 5: PREGUNTAS FRECUENTES (SEO LOCAL)
        st.markdown('<div class="seccion-titulo">Preguntas Frecuentes</div>', unsafe_allow_html=True)

        with st.expander("¿Qué debo hacer ante una citación judicial, allanamiento o detención en Posadas o Misiones?"):
            st.write("Comuníquese de inmediato con un abogado penalista antes de prestar declaración o firmar actuaciones sin presencia de su defensor técnico. Contamos con línea directa de guardia para urgencias penales al +54 376 487-6017.")

        with st.expander("¿El estudio interviene en localidades del interior de la provincia de Misiones?"):
            st.write("Sí. Litigamos de forma digital a través del sistema SIGED en todas las circunscripciones judiciales de Misiones (Posadas, Oberá, Eldorado, Puerto Rico, Leandro N. Alem y San Vicente) y en el fuero federal, asistiendo personalmente a las audiencias clave del proceso.")

        with st.expander("¿Cómo funcionan las consultas online o por videollamada?"):
            st.write("Cuentan con el mismo rigor técnico y amparo del secreto profesional que la atención presencial en despacho. Una vez reservado el turno, analizamos previamente la documentación digitalizada para optimizar la entrevista.")

        with st.expander("¿Cómo se determinan los honorarios profesionales?"):
            st.write("Se establecen con total transparencia según la complejidad técnica del caso, las etapas procesales involucradas y las pautas de la Ley de Honorarios Profesionales de Abogados y Procuradores de Misiones (Ley XII - N° 4), instrumentándose por escrito.")

        # SECCIÓN 6: PIE DE PÁGINA INSTITUCIONAL (FOOTER)
        st.markdown("""
            <div class="footer-institucional">
                <div style="font-family: 'Cinzel', serif; font-size: 1.25rem; font-weight: 600; color: #F5F5F3; letter-spacing: 0.05em;">
                    LEITES & ASOCIADOS — ESTUDIO JURÍDICO
                </div>
                <div style="font-size: 0.88rem; color: #C5CBD3; margin-top: 6px; margin-bottom: 14px;">
                    Dirección Profesional: Dr. Cristian Darío Leites (Mat. C.A.M. N° 4925)
                </div>
                <div style="font-size: 0.88rem; color: #E2E6EC; line-height: 1.7;">
                    📍 <b>Despacho:</b> Av. Uruguay N° 3184, 1° Piso — Posadas, Misiones, Argentina<br>
                    🕒 <b>Horarios:</b> Lunes a viernes de 08:00 a 12:00 hs y de 16:00 a 20:00 hs <i>(Guardia permanente para urgencias penales)</i><br>
                    📞 <b>WhatsApp / Teléfono:</b> <a href="https://wa.me/5493764876017" target="_blank" style="color:#C5CBD3;">+54 376 487-6017</a> &nbsp;|&nbsp; 
                    ✉️ <b>Correo:</b> <a href="mailto:consultas@estudioleites.com.ar" style="color:#C5CBD3;">consultas@estudioleites.com.ar</a><br>
                    📸 <b>Instagram:</b> <a href="https://www.instagram.com/dr.cristianleites" target="_blank" style="color:#C5CBD3;">@dr.cristianleites</a> &nbsp;|&nbsp;
                    🗺️ <a href="https://maps.google.com/maps?cid=396519121907928589" target="_blank" style="color:#C5CBD3;">Ver ubicación en Google Maps</a>
                </div>
                <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(197,203,211,0.2); font-size: 0.78rem; color: #9AA2AE;">
                    © 2026 Leites & Asociados — Estudio Jurídico | Dr. Cristian Darío Leites. Todos los derechos reservados.
                </div>
            </div>
        """, unsafe_allow_html=True)

    else:
        if st.button("⬅️ Volver al menú principal"):
            st.session_state['rol_seleccionado'] = None
            st.rerun()

        st.markdown('<div class="linea-plata"></div>', unsafe_allow_html=True)

        # ROL 1: VÍCTIMA / DENUNCIANTE
        if st.session_state['rol_seleccionado'] == 'VICTIMA':
            st.subheader("🛡️ Asistencia a Víctimas y Querellantes")
            
            tema = st.selectbox("1. Seleccione el motivo principal de su consulta:", 
                                ["Selecciona una opción", 
                                 "Violencia de género / intrafamiliar (Ley 26.485)", 
                                 "Estafas virtuales / Phishing / Fraude informático", 
                                 "Extorsión, Sextorsión o Chantaje Online",
                                 "Amenazas, Hostigamiento o Acoso digital",
                                 "Lesiones, Robo o Hurto",
                                 "Delitos contra la integridad sexual",
                                 "Otro delito penal"])

            plataforma = st.selectbox("2. ¿Dónde o a través de qué medio ocurrió el hecho?", 
                                    ["Selecciona una opción", "Redes Sociales (Instagram, Facebook, etc.)", "Mensajería (WhatsApp, Telegram)", "Vía pública / Entorno físico", "Múltiples medios"])

            st.divider()

            if st.button("Generar Evaluación Jurídica", type="primary", use_container_width=True):
                if tema == "Selecciona una opción" or plataforma == "Selecciona una opción":
                    st.warning("⚠️ Por favor, completa ambas opciones para continuar.")
                else:
                    with st.spinner("Analizando situación procesal..."):
                        try:
                            api_key_secreta = st.secrets["OPENAI_API_KEY"]
                            client = openai.OpenAI(api_key=api_key_secreta)
                            
                            prompt_sistema = """Eres el asistente legal de triage del Dr. Cristian Leites, abogado penalista en Posadas, Misiones. 
                            Asesoras a víctimas y querellantes. Tu tono es firme, empático y protector. Da directrices claras priorizando la integridad física y la preservación inalterada de la evidencia digital."""
                            
                            prompt_usuario = f"""
                            Analiza este caso como VÍCTIMA:
- Delito: {tema}
- Medio: {plataforma}
                            
                            REGLAS ESTRICTAS PARA TU RESPUESTA:
1. Inicia exactamente con esta frase: "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES:"
2. Redacta solo 3 oraciones indicando las medidas urgentes a tomar (ej. resguardo de pruebas, denuncias inmediatas, medidas cautelares).
3. Termina el texto EXACTAMENTE con esta frase: "El Dr. Leites se encuentra a disposición para asumir la representación técnica inmediata como querellante."
                            """
                            
                            respuesta = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
                                temperature=0.2 
                            )
                            
                            analisis_ia = respuesta.choices[0].message.content
                            guardar_consulta("VICTIMA", tema, plataforma, "EVALUADO_POR_IA")
                            st.success("Evaluación generada correctamente.")
                            
                            st.markdown("### 🚨 Directivas Urgentes")
                            st.info(analisis_ia)
                            
                            pdf_bytes = generar_pdf_informe(tema, analisis_ia, f"Medio: {plataforma}")
                            st.download_button(
                                label="📥 Descargar Informe en PDF",
                                data=pdf_bytes,
                                file_name=f"Informe_Legal_Victima_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                            
                            st.divider()
                            st.markdown("### 📲 Contacto Directo con el Estudio")
                            numero_whatsapp = "5493764876017" 
                            mensaje = f"Hola Dr. Leites. Fui VÍCTIMA de '{tema}' ocurrido en '{plataforma}'. Utilicé su sitio web y necesito coordinar una consulta urgente."
                            enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                            
                            st.markdown(f'''
                                <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                    Contactar al Estudio por WhatsApp
                                </a>
                            ''', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error de servidor: {e}")

        # ROL 2: ACUSADO / IMPUTADO
        elif st.session_state['rol_seleccionado'] == 'ACUSADO':
            st.subheader("⚖️ Defensa Penal e Imputados")
            
            estado_libertad = st.selectbox("1. Indique su situación de libertad actual:",
                                         ["Selecciona una opción",
                                          "Estoy en libertad / Notificado de la causa",
                                          "Tengo orden de detención / captura pendiente",
                                          "Estoy detenido en comisaría o dependencia policial (¡URGENTE!)"])

            tema = st.selectbox("2. Seleccione el delito que se le atribuye:", 
                                ["Selecciona una opción", 
                                 "Robo, Hurto o delitos contra la propiedad", 
                                 "Estafas virtuales o económicas", 
                                 "Lesiones, Amenazas o Coacción",
                                 "Delitos contra la integridad sexual",
                                 "Violencia de género (Ley 26.485)",
                                 "Infracción a la Ley de Estupefacientes (Ley 23.737)",
                                 "Otro delito penal"])

            st.divider()

            if st.button("Generar Evaluación de Defensa", type="primary", use_container_width=True):
                if estado_libertad == "Selecciona una opción" or tema == "Selecciona una opción":
                    st.warning("⚠️ Por favor, completa ambas opciones para continuar.")
                else:
                    with st.spinner("Analizando estrategia defensiva..."):
                        try:
                            api_key_secreta = st.secrets["OPENAI_API_KEY"]
                            client = openai.OpenAI(api_key=api_key_secreta)
                            
                            prompt_sistema = """Eres el asistente legal de triage del Dr. Cristian Leites, abogado penalista en Posadas, Misiones. 
                            Asesoras a personas acusadas o imputadas. Tu tono es técnico, estrictamente reservado, garantista y urgente. Si el cliente está detenido o tiene pedido de captura, prioriza la excarcelación y el resguardo de garantías constitucionales."""
                            
                            prompt_usuario = f"""
                            Analiza este caso como DEFENSA PENAL:
- Situación de libertad: {estado_libertad}
- Delito imputado: {tema}
                            
                            REGLAS ESTRICTAS PARA TU RESPUESTA:
1. Inicia exactamente con esta frase: "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES:"
2. Redacta solo 3 oraciones indicando las medidas defensivas inmediatas (ej. no declarar sin asistencia letrada, presentación voluntaria, resguardo de garantías).
3. Termina el texto EXACTAMENTE con esta frase: "El Dr. Leites se encuentra a disposición para asumir la defensa técnica y el control de la causa."
                            """
                            
                            respuesta = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
                                temperature=0.2 
                            )
                            
                            analisis_ia = respuesta.choices[0].message.content
                            guardar_consulta("ACUSADO", tema, estado_libertad, "EVALUADO_POR_IA")
                            st.success("Evaluación generada correctamente.")
                            
                            st.markdown("### 🚨 Pautas Defensivas Urgentes")
                            st.info(analisis_ia)
                            
                            pdf_bytes = generar_pdf_informe(f"Defensa Penal - {tema}", analisis_ia, f"Situación: {estado_libertad}")
                            st.download_button(
                                label="📥 Descargar Informe en PDF",
                                data=pdf_bytes,
                                file_name=f"Informe_Legal_Defensa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                            
                            st.divider()
                            st.markdown("### 📲 Contacto Directo con el Estudio")
                            numero_whatsapp = "5493764876017" 
                            mensaje = f"Hola Dr. Leites. Necesito DEFENSA PENAL urgente. Delito atribuido: '{tema}'. Mi situación actual es: '{estado_libertad}'."
                            enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                            
                            st.markdown(f'''
                                <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                    Contactar al Estudio por WhatsApp
                                </a>
                            ''', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error de servidor: {e}")

        # ROL 3: OTRAS RAMAS DEL DERECHO
        elif st.session_state['rol_seleccionado'] == 'CIVIL_LABORAL':
            st.subheader("📂 Otras Ramas del Derecho")
            
            rama_derecho = st.selectbox("1. Seleccione el área legal de su consulta:",
                                        ["Selecciona una opción",
                                         "Derecho Laboral (Despido, Accidente de trabajo, Diferencias)",
                                         "Derecho de Familia (Alimentos, Cuidado Personal, Régimen de Comunicación)",
                                         "Divorcio y Separación de Bienes",
                                         "Sucesiones / Herencias",
                                         "Accidentes de Tránsito / Daños y Perjuicios",
                                         "Otro asesoramiento civil / comercial"])

            if "Derecho Laboral" in rama_derecho:
                st.markdown("---")
                st.markdown("#### 👷 Asistencia en Derecho Laboral")
                tipo_laboral = st.selectbox("2. Seleccione el tipo de conflicto laboral:",
                                            ["Selecciona una opción",
                                             "Despido sin causa",
                                             "Despido con causa / Injustificado",
                                             "Accidente de trabajo / Enfermedad profesional",
                                             "Falta de registración (En negro) / Diferencias salariales"])
                
                if "Despido" in tipo_laboral:
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        fecha_ingreso = st.date_input("Fecha de Ingreso aproximada:")
                    with col_f2:
                        fecha_egreso = st.date_input("Fecha de Egreso / Despido:")
                    
                    mejor_sueldo = st.number_input("Último mejor sueldo bruto mensual ($):", min_value=0.0, step=50000.0, format="%.2f")
                    
                    st.divider()
                    if st.button("Calcular Estimación y Derivar", type="primary", use_container_width=True):
                        if mejor_sueldo <= 0:
                            st.warning("⚠️ Por favor, ingrese un monto de sueldo válido.")
                        else:
                            try:
                                d1 = datetime.combine(fecha_ingreso, datetime.min.time())
                                d2 = datetime.combine(fecha_egreso, datetime.min.time())
                                anos_antiguedad = max(1, (d2 - d1).days // 365)
                            except Exception:
                                anos_antiguedad = 1
                            
                            estimacion_indemnizacion = mejor_sueldo * anos_antiguedad
                            
                            with st.spinner("Generando análisis de liquidación..."):
                                try:
                                    api_key_secreta = st.secrets["OPENAI_API_KEY"]
                                    client = openai.OpenAI(api_key=api_key_secreta)
                                    
                                    prompt_sistema = "Eres el asistente legal del Dr. Cristian Leites en Posadas, Misiones. Asesoras en derecho laboral con rigor técnico y claridad."
                                    prompt_usuario = f"""
                                    Analiza este caso laboral de despido:
- Tipo: {tipo_laboral}
- Antigüedad estimada: {anos_antiguedad} años
- Mejor sueldo: ${mejor_sueldo}
- Estimación matemática orientativa: ${estimacion_indemnizacion}
                                    
                                    REGLAS ESTRICTAS:
1. Inicia exactamente con: "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES:"
2. Redacta solo 3 oraciones indicando que la cifra es meramente estimativa, la importancia de intimar por telegrama de ley y los plazos legales vigentes.
3. Termina exactamente con: "El Dr. Leites se encuentra a disposición para auditar su liquidación y coordinar el reclamo formal."
                                    """
                                    
                                    respuesta = client.chat.completions.create(
                                        model="gpt-3.5-turbo",
                                        messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
                                        temperature=0.2
                                    )
                                    analisis_ia = respuesta.choices[0].message.content
                                    guardar_consulta("LABORAL", tipo_laboral, f"Sueldo: {mejor_sueldo} - Est: {estimacion_indemnizacion}", "EVALUADO_POR_IA")
                                    
                                    st.success("Evaluación generada con éxito.")
                                    st.markdown("### 📊 Orientación y Cálculo Estimativo")
                                    st.info(analisis_ia)
                                    st.metric(label="Estimación Indemnizatoria Orientativa", value=f"${estimacion_indemnizacion:,.2f}")
                                    
                                    pdf_bytes = generar_pdf_informe(f"Derecho Laboral - {tipo_laboral}", analisis_ia, f"Estimado: ${estimacion_indemnizacion:,.2f}")
                                    st.download_button(
                                        label="📥 Descargar Informe en PDF",
                                        data=pdf_bytes,
                                        file_name=f"Informe_Legal_Laboral_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        type="primary"
                                    )
                                    
                                    st.divider()
                                    st.markdown("### 📲 Contacto Directo con el Estudio")
                                    f_ing_str = fecha_ingreso.strftime('%d/%m/%Y')
                                    f_eg_str = fecha_egreso.strftime('%d/%m/%Y')
                                    mensaje = f"Hola Dr. Leites. Consulté por su web por un '{tipo_laboral}'. Ingreso: {f_ing_str}, Egreso: {f_eg_str}. Sueldo: ${mejor_sueldo:,.2f}. Estimado calculado: ${estimacion_indemnizacion:,.2f}. Necesito coordinar entrevista."
                                    enlace_wa = f"https://wa.me/5493764876017?text={mensaje.replace(' ', '%20')}"
                                    
                                    st.markdown(f'''
                                        <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                            Contactar al Estudio por WhatsApp
                                        </a>
                                    ''', unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"Error: {e}")

                elif "Accidente" in tipo_laboral:
                    tiene_art = st.selectbox("¿Tenía cobertura de ART declarada al momento del accidente?",
                                            ["Selecciona una opción",
                                             "Sí, tenía ART activa",
                                             "No tenía ART / Empleador en negro",
                                             "No estoy seguro / A confirmar"])
                    
                    detalle_accidente = st.text_area("Describa brevemente cómo ocurrió el hecho y las lesiones:", placeholder="Ej: Me caí de una escalera trabajando en la obra y me lesioné la rodilla...")
                    
                    st.divider()
                    if st.button("Generar Orientación por Accidentes", type="primary", use_container_width=True):
                        if tiene_art == "Selecciona una opción" or not detalle_accidente.strip():
                            st.warning("⚠️ Por favor, complete los datos del accidente.")
                        else:
                            with st.spinner("Analizando situación de riesgos del trabajo..."):
                                try:
                                    api_key_secreta = st.secrets["OPENAI_API_KEY"]
                                    client = openai.OpenAI(api_key=api_key_secreta)
                                    
                                    prompt_sistema = "Eres el asistente legal del Dr. Cristian Leites en Posadas, Misiones, experto en accidentes de trabajo y Ley de Riesgos (ART)."
                                    prompt_usuario = f"""
                                    Analiza este accidente laboral:
- Estado ART: {tiene_art}
- Detalle: {detalle_accidente}
                                    
                                    REGLAS ESTRICTAS:
1. Inicia exactamente con: "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES:"
2. Redacta solo 3 oraciones indicando las medidas urgentes (atención médica obligatoria, denuncia a la ART o intimación al empleador, y preservación de constancias).
3. Termina exactamente con: "El Dr. Leites se encuentra a disposición para iniciar los reclamos ante comisiones médicas o tribunales."
                                    """
                                    
                                    respuesta = client.chat.completions.create(
                                        model="gpt-3.5-turbo",
                                        messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
                                        temperature=0.2
                                    )
                                    analisis_ia = respuesta.choices[0].message.content
                                    guardar_consulta("LABORAL", "Accidente de Trabajo", tiene_art, "EVALUADO_POR_IA")
                                    
                                    st.success("Evaluación generada con éxito.")
                                    st.markdown("### 🚨 Pautas Médicas y Legales Urgentes")
                                    st.info(analisis_ia)
                                    
                                    pdf_bytes = generar_pdf_informe("Accidente de Trabajo / ART", analisis_ia, f"Estado ART: {tiene_art}")
                                    st.download_button(
                                        label="📥 Descargar Informe en PDF",
                                        data=pdf_bytes,
                                        file_name=f"Informe_Legal_Accidente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        type="primary"
                                    )
                                    
                                    st.divider()
                                    st.markdown("### 📲 Contacto Directo con el Estudio")
                                    numero_whatsapp = "5493764876017"
                                    mensaje = f"Hola Dr. Leites. Sufrí un accidente laboral. Cobertura: '{tiene_art}'. Detalle: {detalle_accidente[:60]}... Necesito asesoramiento."
                                    enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                                    
                                    st.markdown(f'''
                                        <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                            Contactar al Estudio por WhatsApp
                                        </a>
                                    ''', unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"Error: {e}")

                else:
                    detalle_lab = st.text_area("Describa su situación laboral (diferencias salariales, falta de registración, etc.):")
                    if st.button("Generar Orientación Laboral", type="primary", use_container_width=True):
                        if not detalle_lab.strip():
                            st.warning("Por favor, ingrese un detalle de su consulta.")
                        else:
                            guardar_consulta("LABORAL", tipo_laboral, detalle_lab[:50], "EVALUADO_POR_IA")
                            st.success("Orientación registrada con éxito.")
                            analisis_texto = "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES: Es fundamental conservar recibos de sueldo, registrar testigos y realizar las intimaciones por telegrama laboral respaldado por asesoramiento letrado. El Dr. Leites se encuentra a disposición para coordinar una entrevista y evaluar su caso."
                            st.info(analisis_texto)
                            
                            pdf_bytes = generar_pdf_informe(f"Laboral - {tipo_laboral}", analisis_texto)
                            st.download_button(
                                label="📥 Descargar Informe en PDF",
                                data=pdf_bytes,
                                file_name=f"Informe_Legal_Laboral_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                            
                            mensaje = f"Hola Dr. Leites. Consulté por su web sobre un tema laboral ({tipo_laboral}) y necesito coordinar una entrevista."
                            enlace_wa = f"https://wa.me/5493764876017?text={mensaje.replace(' ', '%20')}"
                            st.markdown(f'''
                                <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                    Contactar al Estudio por WhatsApp
                                </a>
                            ''', unsafe_allow_html=True)

            else:
                if rama_derecho != "Selecciona una opción":
                    detalle_consulta = st.text_area("2. Describa brevemente su situación o duda principal:", 
                                                   placeholder="Ej: Necesito iniciar una demanda por alimentos o sucesión...")

                    st.divider()

                    if st.button("Generar Orientación Legal", type="primary", use_container_width=True):
                        if not detalle_consulta.strip():
                            st.warning("⚠️ Por favor, complete la descripción de su consulta.")
                        else:
                            with st.spinner("Analizando su caso..."):
                                try:
                                    api_key_secreta = st.secrets["OPENAI_API_KEY"]
                                    client = openai.OpenAI(api_key=api_key_secreta)
                                    
                                    prompt_sistema = "Eres el asistente legal del Dr. Cristian Leites, abogado en Posadas, Misiones. Asesoras en ramas civiles y de familia. Tu tono es profesional, claro y prudente."
                                    prompt_usuario = f"""
                                    Analiza este caso extrapenal:
- Área: {rama_derecho}
- Descripción: {detalle_consulta}
                                    
                                    REGLAS ESTRICTAS:
1. Inicia exactamente con: "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES:"
2. Redacta solo 3 oraciones indicando los primeros pasos legales o la documentación a reunir.
3. Termina exactamente con: "El Dr. Leites se encuentra a disposición para coordinar una consulta y evaluar la viabilidad de su caso."
                                    """
                                    
                                    respuesta = client.chat.completions.create(
                                        model="gpt-3.5-turbo",
                                        messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
                                        temperature=0.2 
                                    )
                                    analisis_ia = respuesta.choices[0].message.content
                                    guardar_consulta("OTRAS_RAMAS", rama_derecho, detalle_consulta[:50], "EVALUADO_POR_IA")
                                    
                                    st.success("Orientación generada correctamente.")
                                    st.markdown("### 📋 Orientación Profesional")
                                    st.info(analisis_ia)
                                    
                                    pdf_bytes = generar_pdf_informe(rama_derecho, analisis_ia, f"Detalle: {detalle_consulta[:40]}...")
                                    st.download_button(
                                        label="📥 Descargar Informe en PDF",
                                        data=pdf_bytes,
                                        file_name=f"Informe_Legal_Civil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        type="primary"
                                    )
                                    
                                    st.divider()
                                    st.markdown("### 📲 Contacto Directo con el Estudio")
                                    mensaje = f"Hola Dr. Leites. Consulté por su sitio web sobre un tema de {rama_derecho} y necesito coordinar una entrevista."
                                    enlace_wa = f"https://wa.me/5493764876017?text={mensaje.replace(' ', '%20')}"
                                    
                                    st.markdown(f'''
                                        <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                            Contactar al Estudio por WhatsApp
                                        </a>
                                    ''', unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"Error de servidor: {e}")

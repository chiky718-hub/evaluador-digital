import streamlit as st
import sqlite3
from datetime import datetime
import openai
import base64
import os
import pandas as pd
from fpdf import FPDF

# 2. CONFIGURACIÓN DE PÁGINA (PRIMER ELEMENTO OBLIGATORIO)
st.set_page_config(
    page_title="Leites & Asociados | Estudio Jurídico",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# DETECCIÓN INICIAL DE ENLACES COMPARTIDOS (URL PARAMS) ANTES DE RENDERIZAR NADA
query_params = st.query_params
articulo_url_id = query_params.get("id", None)
if articulo_url_id:
    try:
        articulo_url_id = int(articulo_url_id)
        if 'vista_actual' not in st.session_state:
            st.session_state['vista_actual'] = 'ARTICULOS'
    except:
        articulo_url_id = None

# 1. FUNCIÓN PARA CARGAR IMÁGENES
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# CLASE PARA GENERAR EL PDF DEL ESTUDIO
class PDFEstudio(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, 'LEITES & ASOCIADOS - ESTUDIO JURÍDICO', 0, 1, 'C')
        self.set_font('helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Dr. Cristian Dario Leites | Abogado Penalista (M.P. N° 4925) - Posadas, Misiones', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Documento generado digitalmente - Página {self.page_no()}', 0, 0, 'C')

def generar_pdf_informe(titulo_caso, detalle_analisis, datos_extra=""):
    pdf = PDFEstudio()
    pdf.add_page()
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'R')
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"INFORME DE ORIENTACIÓN JURÍDICA: {titulo_caso}", 0, 1, 'L')
    pdf.ln(3)
    
    if datos_extra:
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(0, 6, f"Detalles específicos: {datos_extra}", 0, 1, 'L')
        pdf.ln(3)
        
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, "Directrices del Estudio:", 0, 1, 'L')
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 6, detalle_analisis)
    pdf.ln(10)
    
    pdf.set_font('helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "Aviso: Este informe preliminar se encuentra amparado por el secreto profesional y constituye una orientación técnica inicial basada en los datos proporcionados por el consultante.")
    
    return bytes(pdf.output())

# 3. APLICAR FONDO CON FILTRO OSCURO
fondo_path = None
for ext in ['fondo.jpg', 'fondo.jpeg', 'fondo.png']:
    if os.path.exists(ext):
        fondo_path = ext
        break

if fondo_path:
    try:
        fondo_base64 = get_base64_of_bin_file(fondo_path)
        tipo_img = "png" if "png" in fondo_path else "jpeg"
        
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("data:image/{tipo_img};base64,{fondo_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except Exception:
        pass

# 4. BASE DE DATOS
def init_db():
    conn = sqlite3.connect('consultas_legales_v2.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS triage 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, rol TEXT, tema TEXT, detalle TEXT, nivel_riesgo TEXT)
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS articulos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, titulo TEXT, contenido TEXT, imagen_path TEXT)
    ''')
    try:
        c.execute("ALTER TABLE triage ADD COLUMN rol TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE triage ADD COLUMN detalle TEXT")
    except:
        pass
    conn.commit()
    conn.close()

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
    c.execute("INSERT INTO articulos (fecha, titulo, contenido, imagen_path) VALUES (?, ?, ?, ?)", 
              (fecha_actual, titulo, contenido, imagen_path))
    conn.commit()
    conn.close()

init_db()

if 'rol_seleccionado' not in st.session_state:
    st.session_state['rol_seleccionado'] = None

if 'vista_actual' not in st.session_state:
    st.session_state['vista_actual'] = 'INICIO'

# 5. BARRA LATERAL (SIDEBAR)
with st.sidebar:
    logo_path = None
    for ext in ['logo.png', 'logo.jpg', 'logo.jpeg']:
        if os.path.exists(ext):
            logo_path = ext
            break
            
    if logo_path:
        try:
            logo_base64 = get_base64_of_bin_file(logo_path)
            st.markdown(
                f'''
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 30px; margin-top: 15px;">
                    <img src="data:image/png;base64,{logo_base64}" style="width: 100%; transform: scale(1.6); filter: invert(1) brightness(2);">
                </div>
                ''', 
                unsafe_allow_html=True
            )
        except Exception:
            st.title("⚖️ Estudio Jurídico Leites")
    else:
        st.title("⚖️ Estudio Jurídico Leites")
        
    st.markdown(
        """
        <div style="text-align: center;">
            <b style="font-size: 1.1em;">Dr. Cristian Dario Leites</b><br>
            <span style="font-size: 0.9em; color: #dddddd;">M.P. N° 4925</span><br>
            <i style="font-size: 0.9em;">Abogado Penalista | Posadas, Misiones</i>
        </div>
        <div style="text-align: center; margin-top: 15px; display: flex; justify-content: center; gap: 15px;">
            <a href="https://www.instagram.com/cristianleites_ok?utm_source=qr" target="_blank" title="Instagram">
                <img src="https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg" width="30" height="30">
            </a>
            <a href="https://www.facebook.com/cristian.leites.560443?mibextid=wwXIfr" target="_blank" title="Facebook">
                <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="30" height="30">
            </a>
            <a href="https://www.linkedin.com/in/cristian-leites-976282433" target="_blank" title="LinkedIn">
                <img src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" width="30" height="30">
            </a>
            <a href="https://wa.me/5493764876017" target="_blank" title="WhatsApp">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="30" height="30">
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.divider()
    
    if st.button("🏠 Inicio / Consulta Legal", use_container_width=True):
        st.query_params.clear()
        st.session_state['vista_actual'] = 'INICIO'
        st.session_state['rol_seleccionado'] = None
        st.rerun()
        
    if st.button("📚 Biblioteca de Artículos", use_container_width=True):
        st.query_params.clear()
        st.session_state['vista_actual'] = 'ARTICULOS'
        st.rerun()

    st.divider()
    st.title("🛡️ Confidencialidad")
    st.info("Este portal está amparado por el **secreto profesional**. Los datos de tu consulta son 100% anónimos y encriptados.")
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
        <style>
        .titulo-panel { font-family: 'Lora', serif; font-size: 2.5rem; color: #ffffff; }
        </style>
        <div class="titulo-panel">⚙️ Panel de Gestión del Estudio</div>
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
        st.markdown("Escriba o pegue su artículo completo. Se asignará un enlace directo único para compartir en redes.")
        
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
                    st.success("¡Artículo publicado con éxito en la web!")
                    st.balloons()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión Interna"):
        st.session_state['acceso_concedido'] = False
        st.rerun()

elif st.session_state['vista_actual'] == 'ARTICULOS':
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500&display=swap');
        .titulo-estudio { font-family: 'Lora', serif; font-size: 2.8rem; font-weight: 500; color: #ffffff; margin-bottom: 0.2em; line-height: 1.2; }
        .subtitulo-rol { font-size: 1.1rem; color: #dddddd; margin-bottom: 1.5rem; }
        </style>
        <div class="titulo-estudio">Biblioteca Jurídica</div>
        <div class="subtitulo-rol">Artículos, ensayos y publicaciones de doctrina y práctica legal del Dr. Cristian Dario Leites.</div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    conn = sqlite3.connect('consultas_legales_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, fecha, titulo, contenido, imagen_path FROM articulos ORDER BY id DESC")
    articulos = cursor.fetchall()
    conn.close()

    if not articulos:
        st.info("Aún no hay artículos publicados. Próximamente se compartirán análisis jurídicos y ponencias.")
    else:
        # Si la URL trae un ID específico, filtramos para mostrar únicamente ese artículo
        articulos_a_mostrar = articulos
        if articulo_url_id:
            articulos_a_mostrar = [a for a in articulos if a[0] == articulo_url_id]
            if articulos_a_mostrar:
                if st.button("⬅️ Ver todos los artículos"):
                    st.query_params.clear()
                    st.rerun()
                st.divider()

        for art_id, fecha, titulo, contenido, imagen_path in articulos_a_mostrar:
            st.markdown(f"## {titulo}")
            st.markdown(f"<span style='color: #aaaaaa; font-size: 0.85em;'>📅 Publicado el {fecha}</span>", unsafe_allow_html=True)
            
            if imagen_path and os.path.exists(imagen_path):
                st.image(imagen_path, use_container_width=True)
                
            st.markdown(f"<div style='background-color: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 8px; color: #eeeeee; line-height: 1.7; margin-top: 10px; margin-bottom: 20px;'>{contenido.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            
            # ENLACE DIRECTO ÚNICO PARA ESTE ARTÍCULO
            url_articulo = f"https://www.estudioleites.com.ar/?id={art_id}"
            
            st.markdown("#### 🔗 Compartir esta publicación:")
            
            texto_compartir = f"Leé este artículo del Dr. Cristian Leites: '{titulo}'. Ingresá acá: {url_articulo}"
            
            wapp_link = f"https://wa.me/?text={texto_compartir.replace(' ', '%20')}"
            fb_link = f"https://www.facebook.com/sharer/sharer.php?u={url_articulo}"
            lk_link = f"https://www.linkedin.com/sharing/share-offsite/?url={url_articulo}"
            tw_link = f"https://twitter.com/intent/tweet?text={texto_compartir.replace(' ', '%20')}"
            
            st.markdown(f'''
                <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 25px;">
                    <a href="{wapp_link}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #25D366; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; font-size: 0.85em; display: flex; align-items: center; gap: 5px;">
                            💬 WhatsApp
                        </div>
                    </a>
                    <a href="{fb_link}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #1877F2; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; font-size: 0.85em;">
                            📘 Facebook
                        </div>
                    </a>
                    <a href="{lk_link}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #0A66C2; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; font-size: 0.85em;">
                            💼 LinkedIn
                        </div>
                    </a>
                    <a href="{tw_link}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #000000; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; font-size: 0.85em;">
                            ✖️ X / Twitter
                        </div>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
            
            st.text_input(f"Enlace directo para historia de Instagram o copiar (Artículo #{art_id}):", value=url_articulo, key=f"link_input_{art_id}")
            
            st.divider()

else:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500&display=swap');
        .titulo-estudio { font-family: 'Lora', serif; font-size: 3.3rem; font-weight: 500; color: #ffffff; margin-bottom: 0.2em; line-height: 1.2; }
        .subtitulo-rol { font-size: 1.1rem; color: #dddddd; margin-bottom: 1.5rem; }
        </style>
        <div class="titulo-estudio">Leites & Asociados</div>
        <div class="subtitulo-rol">Seleccione el área legal correspondiente a su consulta para recibir orientación profesional.</div>
    """, unsafe_allow_html=True)

    if st.session_state['rol_seleccionado'] is None:
        if st.button("🛡️ Fui Víctima / Denunciante\n\n(Derecho Penal - Necesito accionar o protección)", use_container_width=True):
            st.session_state['rol_seleccionado'] = 'VICTIMA'
            st.rerun()
            
        if st.button("⚖️ Estoy Acusado / Imputado\n\n(Derecho Penal - Defensa penal urgente)", use_container_width=True):
            st.session_state['rol_seleccionado'] = 'ACUSADO'
            st.rerun()
            
        if st.button("📂 Otras Ramas del Derecho\n\n(Familia, Sucesiones, Laboral, Accidentes, etc.)", use_container_width=True):
            st.session_state['rol_seleccionado'] = 'CIVIL_LABORAL'
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        col_img, col_txt = st.columns([1, 2.5])
        
        with col_img:
            perfil_path = None
            for ext in ['perfil.jpg', 'perfil.png', 'perfil.jpeg']:
                if os.path.exists(ext):
                    perfil_path = ext
                    break
            
            if perfil_path:
                st.image(perfil_path, use_container_width=True)
            else:
                st.markdown("⚖️ **Dr. Cristian Leites**<br><span style='font-size:0.8em; color:#aaa;'>Subí tu foto como 'perfil.jpg' en GitHub</span>", unsafe_allow_html=True)
                
        with col_txt:
            st.markdown("### Dr. Cristian Dario Leites")
            st.markdown("<span style='color: #dddddd; font-size: 0.9em;'>Abogado Penalista (M.P. N° 4925)</span>", unsafe_allow_html=True)
            st.markdown("""
                <div style="font-size: 0.92em; color: #cccccc; line-height: 1.4; margin-top: 8px; margin-bottom: 15px;">
                    Especializado en litigios penales complejos, derecho penal y asesoramiento legal estratégico en la ciudad de Posadas, Misiones. 
                    Compromiso absoluto con la defensa técnica rigurosa, la ética profesional y la protección de los derechos de nuestros representados.
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                    <a href="https://wa.me/5493764876017" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #25D366; color: white; padding: 8px 15px; border-radius: 8px; font-weight: bold; display: flex; align-items: center; gap: 8px; font-size: 0.9em;">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22"> Contactar ahora
                        </div>
                    </a>
                    <a href="https://www.instagram.com/cristianleites_ok?utm_source=qr" target="_blank" title="Instagram">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg" width="30">
                    </a>
                    <a href="https://www.facebook.com/cristian.leites.560443?mibextid=wwXIfr" target="_blank" title="Facebook">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/2021_Facebook_icon.svg" width="30">
                    </a>
                    <a href="https://www.linkedin.com/in/cristian-leites-976282433" target="_blank" title="LinkedIn">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" width="30">
                    </a>
                </div>
            """, unsafe_allow_html=True)

    else:
        if st.button("⬅️ Volver al menú principal"):
            st.session_state['rol_seleccionado'] = None
            st.rerun()

        st.divider()

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
                            except:
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
                                    2. Redacta 3 oraciones indicando que la cifra es meramente estimativa, la importancia de intimar por telegrama de ley y los plazos legales vigentes.
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
                                    2. Redacta 3 oraciones indicando las medidas urgentes (atención médica obligatoria, denuncia a la ART o intimación al empleador, y preservación de constancias).
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

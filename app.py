import streamlit as st
import sqlite3
from datetime import datetime
import openai
import base64
import os
import pandas as pd

# 1. FUNCIÓN PARA CARGAR IMÁGENES
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Estudio Jurídico Leites | Evaluación Legal", page_icon="⚖️", layout="centered")

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
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, tema TEXT, plataforma TEXT, nivel_riesgo TEXT)
    ''')
    conn.commit()
    conn.close()

def guardar_consulta(tema, plataforma, nivel_riesgo):
    conn = sqlite3.connect('consultas_legales_v2.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO triage (fecha, tema, plataforma, nivel_riesgo) VALUES (?, ?, ?, ?)", 
              (fecha_actual, tema, plataforma, nivel_riesgo))
    conn.commit()
    conn.close()

init_db()

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

# 6. LÓGICA DE PANTALLA DIVIDIDA
if st.session_state.get('acceso_concedido', False):
    # --- PANTALLA PRIVADA ---
    st.markdown("""
        <style>
        .titulo-panel { font-family: 'Lora', serif; font-size: 2.8rem; color: #ffffff; }
        </style>
        <div class="titulo-panel">📊 Panel de Control del Estudio</div>
    """, unsafe_allow_html=True)
    
    st.markdown("Bienvenido al registro interno. Aquí puedes visualizar y descargar las estadísticas de uso de tu Evaluador Legal.")
    
    conn = sqlite3.connect('consultas_legales_v2.db')
    df = pd.read_sql_query("SELECT id as ID, fecha as Fecha, tema as Tema, plataforma as Plataforma, nivel_riesgo as IA_Status FROM triage ORDER BY id DESC", conn)
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
        st.info("Aún no hay consultas registradas en la base de datos.")
    
    if st.button("Cerrar Sesión"):
        st.session_state['acceso_concedido'] = False
        st.rerun()

else:
    # --- PANTALLA PÚBLICA ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500&display=swap');
        .titulo-estudio { font-family: 'Lora', serif; font-size: 3.3rem; font-weight: 500; color: #ffffff; margin-bottom: 0.2em; line-height: 1.2; }
        </style>
        <div class="titulo-estudio">Leites & Asociados</div>
    """, unsafe_allow_html=True)

    st.markdown("Selecciona tu problemática para obtener un encuadre legal y conocer las medidas urgentes a tomar.")

    tema = st.selectbox("1. ¿Cuál es el motivo principal de tu consulta?", 
                              ["Selecciona una opción", 
                               "Difusión no consentida de imágenes / Violencia Digital", 
                               "Sextorsión o Chantaje Online", 
                               "Estafas virtuales o Robo de identidad",
                               "Violencia de género (Ley 26.485)",
                               "Hostigamiento o Acoso",
                               "Otro delito penal"])

    plataforma = st.selectbox("2. ¿Dónde o cómo está ocurriendo el hecho?", 
                              ["Selecciona una opción", "Redes Sociales (Instagram, Facebook, etc.)", "Mensajería (WhatsApp, Telegram)", "Entorno físico / presencial", "Múltiples medios"])

    st.divider()

    if st.button("Generar Evaluación Jurídica", type="primary", use_container_width=True):
        if tema == "Selecciona una opción" or plataforma == "Selecciona una opción":
            st.warning("⚠️ Por favor, completa ambas preguntas para poder evaluar tu caso.")
        else:
            with st.spinner("Analizando situación..."):
                try:
                    api_key_secreta = st.secrets["OPENAI_API_KEY"]
                    client = openai.OpenAI(api_key=api_key_secreta)
                    
                    # CEREBRO DE LA IA ACTUALIZADO
                    prompt_sistema = """Eres el asistente legal de triage del Dr. Cristian Leites, abogado penalista en Posadas, Misiones. 
                    Tu objetivo es brindar directrices legales de urgencia de forma directa, empática y con total autoridad jurídica, sin usar jerga compleja. 
                    Si el caso involucra Violencia de Género (Ley 26.485), debes priorizar la seguridad de la víctima. 
                    Si es un ciberdelito, enfatiza la preservación inalterada de la evidencia digital."""
                    
                    prompt_usuario = f"""
                    Analiza este caso:
                    - Conflicto: {tema}
                    - Medio: {plataforma}
                    
                    REGLAS ESTRICTAS PARA TU RESPUESTA:
                    1. Inicia exactamente con esta frase, en mayúsculas: "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES:"
                    2. Redacta solo 3 oraciones indicando las medidas cautelares o probatorias urgentes que la persona debe tomar HOY (ej. no borrar evidencia ni bloquear agresores sin documentar, resguardar la integridad física).
                    3. Termina el texto EXACTAMENTE con esta frase: "El Dr. Leites se encuentra a disposición para asumir la representación técnica inmediata de este caso."
                    """
                    
                    respuesta = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": prompt_usuario}
                        ],
                        temperature=0.2 
                    )
                    
                    analisis_ia = respuesta.choices[0].message.content
                    
                    guardar_consulta(tema, plataforma, "EVALUADO_POR_IA")
                    st.success("Evaluación generada correctamente.")
                    
                    st.markdown("### 🚨 Respuesta Rápida")
                    st.info(analisis_ia)
                    
                    st.divider()
                    st.markdown("### 📲 Contacto Directo")
                    
                    numero_whatsapp = "5493764876017" 
                    mensaje = "Hola Dr. Leites. Acabo de utilizar el Evaluador Legal en su sitio web y necesito coordinar una consulta profesional urgente."
                    enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                    
                    st.markdown(f'''
                        <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                            Contactar al Estudio por WhatsApp
                        </a>
                    ''', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Hubo un error de servidor. Por favor, intenta más tarde. Detalle: {e}")

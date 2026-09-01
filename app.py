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
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, rol TEXT, tema TEXT, detalle TEXT, nivel_riesgo TEXT)
    ''')
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

init_db()

# Inicializar estados de navegación si no existen
if 'rol_seleccionado' not in st.session_state:
    st.session_state['rol_seleccionado'] = None

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

# 6. LÓGICA PRINCIPAL (PANEL DE CONTROL vs PANTALLA PÚBLICA)
if st.session_state.get('acceso_concedido', False):
    # --- PANTALLA PRIVADA (ADMIN) ---
    st.markdown("""
        <style>
        .titulo-panel { font-family: 'Lora', serif; font-size: 2.8rem; color: #ffffff; }
        </style>
        <div class="titulo-panel">📊 Panel de Control del Estudio</div>
    """, unsafe_allow_html=True)
    
    st.markdown("Registro interno de consultas y perfiles de ingresos.")
    
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
    
    if st.button("Cerrar Sesión"):
        st.session_state['acceso_concedido'] = False
        st.rerun()

else:
    # --- PANTALLA PÚBLICA ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500&display=swap');
        .titulo-estudio { font-family: 'Lora', serif; font-size: 3.3rem; font-weight: 500; color: #ffffff; margin-bottom: 0.2em; line-height: 1.2; }
        .subtitulo-rol { font-size: 1.1rem; color: #dddddd; margin-bottom: 1.5rem; }
        </style>
        <div class="titulo-estudio">Leites & Asociados</div>
        <div class="subtitulo-rol">Seleccione el área legal correspondiente a su consulta para recibir orientación profesional.</div>
    """, unsafe_allow_html=True)

    # PASO 1: SELECCIÓN DE ÁREA / ROL (TRES BOTONES)
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

    else:
        # BOTÓN PARA VOLVER ATRÁS
        if st.button("⬅️ Volver al menú principal"):
            st.session_state['rol_seleccionado'] = None
            st.rerun()

        st.divider()

        # ROL 1: VÍCTIMA / DENUNCIANTE (PENAL)
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
                            
                            st.divider()
                            st.markdown("### 📲 Contacto Directo con el Estudio")
                            numero_whatsapp = "5493764876017" 
                            mensaje = "Hola Dr. Leites. Soy víctima de un hecho delictivo, utilicé su sitio web y necesito coordinar una consulta profesional urgente."
                            enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                            
                            st.markdown(f'''
                                <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                    Contactar al Estudio por WhatsApp
                                </a>
                            ''', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error de servidor: {e}")

        # ROL 2: ACUSADO / IMPUTADO (PENAL)
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
                                 "Estafas o delitos económicos / informáticos", 
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
                            Asesoras a personas acusadas o imputadas. Tu tono es técnico, estrictamente reservado, garantista y urgente. Si el cliente está detenido o tiene pedido de captura, prioriza la excarcelación y el resguardo de derechos constitucionales."""
                            
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
                            
                            st.divider()
                            st.markdown("### 📲 Contacto Directo con el Estudio")
                            numero_whatsapp = "5493764876017" 
                            mensaje = "Hola Dr. Leites. Necesito asistencia y defensa penal urgente, utilicé su sitio web."
                            enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                            
                            st.markdown(f'''
                                <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                    Contactar al Estudio por WhatsApp
                                </a>
                            ''', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error de servidor: {e}")

        # ROL 3: OTRAS RAMAS DEL DERECHO (FAMILIA, SUCESIONES, LABORAL, ACCIDENTES)
        elif st.session_state['rol_seleccionado'] == 'CIVIL_LABORAL':
            st.subheader("📂 Otras Ramas del Derecho")
            
            rama_derecho = st.selectbox("1. Seleccione el área legal de su consulta:",
                                        ["Selecciona una opción",
                                         "Derecho de Familia (Alimentos, Cuidado Personal, Régimen de Comunicación)",
                                         "Divorcio y Separación de Bienes",
                                         "Sucesiones / Herencias",
                                         "Accidentes de Tránsito / Daños y Perjuicios",
                                         "Derecho Laboral (Despido, Accidente de trabajo, Diferencias salariales)",
                                         "Otro asesoramiento civil / comercial"])

            detalle_consulta = st.text_area("2. Describa brevemente su situación o duda principal:", 
                                              placeholder="Ej: Necesito iniciar una demanda por alimentos o fui despedido sin causa...")

            st.divider()

            if st.button("Generar Orientación Legal", type="primary", use_container_width=True):
                if rama_derecho == "Selecciona una opción" or not detalle_consulta.strip():
                    st.warning("⚠️ Por favor, seleccione el área y complete la descripción de su consulta.")
                else:
                    with st.spinner("Analizando su caso..."):
                        try:
                            api_key_secreta = st.secrets["OPENAI_API_KEY"]
                            client = openai.OpenAI(api_key=api_key_secreta)
                            
                            prompt_sistema = """Eres el asistente legal del Dr. Cristian Leites, abogado en Posadas, Misiones. 
                            Asesoras en ramas extrapenales (Familia, Laboral, Civil, Sucesiones). Tu tono es profesional, claro, ordenado y prudente, brindando una orientación inicial general."""
                            
                            prompt_usuario = f"""
                            Analiza este caso extrapenal:
                            - Área: {rama_derecho}
                            - Descripción: {detalle_consulta}
                            
                            REGLAS ESTRICTAS PARA TU RESPUESTA:
                            1. Inicia exactamente con esta frase: "SEGUN EL ANÁLISIS DEL DR. CRISTIAN LEITES:"
                            2. Redacta solo 3 oraciones indicando los primeros pasos legales o la documentación a reunir.
                            3. Termina el texto EXACTAMENTE con esta frase: "El Dr. Leites se encuentra a disposición para coordinar una consulta y evaluar la viabilidad de su caso."
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
                            
                            st.divider()
                            st.markdown("### 📲 Contacto Directo con el Estudio")
                            numero_whatsapp = "5493764876017" 
                            mensaje = "Hola Dr. Leites. Consulté por su sitio web sobre un tema de " + rama_derecho + " y necesito coordinar una entrevista."
                            enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                            
                            st.markdown(f'''
                                <a href="{enlace_wa}" target="_blank" style="display: block; background-color: #25D366; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
                                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="22" style="vertical-align: middle; margin-right: 8px;"> 
                                    Contactar al Estudio por WhatsApp
                                </a>
                            ''', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error de servidor: {e}")

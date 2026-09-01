import streamlit as st
import sqlite3
from datetime import datetime
import openai
import base64
import os

# 1. FUNCIÓN PARA CARGAR IMÁGENES DE FONDO DE FORMA SEGURA
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Estudio Jurídico Leites | Evaluación Legal", page_icon="⚖️", layout="centered")

# 3. APLICAR FONDO CON FILTRO OSCURO (ALTO CONTRASTE)
if os.path.exists('fondo.jpeg'):
    try:
        fondo_base64 = get_base64_of_bin_file('fondo.jpeg')
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("data:image/jpeg;base64,{fondo_base64}");
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

# 5. BARRA LATERAL (SIDEBAR) CON LECTURA DE BYTES (MÁXIMA SEGURIDAD)
with st.sidebar:
    # Buscamos el logo sin importar si quedó guardado como png, jpg o jpeg
    logo_path = None
    for ext in ['logo.png', 'logo.jpg', 'logo.jpeg']:
        if os.path.exists(ext):
            logo_path = ext
            break
            
    if logo_path:
        try:
            # Leemos la imagen como datos crudos para que no haya errores de formato
            with open(logo_path, 'rb') as f:
                st.image(f.read(), use_container_width=True)
        except Exception:
            st.title("⚖️ Estudio Jurídico Leites")
    else:
        st.title("⚖️ Estudio Jurídico Leites")
        
    st.markdown("**Dr. Cristian Dario Leites**")
    st.markdown("*Abogado Penalista | Posadas, Misiones*")
    st.divider()
    st.title("🛡️ Confidencialidad")
    st.info("Este portal está amparado por el **secreto profesional**. Los datos de tu consulta son 100% anónimos y encriptados.")
    st.divider()
    st.markdown("### ¿Emergencia inminente?")
    st.error("Ante violencia física o peligro de vida actual, comunícate de inmediato a la línea **144** o al **911**.")

# 6. INTERFAZ PRINCIPAL
st.title("Evaluación Jurídica Preliminar")
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
                
                prompt_sistema = "Eres el asistente legal del Dr. Cristian Leites. Habla de forma directa, sencilla y coloquial para que cualquier persona te entienda sin jerga legal. Tu respuesta debe ser extremadamente breve."
                prompt_usuario = f"""
                Analiza este caso:
                - Conflicto: {tema}
                - Medio: {plataforma}
                
                REGLAS ESTRICTAS PARA TU RESPUESTA:
                1. Empieza el texto EXACTAMENTE con esta frase, en mayúsculas: "SEGUN EL DR. CRISTIAN LEITES,"
                2. Luego, escribe solo 2 o 3 oraciones simples explicando qué hacer de inmediato (por ejemplo: no borrar evidencia, hacer capturas de pantalla, hacer la denuncia). 
                3. Termina el texto EXACTAMENTE con esta frase: "el Dr. Cristian Leites se encuentra con disponibilidad para tomar el caso."
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

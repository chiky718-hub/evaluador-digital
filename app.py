import streamlit as st
import sqlite3
from datetime import datetime
import openai

# 1. CONFIGURACIÓN DE PÁGINA Y BRANDING
st.set_page_config(page_title="Estudio Jurídico Leites | Evaluación Legal", page_icon="⚖️", layout="centered")

# 2. BASE DE DATOS
def init_db():
    conn = sqlite3.connect('consultas_legales.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS triage 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, tema TEXT, plataforma TEXT, nivel_riesgo TEXT)
    ''')
    conn.commit()
    conn.close()

def guardar_consulta(tema, plataforma, nivel_riesgo):
    conn = sqlite3.connect('consultas_legales.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO triage (fecha, tema, plataforma, nivel_riesgo) VALUES (?, ?, ?, ?)", 
              (fecha_actual, tema, plataforma, nivel_riesgo))
    conn.commit()
    conn.close()

init_db()

# 3. BARRA LATERAL (SIDEBAR) - IDENTIDAD PROFESIONAL
with st.sidebar:
    st.title("⚖️ Estudio Jurídico Leites")
    st.markdown("**Dr. Cristian Dario Leites**")
    st.markdown("*Abogado Penalista | Posadas, Misiones*")
    
    st.divider()
    
    st.title("🛡️ Confidencialidad")
    st.info("Este portal está amparado por el **secreto profesional**. Los datos de tu consulta son 100% anónimos y encriptados.")
    
    st.divider()
    st.markdown("### ¿Emergencia inminente?")
    st.error("Ante violencia física o peligro de vida actual, comunícate de inmediato a la línea **144** o al **911**.")

# 4. INTERFAZ PRINCIPAL - CUESTIONARIO AMPLIADO
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

# Botón principal de acción
if st.button("Generar Evaluación Jurídica", type="primary", use_container_width=True):
    
    if tema == "Selecciona una opción" or plataforma == "Selecciona una opción":
        st.warning("⚠️ Por favor, completa ambas preguntas para poder evaluar tu caso.")
    else:
        with st.spinner("Analizando marco legal y doctrina aplicable..."):
            try:
                # Conexión con OpenAI
                api_key_secreta = st.secrets["OPENAI_API_KEY"]
                client = openai.OpenAI(api_key=api_key_secreta)
                
                prompt_sistema = "Eres el asistente legal de inteligencia artificial del Estudio Jurídico del Dr. Cristian Leites, abogado penalista. Eres experto en derecho penal argentino, cibercrimen y normativas de género. Tu tono es serio, protector, resolutivo y altamente profesional."
                prompt_usuario = f"""
                Redacta un dictamen preliminar breve (máximo 2 párrafos) y 3 pasos de acción legales inmediatos para un cliente con esta situación:
                - Conflicto: {tema}
                - Medio: {plataforma}
                
                Termina indicando que el Dr. Leites está a disposición para asumir la querella, defensa o solicitar medidas cautelares urgentes según corresponda. Usa negritas para destacar términos jurídicos.
                """
                
                respuesta = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    temperature=0.3 
                )
                
                analisis_ia = respuesta.choices[0].message.content
                
                guardar_consulta(tema, plataforma, "EVALUADO_POR_IA")
                
                st.success("Evaluación generada correctamente.")
                
                st.markdown("### 🚨 Dictamen Preliminar")
                st.info(analisis_ia)
                
                st.divider()
                
                st.markdown("### 📲 Asesoramiento Legal Urgente")
                st.markdown("Para iniciar acciones legales, frenar el daño o coordinar una entrevista presencial, comunicate ahora mismo:")
                
                # --- CONFIGURACIÓN DE WHATSAPP ---
                # Reemplazá los ceros por tu número real, incluyendo el 549376 de Posadas. 
                # Ejemplo: "5493764123456"
                numero_whatsapp = "5493764876017" 
                
                mensaje = "Hola Dr. Leites. Acabo de utilizar el Evaluador Legal en su sitio web y necesito coordinar una consulta profesional urgente."
                enlace_wa = f"https://wa.me/{numero_whatsapp}?text={mensaje.replace(' ', '%20')}"
                
                st.link_button("💬 Enviar WhatsApp al Estudio", enlace_wa, type="primary", use_container_width=True)
                
            except Exception as e:
                st.error(f"Hubo un error de servidor. Por favor, intenta más tarde. Detalle: {e}")

import streamlit as st
import sqlite3
from datetime import datetime
import openai

# 1. CONFIGURACIÓN DE LA PÁGINA Y DISEÑO VISUAL
st.set_page_config(page_title="Evaluador de Riesgo Digital", page_icon="⚖️", layout="centered")

# 2. CONEXIÓN A BASE DE DATOS SQLITE
def init_db():
    conn = sqlite3.connect('consultas_legales.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS triage 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, plataforma TEXT, consentimiento TEXT, nivel_riesgo TEXT)
    ''')
    conn.commit()
    conn.close()

def guardar_consulta(plataforma, consentimiento, nivel_riesgo):
    conn = sqlite3.connect('consultas_legales.db')
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO triage (fecha, plataforma, consentimiento, nivel_riesgo) VALUES (?, ?, ?, ?)", 
              (fecha_actual, plataforma, consentimiento, nivel_riesgo))
    conn.commit()
    conn.close()

init_db()

# 3. BARRA LATERAL (SIDEBAR) LIMPIA Y PROFESIONAL
with st.sidebar:
    st.title("🛡️ Información Importante")
    st.info("**Privacidad garantizada:** Este formulario es 100% anónimo. No guardamos tu IP, nombre ni datos de contacto.")
    st.divider()
    st.markdown("### ¿Estás en peligro inminente?")
    st.error("Si sufres violencia física o amenazas de muerte, comunícate inmediatamente a la línea **144** o al **911**.")

# 4. INTERFAZ PRINCIPAL (CUESTIONARIO)
st.title("Evaluador de Riesgo: Violencia Digital")
st.markdown("Responde estas breves preguntas para conocer tu situación legal y los pasos a seguir ante la difusión no consentida de imágenes.")

plataforma = st.selectbox("1. ¿Dónde se está difundiendo el contenido?", 
                          ["Selecciona una opción", "Instagram / Facebook", "WhatsApp / Telegram", "Páginas web / Foros", "Otro"])

consentimiento = st.radio("2. ¿Hubo consentimiento previo para la captura de esa imagen/video?", 
                          ["Selecciona una opción", "Sí, pero NO para difundirlo", "No, fue grabado sin mi permiso", "Es material editado/falso (Deepfake)"])

st.divider()

# Botón principal de acción, amplio y destacado
if st.button("Evaluar mi situación legal", type="primary", use_container_width=True):
    
    if plataforma == "Selecciona una opción" or consentimiento == "Selecciona una opción":
        st.warning("⚠️ Por favor, completa todas las preguntas para obtener una evaluación.")
    else:
        # Spinner visual mientras la IA procesa la consulta
        with st.spinner("Analizando jurisprudencia y encuadre penal..."):
            try:
                # Conexión con OpenAI utilizando la clave interna y segura de Streamlit Secrets
                api_key_secreta = st.secrets["OPENAI_API_KEY"]
                client = openai.OpenAI(api_key=api_key_secreta)
                
                prompt_sistema = "Eres un abogado penalista argentino experto en cibercrimen y la Ley 26.485 (Protección Integral a las Mujeres). Tu tono es profesional, empático y urgente."
                prompt_usuario = f"""
                Analiza el siguiente caso de vulneración de privacidad digital:
                - Plataforma de difusión: {plataforma}
                - Contexto de la obtención del material: {consentimiento}
                
                Redacta un breve análisis de riesgo legal (máximo 2 párrafos) y 3 pasos de acción inmediatos para la víctima.
                Utiliza negritas para resaltar conceptos clave. No uses formatos de código ni introducciones genéricas.
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
                
                # Registrar en la base de datos local
                guardar_consulta(plataforma, consentimiento, "EVALUADO_POR_IA")
                
                st.success("Evaluación completada con éxito.")
                
                # Mostrar el análisis redactado por la IA
                st.markdown("### 🚨 Análisis de Riesgo Legal Detallado")
                st.info(analisis_ia)
                
                st.divider()
                st.markdown("### ¿Necesitas frenar esto ahora?")
                
                # Link a tu Google Calendar
                enlace_reservas = "https://calendar.google.com/" 
                st.link_button("📅 Agendar Consulta Profesional Urgente", enlace_reservas, type="primary", use_container_width=True)
                
            except Exception as e:
                st.error(f"Hubo un error de configuración en el servidor. Por favor, intenta más tarde. Detalle: {e}")

# ============================================
# src/app.py - INTERFAZ GRÁFICA CON STREAMLIT
# ============================================

import streamlit as st
import os
import sys
from pathlib import Path

# Añadir el directorio actual al path para importar agente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar el agente (tu código de agente.py)
from agente import preguntar, todos_los_documentos, fragmentos, get_stats

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="🏥 Agente IA - Clínica Salud+",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO (MEJORA LA APARIENCIA)
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-radius: 10px;
        padding: 1rem;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-radius: 10px;
        padding: 1rem;
    }
    .metric-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    .sidebar-section {
        margin-top: 2rem;
        padding: 1rem;
        background-color: #F0F2F6;
        border-radius: 10px;
    }
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #eee;
    }
    .example-question {
        background-color: #E8F5E9;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        cursor: pointer;
        margin: 0.3rem 0;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        border: 1px solid #C8E6C9;
    }
    .example-question:hover {
        background-color: #C8E6C9;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO Y DESCRIPCIÓN
# ============================================
st.markdown('<p class="main-header">🏥 Asistente IA - Clínica Salud+</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Tu base de conocimiento inteligente sobre políticas, procedimientos y servicios</p>', unsafe_allow_html=True)

# ============================================
# SIDEBAR - INFORMACIÓN Y ESTADÍSTICAS
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/hospital.png", width=80)
    st.markdown("### 📊 Estado del Sistema")
    
    # Métricas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📄 Documentos", len(todos_los_documentos) if todos_los_documentos else 0)
    with col2:
        st.metric("📝 Fragmentos", len(fragmentos) if fragmentos else 0)
    
    st.markdown("---")
    
    st.markdown("### 📂 Dominios Cubiertos")
    dominios = [
        "🏥 Atención al paciente",
        "💰 Finanzas",
        "👥 Recursos Humanos",
        "⚕️ Operaciones",
        "📋 Calidad",
        "⚖️ Legal",
        "📢 Comunicaciones"
    ]
    for dominio in dominios:
        st.markdown(f"- {dominio}")
    
    st.markdown("---")
    
    st.markdown("### 💡 Preguntas de Ejemplo")
    st.markdown("*(Haz clic para probar)*")
    
    # Preguntas de ejemplo (al hacer clic, se envía al chat)
    preguntas_ejemplo = [
        "¿Cómo puedo agendar una cita médica?",
        "¿Cuántos días de vacaciones tengo?",
        "¿Cuál fue la utilidad de diciembre?",
        "¿Cuánto cuesta una resonancia magnética?",
        "¿Qué dice el contrato con EPS SaludTotal?",
        "¿Cuáles son los tiempos de triaje en urgencias?",
        "¿Qué beneficios tienen los empleados?"
    ]
    
    for p in preguntas_ejemplo:
        if st.button(f"📌 {p}", key=p, use_container_width=True):
            # Al hacer clic, guardar en session_state para procesar
            st.session_state.ejemplo_pregunta = p
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📞 Contacto")
    st.markdown("""
    **Soporte:**  
    📞 (+57) 601 234 5678  
    📧 soporte@saludmas.com  
    🌐 www.saludmas.com
    """)
    
    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.8rem; color: #999; text-align: center;'>
    ⚡ Desarrollado con LangChain + Gemini<br>
    © 2026 Clínica Salud+ - Challenge Alura Agente
    </div>
    """, unsafe_allow_html=True)

# ============================================
# INICIALIZAR ESTADO DE LA SESIÓN
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy el asistente virtual de Clínica Salud+. Estoy aquí para ayudarte con información sobre políticas, procedimientos, finanzas y servicios de la clínica. ¿En qué puedo ayudarte hoy?"}
    ]

# Procesar pregunta de ejemplo (si existe)
if "ejemplo_pregunta" in st.session_state and st.session_state.ejemplo_pregunta:
    prompt_ejemplo = st.session_state.ejemplo_pregunta
    st.session_state.ejemplo_pregunta = None  # Limpiar para no repetir
    
    # Agregar la pregunta al chat
    st.session_state.messages.append({"role": "user", "content": prompt_ejemplo})
    
    # Generar respuesta
    with st.spinner("🔍 Buscando en los documentos..."):
        # try:
        respuesta = preguntar(prompt_ejemplo)
        # Si la respuesta es una lista, unirla
        if isinstance(respuesta, list):
            respuesta = " ".join(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        # except Exception as e:
        #     st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
    
    st.rerun()

# ============================================
# MOSTRAR HISTORIAL DE CHAT
# ============================================
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**👤 Tú:** {message['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(f"**🤖 Agente:** {message['content']}")

# ============================================
# INPUT DEL USUARIO
# ============================================
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Mostrar pregunta del usuario
    with st.chat_message("user"):
        st.markdown(f"**👤 Tú:** {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🔍 Consultando la base de conocimiento..."):
            # try:
            respuesta = preguntar(prompt)
            # Si la respuesta es una lista, unirla
            if isinstance(respuesta, list):
                respuesta = " ".join(respuesta)
            st.markdown(f"**🤖 Agente:** {respuesta}")
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            # except Exception as e:
            #     mensaje_error = f"❌ Ocurrió un error: {str(e)}"
            #     st.markdown(f"**🤖 Agente:** {mensaje_error}")
            #     st.session_state.messages.append({"role": "assistant", "content": mensaje_error})

# ============================================
# FOOTER
# ============================================
st.markdown('<div class="footer">🏥 Clínica Salud+ - Asistente Virtual con IA | Challenge Alura Agente</div>', unsafe_allow_html=True)
#  Clínica Salud+ - Asistente Virtual con IA

<div align="center">

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C6C?style=for-the-badge&logo=langchain&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-886FBF?style=for-the-badge&logo=googlegemini&logoColor=white)
![Deployed](https://img.shields.io/badge/Deployed%20on-Streamlit%20Cloud-FF4B4B?style=for-the-badge)

**Un asistente inteligente tipo RAG (Retrieval-Augmented Generation) para responder preguntas sobre políticas, procedimientos y servicios de la Clínica Salud+.**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://alura-agente-deckard-debug.streamlit.app)

</div>

---

##  Descripción General

Este proyecto consiste en un **agente de inteligencia artificial** diseñado para funcionar como una base de conocimiento conversacional para la **Clínica Salud+**. El sistema permite a colaboradores, pacientes y personal administrativo realizar preguntas en lenguaje natural y obtener respuestas precisas basadas en documentos internos de la organización.

###  Propósito
- **Centralizar** la información dispersa en múltiples documentos
- **Facilitar** el acceso a políticas, procedimientos y datos clave
- **Reducir** el tiempo de búsqueda de información
- **Automatizar** respuestas a preguntas frecuentes

## Notas Importantes

### Tiempo de Carga
- La aplicación puede tardar **aproximadamente 30 segundos** en cargar completamente durante el primer acceso.
- Esto se debe a que el sistema está:
  1. Cargando los documentos desde la carpeta `data/`
  2. Generando los embeddings con Gemini
  3. Construyendo la base de datos vectorial ChromaDB
- Las cargas posteriores serán más rápidas gracias al caché interno.
---

##  Características Principales

| Característica | Descripción |
|----------------|-------------|
| **RAG Inteligente** | Combina búsqueda vectorial con generación de lenguaje natural |
| **Múltiples Formatos** | Soporta PDF, CSV, TXT, Excel, Markdown y JSON |
| **7 Dominios** | Atención, Finanzas, RRHH, Operaciones, Calidad, Legal, Comunicaciones |
| **Chat Interactivo** | Interfaz web con historial de conversación |
| **Respuestas Precisas** | Basadas exclusivamente en el contexto recuperado |
| **Tiempo Real** | Procesamiento rápido con Gemini 3.6 Flash |
| **Accesible** | Desplegado en la nube con URL pública |
| **Carga Inicial** | La primera carga puede tomar ~30 segundos mientras se indexan los documento |

---

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| **Python 3.12+** | Lenguaje de programación |
| **LangChain** | Framework para orquestar el agente RAG |
| **Google Gemini** | LLM y embeddings (gratuito) |
| **ChromaDB** | Base de datos vectorial |
| **Streamlit** | Interfaz web |
| **PyPDF, Pandas** | Lectura de documentos |

## Instalación y Ejecución
``` batch
# 1. Clonar el repositorio
git clone <git@github.com:deckard-debug/ALURA_AGENT.git>
cd alura-agente

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crea un archivo .env en la raíz con:
GOOGLE_API_KEY=tu_api_key_aqui

# 5. Agregar documentos
Coloca tus documentos (PDF, CSV, TXT, EXCEL, MD, JSON) en la carpeta data/

# 6. Ejecutar el agente
cd src
streamlit run app.py

# 7. Abrir en el navegador
http://localhost:8501
```
## Ejemplos de Preguntas y Respuestas

| # | Pregunta | Respuesta del Agente | Dominio |
|---|----------|---------------------|---------|
| 1 | "¿Cómo puedo agendar una cita médica?" | "Puedes agendar tu cita a través de línea telefónica (+57 601 234 5678), plataforma web (www.saludmas.com/agendar), aplicación móvil Salud+ o en ventanilla de atención." | 🏥 Atención |
| 2 | "¿Cuántos días de vacaciones tengo?" | "Según las políticas generales, tienes 15 días hábiles de vacaciones al año después del primer año de trabajo." | 👥 RRHH |
| 3 | "¿Cuál fue la utilidad de diciembre?" | "Según los datos financieros, la utilidad de diciembre fue de $29,000,000 COP con ingresos de $70,000,000 y gastos de $41,000,000." | 💰 Finanzas |
| 4 | "¿Cuánto cuesta una resonancia magnética?" | "El precio para particular es de $650,000 COP y para EPS es de $520,000 COP con un tiempo estimado de 60 minutos." | 📈 Comercial |
| 5 | "¿Qué dice el contrato con EPS SaludTotal?" | "El contrato CS-2026-001 establece cobertura del 100% en consultas, 80% en cirugías y 90% en exámenes, con tarifas preferenciales." | ⚖️ Legal |

## Despliegue en la Nube
Streamlit Community Cloud
El agente está desplegado en Streamlit Community Cloud, una plataforma gratuita que no requiere tarjeta de crédito.

URL de acceso: https://alura-agente-deckard-debug.streamlit.app

## Capturas de Pantalla
### Aplicación en funcionamiento
<img width="1913" height="1031" alt="image" src="https://github.com/user-attachments/assets/c6c99fc8-76a5-4893-a63e-67e5c96b940f" />


## Mejoras Futuras
* Soporte para Word y PowerPoint
* Memoria conversacional
* Autenticación de usuarios
* Exportar respuestas a PDF
* Dashboard de análisis de preguntas frecuentes

##  Licencia
Este proyecto fue desarrollado como parte del Challenge Alura Agente - ONE AI FOR TECH.

## Autor
[DEIKERT GONZALEZ] - [deckard-debug]

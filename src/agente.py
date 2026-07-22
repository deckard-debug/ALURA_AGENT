# 1 importar librerias 
import os
import pandas as pd
import json
import re
import time
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from pathlib import Path

# 2 Crear Variables de Entorno
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# if (GOOGLE_API_KEY):
#     print("ta cargada la api causita")
# else:
#     print("no se encontro la variables de entorno")


# 3 Cargar documentos

def cargar_documentos(ruta: str):
    """
    Carga documento en multiples formatos:
    - PDF: usa PyPDF
    - CSV: usa pandas
    - TXT: lectura simple
    - Word: python-do
    - Excel: pandas
    - JSON: carga como texto
    - MD: carga como texto
    """
    global RDocuments
    documentos = []
    ruta = Path(ruta)

    formatdoc = ruta.suffix.lower()

    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró: {ruta}")

    # Cargar PDF
    if formatdoc == '.pdf':
        lector = PdfReader(str(ruta))
        for i, pagina in enumerate(lector.pages):
            texto = pagina.extract_text()
            if texto.strip():
                documentos.append(Document(
                    page_content=texto, 
                    metadata={"source": str(ruta), "page": i, "format": "PDF"}))
        print(f"Paginas del documento {formatdoc}: {len(documentos)}")

    # Cargar CSV
    elif formatdoc == '.csv':
        df = pd.read_csv(ruta)
        for i, row in df.iterrows():
            texto = " | ".join([f"{col}: {row[col]}" for col in df.columns])
            documentos.append(Document(
                    page_content=texto, 
                    metadata={"source": str(ruta), "page": i, "format": "CSV"}))
        print(f"Paginas del documento {formatdoc}: {len(documentos)}")

    # Cargar TXT
    elif formatdoc == '.txt':
        with open(ruta, "r", encoding="utf-8") as formato:
            texto = formato.read()
            fragmentos = texto.split("\n\n")
            for i, fragmento in enumerate(fragmentos):
                if fragmento.strip():
                    documentos.append(Document(
                        page_content=fragmento, 
                        metadata={"source": str(ruta), "page": i, "format": "TXT"}))
            print(f"Paginas del documento {formatdoc}: {len(documentos)}")

     # Cargar MD
    elif formatdoc == '.md':
        with open(ruta, "r", encoding="utf-8") as formato:
            texto = formato.read()
            fragmentos_md = re.split(r'\n##\s', texto)
            for i, fragmento in enumerate(fragmentos_md):
                if fragmento.strip():
                    if i == 0:
                        titulo = "Introducción"
                        contenido = fragmento
                    else:
                        lineas = fragmento.split('\n', 1)
                        titulo = lineas[0].strip() if lineas else "Sección"
                        contenido = lineas[1] if len(lineas) > 1 else ""

                    texto_completo = f"{titulo}: {contenido}"
                    documentos.append(Document(
                        page_content=texto_completo, 
                        metadata={"source": str(ruta), "page": i, "format": "MD"}))
            print(f"Paginas del documento {formatdoc}: {len(documentos)}")

    # Cargar JSON
    elif formatdoc == '.json':
        try:
            with open(ruta, "r", encoding="utf-8") as formato:

                datos = json.load(formato)

                if isinstance(datos, list):

                    for i, item in enumerate(datos):
                        if isinstance(item, dict):

                            texto = " | ".join([f"{k}: {v}" for k, v in item.items()])
                            documentos.append(Document(
                                page_content=texto,
                                metadata={"source": str(ruta), "index": i, "format": "JSON"}
                            ))

                    print(f"Paginas del documento {formatdoc}: {len(documentos)}")

                elif isinstance(datos, dict):

                    texto = " | ".join([f"{k}: {v}" for k, v in datos.items()])
                    documentos.append(Document(
                        page_content=texto,
                        metadata={"source": str(ruta), "format": "JSON"}
                    ))

                    print(f" JSON cargado: 1 elemento")
                
        except Exception:
            print(f"ERROR AL LEER JSON {ruta.name}: {Exception}")

    # Cargar EXCEL
    elif formatdoc in ['.xlsx','xls']:
        df = pd.read_excel(ruta)
        for i, row in df.iterrows():
            texto = " | ".join([f"{col}: {row[col]}" for col in df.columns])
            documentos.append(Document(
                    page_content=texto, 
                    metadata={"source": str(ruta), "page": i, "format": "EXCEL"}))
        print(f"Paginas del documento {formatdoc}: {len(documentos)}")

    else:
        raise ValueError(f"formato no soportado: {ruta.suffix}")

    return documentos

# Obtener la ruta del directorio donde está este archivo (src/)
DIRECTORIO_ACTUAL = Path(__file__).parent.resolve()
# Ruta a la carpeta data (un nivel arriba de src)
ruta_documento = DIRECTORIO_ACTUAL.parent / "data"


todos_los_documentos = []

if ruta_documento.exists():
# Cargar TODOS los documentos en la carpeta data/
    for archivo in Path(ruta_documento).iterdir():
        if archivo.suffix.lower() in ['.pdf', '.csv', '.txt', '.xlsx', '.xls', '.md', '.json']:
            print(f" Cargando: {archivo.name}")
        try:
            docs = cargar_documentos(str(archivo))
            todos_los_documentos.extend(docs)

            print(f"\n TOTAL: {len(todos_los_documentos)} documentos cargados")

        except Exception as e:
            print(f" Error: {e}")
            exit(1)

# 4 Dividir en Fragmentos para que la IA tenga informacion relevante
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n","\n","."," ",""]
)
fragmentos = text_splitter.split_documents(todos_los_documentos)

# 5 EMBEDDINGS y Base de Datos Vectorial
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)

vectorstore = None
if fragmentos:
    # Reducido a 15 fragmentos por lote para respetar los límites Rpm del modelo de embedding
    chunk_size_embedding = 15 
    print(f"Vectorizando {len(fragmentos)} fragmentos...")
    for i in range(0, len(fragmentos), chunk_size_embedding):
        batch = fragmentos[i:i + chunk_size_embedding]
        if vectorstore is None:
            vectorstore = Chroma.from_documents(documents=batch, embedding=embeddings)
        else:
            vectorstore.add_documents(batch)
        print(f"Procesado lote {i // chunk_size_embedding + 1} de {-(len(fragmentos) // -chunk_size_embedding)}")
        time.sleep(4)  # Esperar 4 segundos entre solicitudes para liberar cuota


# 6 Agente RAG
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key = GOOGLE_API_KEY,
    # temperature = 0.3
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) if vectorstore else None
system_prompt = (
    """
        Eres un asistente virtual experto de la CLÍNICA SALUD+, una organización de salud 
        comprometida con la excelencia en la atención al paciente.

        🎯 **TU ROL:**
        - Responde preguntas de colaboradores, pacientes y personal administrativo.
        - Actúas como una base de conocimiento centralizada de la organización.
        - Debes ser claro, profesional y empático en tus respuestas.

        📋 **INSTRUCCIONES ESTRICTAS:**
        1. Responde ÚNICAMENTE basándote en el CONTEXTO proporcionado.
        2. Si es una pregunta y NO está en el contexto, di:
        "No tengo esa información en mi base de datos. Por favor, contacta a nuestro equipo de soporte al (+57) 601 234 5678 o envía un correo a soporte@saludmas.com"
        3. NO inventes información, NO des consejos médicos no respaldados.
        4. SI la pregunta es sobre síntomas o diagnósticos, recomienda consultar con un médico.
        5. SI la pregunta es sobre datos financieros, sé preciso con los números.
        6. SI la pregunta es sobre políticas de RH, menciona la fuente.
        7. Organiza tu respuesta en párrafos claros y concisos.
        8. SI la pregunta tiene múltiples partes, responde cada una de forma estructurada.

        📚 **CONTEXTO RECUPERADO (USA SOLO ESTO):**
        {context}

        👤 **PREGUNTA DEL USUARIO:**
        {input}

        🤖 **RESPUESTA (basada ÚNICAMENTE en el contexto):**
    """
)
prompt = ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        ("human", "{input}"),
    ])

if retriever:
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    qa_chain = create_retrieval_chain(retriever, combine_docs_chain)
else:
    qa_chain = None

# ============================================
# 7. FUNCIÓN PARA PREGUNTAR
# ============================================

def preguntar(pregunta: str) -> str:
    """
    Función principal que procesa la consulta del usuario en la interfaz.
    """

    if not qa_chain:
        return "El sistema no está inicializado porque no se encontraron documentos válidos en la carpeta data."

    try:
        respuesta = qa_chain.invoke({"input": pregunta})
        respuesta_final = respuesta.get("answer", "respuesta invalida")
        limpiar_respuesta = re.sub(r'\*=','', respuesta_final)

        return limpiar_respuesta.strip()
    
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================
# 9. FUNCIÓN PARA OBTENER ESTADÍSTICAS
# ============================================

def get_stats():
    """
    Retorna un diccionario con estadísticas de procesamiento.
    """
    return {
        "total_documentos": len(todos_los_documentos),
        "total_fragmentos": len(fragmentos),
        }
    
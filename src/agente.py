# 1 importar librerias 
import os
import pandas as pd
import json
import re
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
                        page_content=texto, 
                        metadata={"source": str(ruta), "page": i, "format": "TXT"}))
            print(f"Paginas del documento {formatdoc}: {len(documentos)}")

    # Cargar MD
    elif formatdoc == '.md':
        with open(ruta, "r", encoding="utf-8") as formato:

            texto = formato.read()
            fragmentos = re.split(r'\n##\s', texto)

            for i, fragmento in enumerate(fragmentos):

                if fragmento.strip():
                    # Si es la primera sección, no tiene título
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

ruta_documento = "./data/"

try:
# Cargar TODOS los documentos en la carpeta data/
    todos_los_documentos = []
    for archivo in Path(ruta_documento).iterdir():
        if archivo.suffix.lower() in ['.pdf', '.csv', '.txt', '.xlsx', '.xls', '.md', '.json']:
            print(f" Cargando: {archivo.name}")
            docs = cargar_documentos(str(archivo))
            todos_los_documentos.extend(docs)

    print(f"\n TOTAL: {len(todos_los_documentos)} documentos cargados")

except Exception:
    print(f" Error: {Exception}")
    exit(1)

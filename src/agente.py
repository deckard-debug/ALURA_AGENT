# 1 importar librerias 
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 2 Crear Variables de Entorno
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if (GOOGLE_API_KEY):
    print("ta cargada la api causita")
else:
    print("no se encontro la variables de entorno")


# 3 Cargar el documento
ruta_documento = "./data/documento.pdf"

try:
    lector = PdfReader(ruta_documento)
    documento = []
    for i, pagina in enumerate(lector.pages):
        texto = pagina.extract_text()
        if texto.strip():
            documento.append(Document(page_content=texto, metadata={"source": ruta_documento, "page": i}))
    print(f"Paginas del documento: {len(documento)}")
except:
    print(f"no se encontro el documento, ruta: {ruta_documento}")
    exit(1)

# 4 Dividir en Fragmentos para que la IA tenga informacion relevante
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n","\n","."," ",""]
)

fragmentos = text_splitter.split_documents(documento)
print(f"documento dividido en {len(fragmentos)} fragmentos")
print(f"fragmentos:\n{fragmentos[0].page_content[:200]}... ")


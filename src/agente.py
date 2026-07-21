# 1 importar librerias 
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# 2 Crear Variables de Entorno
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# if (GOOGLE_API_KEY):
#     print("ta cargada la api causita")
# else:
#     print("no se encontro la variables de entorno")


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
# print(f"documento dividido en {len(fragmentos)} fragmentos")
# print(f"fragmentos:\n{fragmentos[0].page_content[:200]}... ")

# 5 EMBEDDINGS y Base de Datos Vectorial
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key = GOOGLE_API_KEY
)

vectorstore = Chroma.from_documents(
    documents=fragmentos,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
# print(f"Base de datos vectorial creada con {len(fragmentos)} fragmentos")

# 6 Agente RAG
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key = GOOGLE_API_KEY,
    #temperature = 0.3
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
system_prompt = (
    """
    Eres un asistente experto. Responde las preguntas del usuario basandote unicamente
    en el contexto recuperado, NO inventes nueva informacion, No seas redundante en la
    misma infromacion, en caso de no poseer la respuesta a la pregunta permitete decir
    "no se"
    utiliza unicamente el contexto recuperado: {context}
    """
)
prompt = ChatPromptTemplate.from_messages([
        ("system",system_prompt),
        ("human", "{input}"),
    ])

combine_docs_chain = create_stuff_documents_chain(llm, prompt)

qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

# ============================================
# 7. FUNCIÓN PARA PREGUNTAR
# ============================================

def preguntar(pregunta: str) -> str:
    """
    Función que recibe una pregunta y devuelve la respuesta del agente.
    
    Args:
        pregunta: Texto de la pregunta del usuario
        
    Returns:
        Respuesta del agente basada en el documento
    """
    try:
        respuesta = qa_chain.invoke({"input": pregunta})
        return respuesta["answer"]
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================
# 8. INTERFAZ POR CONSOLA
# ============================================

print("\n" + "="*60)
print("AGENTE RAG - CHAT CON TU DOCUMENTO")
print("="*60)
print("Escribe 'salir' o 'exit' para terminar")
print("Escribe 'info' para ver estadísticas")
print("="*60 + "\n")

while True:
    pregunta = input("Tú: ").strip()
    
    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("\n¡Hasta luego!")
        break
    
    if pregunta.lower() == "info":
        print(f"\n Estadísticas:")
        print(f"   - Páginas en PDF: {len(documento)}")
        print(f"   - Fragmentos indexados: {len(fragmentos)}")
        print(f"   - Modelo: Gemini 3.6 Flash\n")
        continue
    
    if not pregunta:
        continue
    
    print("\nAgente: ", end="", flush=True)
    respuesta = preguntar(pregunta)
    print(respuesta + "\n")
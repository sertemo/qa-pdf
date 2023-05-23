import streamlit as st
import langchain_logic as lang
from io import BytesIO
from pypdf import PdfReader
import re
from langchain.callbacks import get_openai_callback
from streamlit_chat import message

#Configuración de la app
st.set_page_config(
    page_title="Q&A PDF -STM-",   
    page_icon="💬",)

#st.session_state.get("coste_total",0)

## Parámetros de la aplicación ##
embedding_type = "openai"
limite_palabras = 500_000
limite_coste = 0.101
#################################

## Funciones auxiliares ##
@st.cache_data(show_spinner=False)
def depurar_pdf(file: BytesIO) -> list[str]:
    """ 
    Coge un archivo pdf y lo depura.
    Devuele una lista de strings con todas las palabras del documento
    
    Función copiada de [Avra](https://medium.com/@avra42/how-to-build-a-personalized-pdf-chat-bot-with-conversational-memory-965280c160f8)
    """
    pdf = PdfReader(file)
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        # Merge hyphenated words
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Fix newlines in the middle of sentences
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)
        output.append(text)
    return output

@st.cache_data(show_spinner=False)
def validar_tamaño_documento(_docs):
    """ 
    Detiene la ejecución si se sobrepasa el limite de palabras del documento
    """

    if palabras_documentos(_docs) > limite_palabras:
        st.stop(f"El documento excede el límite de {limite_palabras} palabras. Prueba de nuevo con un documento más pequeño")

def palabras_documentos(docs)->int:
    return sum([len(doc.page_content) for doc in docs])

def calcular_coste_embeddings(palabras:int,llm_type:str)->str:
    """
    Función que no se usa.
    Devuelve el coste estimado en dólares de los embeddings\n
    en función del tipo de LLM escogido
    """
    coste = 0.00
    TARIFA_EMBEDDINGS_OPENAI = 0.0004 # $/1000 tokens
    n_tokens = 1.3333 * palabras

    if llm_type == "openai":
        coste = n_tokens / 1000 * TARIFA_EMBEDDINGS_OPENAI

    return round(coste,3)

@st.cache_data(show_spinner=False)
def devolver_respuesta(_cadena,pregunta):
        respuesta = _cadena(pregunta)
        return respuesta["result"]

def actualizar_historial(pregunta,respuesta):
    """ Verifica si existe en la sesión alguna respuesta y si están duplicadas. Si la pregunta y la respuesta ya\n
     existen, no actualiza el historial. """

    if "responses" in st.session_state:
        if respuesta not in st.session_state["responses"]:
            st.session_state["responses"].append(respuesta)
    else:
        st.session_state["responses"] = [respuesta]

    if "preguntas" in st.session_state:
        if pregunta not in st.session_state["preguntas"]:
            st.session_state["preguntas"].append(pregunta)
    else:
        st.session_state["preguntas"] = [pregunta]

def mostrar_historial():
    if "responses" in st.session_state:
        with st.sidebar:
            st.markdown("# Historial de :green[Q]&A")
            #st.write("-------")
            for q,a in zip(reversed(st.session_state["preguntas"]),reversed(st.session_state["responses"])):
                message(q,is_user=True)
                message(a)                

def cambiar_de_archivo():
    """ funcion que se deberia ejecutar al cargar otro archivo diferente.\n
    Borramos todo el caché.\n
    Se considera el cambio de archivo como un reseteo. No obstante conservamos los datos de coste total """
    #Borramos cachés
    st.cache_data.clear()
    #st.session_state.clear()
    st.cache_resource.clear()

def actualizar_consumos(cb):
    """ 
    Actualización de los consumos acumulados para el archivo actual procesado.
    """
    st.session_state["coste_total"] = st.session_state.get("coste_total",0) + round(cb.total_cost,3)   
    st.session_state["total_tokens"] = st.session_state.get("total_tokens",0) + cb.total_tokens
    st.session_state["completion_tokens"] = st.session_state.get("completion_tokens",0) + cb.completion_tokens

def validar_coste_total():
    """ Función que ya no se usa. """
    if st.session_state.get("coste_total",0.0) > limite_coste:
        st.stop("Has alcanzado el coste máximo para usar la aplicación.")

def mostrar_consumos():
    if "coste_total" in st.session_state:
        with st.expander("Ver consumos acumulados"):
            st.write("Coste total acumulado ($):",st.session_state.get("coste_total",0))
            st.write("Tokens totales utilizados:",st.session_state.get("total_tokens",0))
            st.write("'Completion Tokens' utilizados:",st.session_state.get("completion_tokens",0))


##################################

if __name__ == '__main__':
    
    #validar_coste_total()

    st.markdown("# :blue[Q]&A :red[PDF]💬 app")
    st.markdown(""" 

        ## App para preguntar a tus documentos _pdf_ 📑. """)
    
    #Instanciar modelo llm
    with st.expander("Credenciales del modelo"):
        model_type = st.selectbox(
            label="Modelo",
            options=("openai",),
        )
        API_KEY = st.text_input(label="Api key",placeholder=f"Ingresa una api key válida de {model_type} para continuar")
    
    if API_KEY:
        try:
            llm_type = lang.instanciar_modelo(API_KEY,model_type=model_type)
        except:
            st.stop("Se ha producido un error al instanciar el modelo")

        uploaded_file = st.file_uploader("Carga o arrastra un archivo pdf", type="pdf",on_change=cambiar_de_archivo)

        if uploaded_file is not None:      
            with st.spinner("Validando archivo..."):
                try:
                    with get_openai_callback() as cb:
                        doc_chunks = lang.dividir_documentos(
                            lang.texto_a_Document(
                                depurar_pdf(uploaded_file))
                        )
                        actualizar_consumos(cb)

                except Exception as e:
                    print(e)
                    st.stop("Error al procesar el archivo.")
                    
                validar_tamaño_documento(doc_chunks)
                palabras = palabras_documentos(doc_chunks)
                st.write("Número total de documentos:",len(doc_chunks),"|","Palabras totales:",palabras,"|")
                                
                cadena = lang.pipeline_to_chain(
                    _docs=doc_chunks,
                    api_key=API_KEY,
                    embedding_type=embedding_type,
                    _llm_type=llm_type,)

            
            #Poner sidebar para historial de conversación
            st.markdown("### Haz una pregunta sobre tu documento")
            pregunta = st.text_input("pregunta",
                        key="question",
                        placeholder="¿ Qué quieres preguntar ?",
                        label_visibility="hidden")

            if st.button("Enviar") and pregunta:
                st.markdown("### Respuesta:")

                with st.spinner("Pensando..."):
                    with get_openai_callback() as cb:
                        response = devolver_respuesta(cadena,pregunta)
                        actualizar_consumos(cb)
                        #print(cb)
                
                st.write(response)
                actualizar_historial(pregunta,respuesta=response)
    mostrar_historial()
    mostrar_consumos()
        
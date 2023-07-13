import streamlit as st
import langchain_logic as lang
from io import BytesIO
from pypdf import PdfReader
import re
from langchain.callbacks import get_openai_callback
import datetime
import os
import yagmail
import pytz
import requests
from dotenv import load_dotenv
import time

load_dotenv()

#Configuración de la app
st.set_page_config(
    page_title="Q2 PDF -STM-",   
    page_icon="💬",)

## Parámetros de la aplicación ##
embedding_type = "openai"
limite_palabras = 500_000

nombre_arch = ""

time_stamp = datetime.datetime.strftime(datetime.datetime.now(tz=pytz.timezone('Europe/Madrid')),format="%d-%m-%Y %H:%M:%S")
TXT_NAME = f"Historial de Q2-pdf {time_stamp}.txt"
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
YAG = yagmail.SMTP("tejedor.moreno.dev@gmail.com",GOOGLE_API_KEY)
#################################

## Funciones auxiliares ##
def is_valid_mail(email:str)->bool:
    """Función para validar una dirección de email

    Parameters
    ----------
    email : str
        La dirección de email a validar

    Returns
    -------
    bool
        Devuelve True si la dirección es una dirección válida, False en caso contrario
    """
    if not isinstance(email,str):
        return False

    if re.fullmatch(EMAIL_REGEX, email):
        return True
    else:
        return False

def stream_response_assistant(llm_texto:str,cadencia:float=0.02)->None:
    """Streamea la respuesta del LLM como chat message con una cadencia determinada

    Parameters
    ----------
    texto : str
        El texto a streamear
    cadencia : float, optional
        en segundos cuanto espera antes de mostrar la siguiente cadena de texto, by default 0.02   """
    frase = ""
    output = st.empty()
    for char in llm_texto:
        frase += char
        output.write(frase)
        time.sleep(cadencia)

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

@st.cache_data(show_spinner=False)
def devolver_respuesta(_cadena,pregunta):
        respuesta = _cadena(pregunta)
        return respuesta["result"]

def crear_historial_str_op():
    historial_str = "" #Para descargar el txt
    historial_HTML = "" #Para enviar al mail
    for dict_doc in st.session_state.values():
        if isinstance(dict_doc,dict):
            for idx,doc in enumerate(dict_doc.items(),start=1):
                historial_str += f"DOCUMENTO {idx}: {os.path.splitext(doc[0])[0]}\n\n"
                historial_HTML += f"<b style='color : #0e5188'>DOCUMENTO {idx}: {os.path.splitext(doc[0])[0]}</b>\n\n"
                for idx,(p,r) in enumerate(zip(*doc[1].values()),start=1):
                    historial_str += f"\t{idx} - {p}\n"
                    historial_str += f"\t{r}\n\n"
                    historial_HTML += f"\t<b style='color : #0e5188' >{idx} - </b><i style='color : #2a9cc1'>{p}</i>\n"
                    historial_HTML += f"\t{r}\n\n"               

    historial_str += f"""----\n\nTipo de modelo: OpenAI\nConsumos:\n\
    Tokens totales: {st.session_state.get("total_tokens",0)}\n\
    Coste total ($): {st.session_state.get("coste_total",0)}"""
    
    historial_HTML += f"""----\n
    <table class="default">
        <tr>
            <th>Tipo de modelo</th>
            <th>Tokens consumidos</th>
            <th>Coste total ($)</th>
        </tr>
        <tr>
            <td>OepnAI</td>
            <td>{st.session_state.get("total_tokens",0)}</td>
            <td>{st.session_state.get("coste_total",0)}</td>
        </tr>
    </table>"""

    return historial_str, historial_HTML

def mandar_email(email:str,text:str)->None:
    """Función para enviar por email con yagmail el historial de mensajes
    y los consumos de tokens

    Parameters
    ----------
    email : str
        el email del receptor
    text : str
        El body del email
    """
    YAG.send(
    to=email,
    subject=TXT_NAME[:-4], #Aqui le quitamos la extensión o usar os.path.splitext()
    contents=text, 
    #attachments=filename,
)

def mostrar_opciones_descarga_historial(historial_str,historial_HTML):    
        with st.expander("Opciones de Historial"):
            #Descarga el historial
            st.subheader("Descargar en formato txt")
            st.download_button(
                label = "Descargar",
                #on_click = historial_to_txt,
                data=historial_str,
                file_name=TXT_NAME,
            )            
            st.subheader("Enviar historial por email")
            email_receptor = st.text_input("Enviar historial por email",label_visibility="collapsed", placeholder="Introduce un email")
            if st.button("Enviar al email"):
                if email_receptor and is_valid_mail(email_receptor):
                    try:
                        mandar_email(email_receptor,historial_HTML)
                        st.success("Email enviado correctamente")
                    except Exception as exc:
                        st.error(f"Se ha producido un error al enviar el email: {exc}")
                else:
                    st.error("El email no es válido")

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
    st.session_state["coste_total"] = st.session_state.get("coste_total",0) + round(cb.total_cost,4)
    st.session_state["total_tokens"] = st.session_state.get("total_tokens",0) + cb.total_tokens

def validar_coste_total():
    """ Función que ya no se usa. """
    if st.session_state.get("coste_total",0.0) > limite_coste:
        st.stop("Has alcanzado el coste máximo para usar la aplicación.")

def mostrar_consumos():
    if "coste_total" in st.session_state:
        with st.expander("Ver consumos acumulados"):
            st.write("Coste total acumulado ($):",st.session_state.get("coste_total",0))
            st.write("Tokens totales utilizados:",st.session_state.get("total_tokens",0))

@st.cache_data(show_spinner=False)
def validar_api_key(api_key:str)->tuple[bool,str]:
    url = "https://api.openai.com/v1/engines/davinci"  # Endpoint de prueba

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("La API key es válida.")
            return True,""
        else:
            print("La API key no es válida.")
            return False,"La API key no es válida."
    except requests.exceptions.RequestException as e:
        print("Ocurrió un error al validar la API key:", e)
        return False, f"Ocurrió un error al validar la API key: {e}"

def actualizar_historial_op(pregunta,respuesta,document)->None:
    """Version mejorada del actualizar historial
    para poder mostrar los documentos y las preguntas y respuestas

    Parameters
    ----------
    pregunta : str
        _description_
    respuesta : str
        _description_
    document : str
        _description_
    """

    if st.session_state["docs"].get(document,None) is None:
        st.session_state["docs"][document] = {
        "preguntas" : [],
        "respuestas" : [],
    }

    if pregunta and (pregunta not in st.session_state["docs"][document]["preguntas"]):
        st.session_state["docs"][document]["preguntas"].append(pregunta)
        st.session_state["docs"][document]["respuestas"].append(respuesta)
        pregunta, respuesta = None, None

def mostrar_historial_op()->None:
    for dict_doc in st.session_state.values():
        if isinstance(dict_doc,dict):
            for idx,doc in enumerate(dict_doc.items(),start=1):
                st.write(f"*Documento {idx}* : :green[**{os.path.splitext(doc[0])[0]}**]")
                for indice,(p,r) in enumerate(zip(*doc[1].values()),start=1):
                    with st.chat_message("user"):
                        st.write(p)
                    with st.chat_message("assistant"):
                        if indice == len(st.session_state["docs"][doc[0]]["preguntas"]) \
                            and st.session_state["activador_stream"] \
                            and idx == len(st.session_state["docs"]):
                            stream_response_assistant(r)
                            st.session_state["activador_stream"] = False
                            break
                        st.write(r)

def desactivar_chat()->bool:
    return not isinstance(st.session_state.get("api_key",False),str)

##################################

if __name__ == '__main__':

    #Inicializamos variable de entorno para recibir historial
    if st.session_state.get("docs",None) is None:
        st.session_state["docs"] = {}
    st.session_state["activador_historial"] = st.session_state.get("activador_historial",False)
    st.session_state["activador_stream"] = st.session_state.get("activador_stream",False)
     
    st.markdown("# :green[Q]2-:red[PDF]💬 app")
        
    with st.sidebar:
        st.subheader("Pasos")
        st.caption("""        
        1. Ingresa una API key válida de OpenAI.\n
        2. Arrastra un archivo pdf.
        3. Hazle preguntas.""")

        st.divider()
        #Instanciar modelo llm
        API_KEY = st.text_input(
            label="API Key de OpenAI",
            placeholder=f"Ingresa la key",
            type="password",
            key="api_key",
            help="""
            Si no tienes API key,\n
            ve a https://platform.openai.com para obtener una.""")
        
        if API_KEY:
            valida_key, error_msg = validar_api_key(API_KEY)
            if not valida_key:
                st.error(error_msg)
                st.stop()
            try:
                llm_type = lang.instanciar_modelo(API_KEY,model_type="openai")
            except:
                st.stop("Se ha producido un error al instanciar el modelo")

            st.divider()
            uploaded_file = st.file_uploader("Carga o arrastra un archivo pdf", type="pdf",on_change=cambiar_de_archivo,key="archivo_cargado")
            
            if uploaded_file is not None:
                nombre_arch, ext = os.path.splitext(uploaded_file.name)  
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
                    st.write(f"""
                             Número total de documentos: :green[{len(doc_chunks)}]\
                             \nPalabras totales: :green[{palabras:,}]
                             """)

                    cadena = lang.pipeline_to_chain(
                        _docs=doc_chunks,
                        api_key=API_KEY,
                        embedding_type=embedding_type,
                        _llm_type=llm_type,)
            st.divider()

    if st.session_state.get("archivo_cargado",None) is not None:        
        pregunta = st.chat_input(placeholder=f"Haz preguntas sobre {nombre_arch}",disabled=desactivar_chat())
        if pregunta:
            with st.spinner("Pensando..."):
                with get_openai_callback() as cb:
                    response = devolver_respuesta(cadena,pregunta)
                    actualizar_consumos(cb)          
            actualizar_historial_op(pregunta,respuesta=response,document=uploaded_file.name)
            st.session_state["activador_historial"] = True
            st.session_state["activador_stream"] = True

    if st.session_state["activador_historial"]:               
        mostrar_historial_op()

        try:
            historial_str, historial_HTML = crear_historial_str_op()
        except Exception:
            historial_str = ""
            historial_HTML = ""
        with st.sidebar:
            mostrar_opciones_descarga_historial(historial_str,historial_HTML)          
    
    with st.sidebar:
        mostrar_consumos()

#st.session_state

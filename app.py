import streamlit as st
import langchain_logic as lang
from io import BytesIO
from pypdf import PdfReader
import re
from langchain.callbacks import get_openai_callback
from streamlit_chat import message
import datetime
import os
import yagmail

#Configuración de la app
st.set_page_config(
    page_title="Q2 PDF -STM-",   
    page_icon="💬",)

## Parámetros de la aplicación ##
embedding_type = "openai"
limite_palabras = 500_000
limite_coste = 0.101 #no se usa
MODEL_OPTIONS = (
    "openai",
)
time_stamp = datetime.datetime.strftime(datetime.datetime.now(),format="%d-%m-%Y %H:%M:%S")
TXT_NAME = f"Historial de Q2-pdf {time_stamp}.txt"
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"] #Esto para deploy
#GOOGLE_API_KEY = st.secrets.api_keys["GOOGLE_API_KEY"] #Esto para local
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

def actualizar_historial(pregunta,respuesta,document):#!SUSTITUIDO POR LA VERSION OP
    """ Verifica si existe en la sesión alguna respuesta y si están duplicadas. Si la pregunta y la respuesta ya\n
     existen, no actualiza el historial.
      Actualiza tambien el documento sobre el que se hacen las preguntas. """

    if "responses" in st.session_state:
        if respuesta not in st.session_state["responses"]:
            st.session_state["responses"].append(respuesta)
            st.session_state["documents"].append(document)
    else:
        st.session_state["responses"] = [respuesta]
        st.session_state["documents"] = [document]

    if "preguntas" in st.session_state:
        if pregunta not in st.session_state["preguntas"]:
            st.session_state["preguntas"].append(pregunta)
    else:
        st.session_state["preguntas"] = [pregunta]

def mostrar_historial():#!SUSTITUIDO POR LA VERSION OP
    if "responses" in st.session_state:     
        st.markdown("# Historial de :green[Q]2-:red[pdf]")
        #st.write("-------")
        for q,a in zip(reversed(st.session_state["preguntas"]),reversed(st.session_state["responses"])):
            message(q,is_user=True)
            message(a)

def crear_historial_str():#!SUSTITUIDO POR LA VERSION OP
    historial_str = ""
    historial_str = historial_str.join(
        [f"Documento:{d}\nP: {q}\nR: {a}\n\n" 
         for q,a,d 
         in 
         zip(
        st.session_state["preguntas"],
        st.session_state["responses"],
        st.session_state["documents"])])
    
    historial_str += f"""\n\nTipo de modelo: {model_type}\nConsumos:\n\
    Tokens totales: {st.session_state.get("total_tokens",0)}\n\
    Coste total ($): {st.session_state.get("coste_total",0)}"""
    return historial_str

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

    historial_str += f"""----\n\nTipo de modelo: {model_type}\nConsumos:\n\
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
            <td>{model_type}</td>
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

###Tests de formateo de muestra de historial para mostrar solo 1 documento por pregunta / respuesta
def actualizar_historial_op(pregunta,respuesta,document):
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

def mostrar_historial_op():
    st.markdown("# Historial de :green[Q]2-:red[pdf]")
    for dict_doc in st.session_state.values():
        if isinstance(dict_doc,dict):
            for idx,doc in enumerate(dict_doc.items(),start=1):
                st.write(f"*Documento {idx}* : :green[**{os.path.splitext(doc[0])[0]}**]")
                for (p,r) in zip(*doc[1].values()):
                    message(p,is_user=True)
                    message(r)


##################################

if __name__ == '__main__':

    #Inicializamos variable de entorno para recibir historial
    if st.session_state.get("docs",None) is None:
        st.session_state["docs"] = {}
    st.session_state["activador_historial"] = st.session_state.get("activador_historial",False)
     
    st.markdown("# :green[Q]2-:red[PDF]💬 app")
    st.markdown(""" 

        ## App para preguntar a tus documentos _pdf_ 📑. """)
    
    #Instanciar modelo llm
    with st.expander("Credenciales del modelo"):
        model_type = st.selectbox(
            label="Modelo",
            options=MODEL_OPTIONS,
        )
        API_KEY = st.text_input(
            label="Api key",
            placeholder=f"Ingresa una api key válida de {model_type} para continuar",
            type="password",)
    
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
                       
            st.markdown("### Haz una pregunta sobre tu documento")
            pregunta = st.text_input("pregunta",
                        #key="question",
                        placeholder="¿ Qué quieres preguntar ?",
                        label_visibility="hidden")

            if st.button("Enviar") and pregunta:
                st.markdown("### Respuesta:")

                with st.spinner("Pensando..."):
                    with get_openai_callback() as cb:
                        response = devolver_respuesta(cadena,pregunta)
                        actualizar_consumos(cb)
                        print(cb)
                
                st.write(response)
                actualizar_historial_op(pregunta,respuesta=response,document=uploaded_file.name)
                st.session_state["activador_historial"] = True
    try:
        historial_str, historial_HTML = crear_historial_str_op()
    except Exception:
        historial_str = ""
        historial_HTML = ""
    with st.sidebar:
        if st.session_state["activador_historial"]:
            mostrar_opciones_descarga_historial(historial_str,historial_HTML)
            mostrar_historial_op()    
    mostrar_consumos()

#st.session_state
<<<<<<< HEAD
import streamlit as st
from typing import Literal, Union

#LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.chat_models import ChatOpenAI

#Instructor Embeddings
from langchain.embeddings import HuggingFaceInstructEmbeddings, OpenAIEmbeddings
#import hugging_logic as hugg

#VectoreStore
from langchain.vectorstores import FAISS, DeepLake

#Secrets
#OPENAI_API_KEY = st.secrets.api_keys.OPENAI_API_KEY

#Definimos text splitter para los chunks del documento
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 600,
        chunk_overlap = 50,
        )

@st.cache_resource
def cargar_modelo_hugg(pipeline):
  """ Recibe una pipeline y devuelve el modelo Huggingface """
  return HuggingFacePipeline(pipeline=pipeline)

#Instanciamos los modelos
def instanciar_modelo(
        api_key:str,
        model_type:Literal["openai","wizardlm"]="openai"):
    """ Funcion para definir el modelo llm que se quiere usar y devolverlo.
     De momento solo disponible openai """
    
    llm_openai = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.1,
        openai_api_key=api_key,
        streaming=False)
    #llm_wizardlm = cargar_modelo_hugg(hugg.pipe)

    if model_type == "openai":
        llm = llm_openai
    
    return llm

#Definimos funciones auxiliares
@st.cache_data(show_spinner=False)
def texto_a_Document(text:str)->list[Document]:
    """ 
    Coge la lista de palabras extraidas del pdf y crea un documento\n
    tipo `Document` como el que crea PyPDFLoader. """

    if isinstance(text, str):
        # Take a single string as one page
        text = [text]
    page_docs = [Document(page_content=page) for page in text]

    # Add page numbers as metadata
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    return page_docs #doc_chunks

@st.cache_data(show_spinner=False)
def dividir_documentos(_docs:list[Document])->list[Document]:
    """ 
    Coge una lista de Documents y los trocea para crear Documents\n
    más pequeños
    """

    texts = text_splitter.split_documents(_docs)
    return texts

@st.cache_resource(show_spinner=False)
def crear_embeddings(tipo:Literal["instructor","openai"],api_key):
    if tipo == "instructor":
      embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl", model_kwargs={"device":"cuda"})
    elif tipo == "openai":
      embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    return embeddings
   
@st.cache_resource(show_spinner=False)
def crear_vectorstore(_texts:list[Document],_embeddings):
    """ 
    Devuelve un vectorstore
    """
    vectorstore = FAISS.from_documents(_texts,_embeddings)
    #vectorstore = DeepLake.from_documents(_texts,_embeddings)
    return vectorstore

@st.cache_resource(show_spinner=False)
def crear_retriever(_vectorstore:Union[FAISS,DeepLake]):
   
    retriever = _vectorstore.as_retriever(
        search_kwargs={
            "distance_metric" : "cos",
            "fetch_k" : 100,
            "maximal_marginal_relevance" : True,
            "k" : 10,
        }
    )
    return retriever

@st.cache_resource(show_spinner=False)
def crear_cadena(_retriever,_llm_type):

    chain = RetrievalQA.from_chain_type(llm=_llm_type,
                                    chain_type="stuff",
                                    retriever=_retriever,
                                    return_source_documents=False,)    
    return chain

@st.cache_data(show_spinner=False)
def pipeline_to_chain(
    _docs:list[Document],
    _llm_type,
    api_key,
    embedding_type:Literal["instructor","openai"]="openai",   
    )->RetrievalQA:
    """ 
    Función que recibe el texto en formato Document, el tipo de embeddings y el tipo de llm\n
    y devuelve una cadena de LangChain
    """
    try:
        embeddings = crear_embeddings(embedding_type,api_key=api_key)
        vectorstore = crear_vectorstore(_docs,embeddings)
        retriever = crear_retriever(vectorstore)
        cadena = crear_cadena(retriever,_llm_type)
    except Exception as exc:
        st.error("Se ha producido un error. La key introducida no es válida.")
        with st.expander("Ver detalles error"):
            st.error(exc)
        
        st.stop()

    return cadena


=======
import streamlit as st
from typing import Literal, Union

#LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.chat_models import ChatOpenAI

#Instructor Embeddings
from langchain.embeddings import HuggingFaceInstructEmbeddings, OpenAIEmbeddings
#import hugging_logic as hugg

#VectoreStore
from langchain.vectorstores import FAISS, DeepLake

#Secrets
#OPENAI_API_KEY = st.secrets.api_keys.OPENAI_API_KEY

#Definimos text splitter para los chunks del documento
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 600,
        chunk_overlap = 50,
        )

@st.cache_resource
def cargar_modelo_hugg(pipeline):
  """ Recibe una pipeline y devuelve el modelo Huggingface """
  return HuggingFacePipeline(pipeline=pipeline)

#Instanciamos los modelos
def instanciar_modelo(
        api_key:str,
        model_type:Literal["openai","wizardlm"]="openai"):
    """ Funcion para definir el modelo llm que se quiere usar y devolverlo.
     De momento solo disponible openai """
    
    llm_openai = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.1,
        openai_api_key=api_key,
        streaming=False)
    #llm_wizardlm = cargar_modelo_hugg(hugg.pipe)

    if model_type == "openai":
        llm = llm_openai
    
    return llm

#Definimos funciones auxiliares
@st.cache_data(show_spinner=False)
def texto_a_Document(text:str)->list[Document]:
    """ 
    Coge la lista de palabras extraidas del pdf y crea un documento\n
    tipo `Document` como el que crea PyPDFLoader. """

    if isinstance(text, str):
        # Take a single string as one page
        text = [text]
    page_docs = [Document(page_content=page) for page in text]

    # Add page numbers as metadata
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    return page_docs #doc_chunks

@st.cache_data(show_spinner=False)
def dividir_documentos(_docs:list[Document])->list[Document]:
    """ 
    Coge una lista de Documents y los trocea para crear Documents\n
    más pequeños
    """

    texts = text_splitter.split_documents(_docs)
    return texts

@st.cache_resource(show_spinner=False)
def crear_embeddings(tipo:Literal["instructor","openai"],api_key):
    if tipo == "instructor":
      embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl", model_kwargs={"device":"cuda"})
    elif tipo == "openai":
      embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    
    return embeddings
   
@st.cache_resource(show_spinner=False)
def crear_vectorstore(_texts:list[Document],_embeddings):
    """ 
    Devuelve un vectorstore
    """
    vectorstore = FAISS.from_documents(_texts,_embeddings)
    #vectorstore = DeepLake.from_documents(_texts,_embeddings)
    return vectorstore

@st.cache_resource(show_spinner=False)
def crear_retriever(_vectorstore:Union[FAISS,DeepLake]):
   
    retriever = _vectorstore.as_retriever(
        search_kwargs={
            "distance_metric" : "cos",
            "fetch_k" : 100,
            "maximal_marginal_relevance" : True,
            "k" : 10,
        }
    )
    return retriever

@st.cache_resource(show_spinner=False)
def crear_cadena(_retriever,_llm_type):

    chain = RetrievalQA.from_chain_type(llm=_llm_type,
                                    chain_type="stuff",
                                    retriever=_retriever,
                                    return_source_documents=False,)    
    return chain

@st.cache_data(show_spinner=False)
def pipeline_to_chain(
    _docs:list[Document],
    _llm_type,
    api_key,
    embedding_type:Literal["instructor","openai"]="openai",   
    )->RetrievalQA:
    """ 
    Función que recibe el texto en formato Document, el tipo de embeddings y el tipo de llm\n
    y devuelve una cadena de LangChain
    """
    try:
        embeddings = crear_embeddings(embedding_type,api_key=api_key)
        vectorstore = crear_vectorstore(_docs,embeddings)
        retriever = crear_retriever(vectorstore)
        cadena = crear_cadena(retriever,_llm_type)
    except Exception as exc:
        st.error("Se ha producido un error. La key introducida no es válida.")
        with st.expander("Ver detalles error"):
            st.error(exc)
        
        st.stop()

    return cadena


>>>>>>> 7191bd2583c83b4c110ac69bcdd0246340bfeeeb

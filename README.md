<<<<<<< HEAD
# Aplicación para Preguntas y Respuestas con tus documentos pdf

La apliación usa el framework **LangChain** para agrupar el proceso, que consiste en:
- Convertir a texto el pdf con **pypdf**
- Crear embeddings con **Openai**. En un futuro intentaré utilizar embeddings open source
- Crear un VectorStore con **FAISS** o **DeepLake**
- Crear el objeto retriever de **LangChain** con un contexto de *10* documentos similares (*k=10*)
- Crear cadena con LangChain y el LLM de **Openai**.

# Cómo funciona

## 0- Inserta tu API KEY de OpenAI
De momento sólo está disponible el modelo Openai.

## 1- Carga un documento pdf
El número máximo de palabras está limitado a 500.000

## 2- Haz preguntas sobre el contenido
Las preguntas y respuestas se irán guardando en el historial que aparece en el desplegable de la izquierda

Enlace a la app [aquí](https://q2-pdf.streamlit.app/).

## Actualizaciones
1. *04/06/2023* 
- Añadida la posibilidad de descargar el historial de mensajes en archivo.txt
- Añadida también la posibilidad de enviarse el historial de mensajes por email (mejora: enviar con formato HTML)
2. *06/06/2023*
- Mejorada la presentación del historial: aparece una sola vez el documento por cada pregunta y respuesta.
- Añadido formato HTML para el archivo que se envía por email con negritas y algunos colores.
3. *09/07/2023*
- Implementada nueva característica de visualización del chat.
- Movida la configuración de API Key, opciones de historial etc a la barra lateral izquierda.
- Movido el historial de chats a la ventana central.
4. *13/07/2023*
- Implementado el "streaming" del último mensaje sólo en el momento de lanzarlo


=======
# Aplicación para Preguntas y Respuestas con tus documentos pdf

La apliación usa el framework **LangChain** para agrupar el proceso, que consiste en:
- Convertir a texto el pdf con **pypdf**
- Crear embeddings con **Openai**. En un futuro intentaré utilizar embeddings open source
- Crear un VectorStore con **FAISS** o **DeepLake**
- Crear el objeto retriever de **LangChain** con un contexto de *10* documentos similares (*k=10*)
- Crear cadena con LangChain y el LLM de **Openai**.

# Cómo funciona

## 0- Inserta tu API KEY de OpenAI
De momento sólo está disponible el modelo Openai.

## 1- Carga un documento pdf
El número máximo de palabras está limitado a 500.000

## 2- Haz preguntas sobre el contenido
Las preguntas y respuestas se irán guardando en el historial que aparece en el desplegable de la izquierda

Enlace a la app [aquí](https://q2-pdf.streamlit.app/).

## Actualizaciones
1. *04/06/2023* 
- Añadida la posibilidad de descargar el historial de mensajes en archivo.txt
- Añadida también la posibilidad de enviarse el historial de mensajes por email (mejora: enviar con formato HTML)
2. *06/06/2023*
- Mejorada la presentación del historial: aparece una sola vez el documento por cada pregunta y respuesta.
- Añadido formato HTML para el archivo que se envía por email con negritas y algunos colores.
3. *09/07/2023*
- Implementada nueva característica de visualización del chat.
- Movida la configuración de API Key, opciones de historial etc a la barra lateral izquierda.
- Movido el historial de chats a la ventana central.
4. *13/07/2023*
- Implementado el "streaming" del último mensaje sólo en el momento de lanzarlo


>>>>>>> 7191bd2583c83b4c110ac69bcdd0246340bfeeeb

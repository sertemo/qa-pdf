# Aplicación para Preguntas y Respuestas con tus documentos pdf

La apliación usa el framework **LangChain** para agrupar el proceso, que consiste en:
- Convertir a texto el pdf con **pypdf**
- Crear embeddings con **Openai**. En un futuro intentaré utilizar embeddings open source
- Crear un VectorStore con **FAISS**
- Crear el objeto retriever de **LangChain** con un contexto de *2* documentos similares (*k=2*)
- Crear cadena con LangChain y el LLM de **Openai**.

# Cómo funciona

## 1- Carga un documento pdf
El número máximo de palabras está limitado a 500.000

## 2- Haz preguntas sobre el contenido
Las preguntas y respuestas se irán guardando en el historial que aparece en el desplegable de la izquierda


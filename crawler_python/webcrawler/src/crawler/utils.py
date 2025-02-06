from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def transform_text_to_docs(text: str, 
                           chunk_size: int = 1000, 
                           chunk_overlap: int = 100) -> list[Document]:
    """
    Convierte un texto largo en una lista de objetos Document,
    dividiéndolo en 'chunks' de un tamaño dado con cierto traslape.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_text(text)

   
    docs = [
        Document(page_content=chunk, metadata={"source": "my_text_data"})
        for chunk in chunks
    ]
    return docs

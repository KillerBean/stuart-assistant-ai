import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
import pypdf
from stuart_ai.core.config import settings
from stuart_ai.core.logger import logger
from stuart_ai.core.exceptions import ToolError

class DocumentStore:
    def __init__(self):
        self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
        self.collection_name = "stuart_knowledge_base"
        
        # Initialize Chroma Client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # We use Langchain's OllamaEmbeddings wrapper to generate embeddings
        # But Chroma needs an embedding function. 
        # We can use a custom embedding function adapter or use the one provided by chroma if available.
        # Alternatively, we can generate embeddings manually before adding to chroma.
        # Let's use langchain to generate embeddings and pass them to chroma.
        
        self.embedding_model = OllamaEmbeddings(
            base_url=f"http://{settings.llm_host}:{settings.llm_port}",
            model=settings.embedding_model
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def _read_file(self, file_path: str) -> str:
        """Reads text from a file (txt, md, pdf)."""
        if not os.path.exists(file_path):
            raise ToolError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                text = ""
                with open(file_path, 'rb') as f:
                    pdf = pypdf.PdfReader(f)
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                return text
            else:
                # Assume text-based for others (txt, md, py, etc)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            raise ToolError(f"Failed to read file {file_path}: {e}")

    def add_document(self, file_path: str):
        """Processes a file and adds it to the vector store."""
        logger.info(f"Adding document: {file_path}")
        text = self._read_file(file_path)
        
        if not text.strip():
            logger.warning(f"File {file_path} is empty.")
            return

        chunks = self.text_splitter.split_text(text)
        
        # Generate IDs based on filename and chunk index
        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file_path, "chunk_index": i} for i in range(len(chunks))]
        
        # Generate embeddings
        # OllamaEmbeddings.embed_documents takes a list of strings
        embeddings = self.embedding_model.embed_documents(chunks)
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(chunks)} chunks from {file_path}")

    def search(self, query: str, n_results: int = 3) -> list[str]:
        """Searches for relevant document chunks."""
        query_embedding = self.embedding_model.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # results['documents'] is a list of lists (because we can query multiple embeddings)
        if results['documents']:
            return results['documents'][0]
        return []

    def clear_database(self):
        """Clears all documents."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(self.collection_name)
        logger.info("Database cleared.")

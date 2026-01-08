import os
from typing import cast
from stuart_ai.core.config import settings
from stuart_ai.core.logger import logger
from stuart_ai.core.exceptions import ToolError

class DocumentStore:
    def __init__(self):
        self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
        self.collection_name = "stuart_knowledge_base"
        
        self._client = None
        self._embedding_model = None
        self._collection = None
        self._text_splitter = None

    @property
    def client(self):
        if self._client is None:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.persist_directory)
        return self._client

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            from langchain_ollama import OllamaEmbeddings
            self._embedding_model = OllamaEmbeddings(
                base_url=f"http://{settings.llm_host}:{settings.llm_port}",
                model=settings.embedding_model
            )
        return self._embedding_model

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    @property
    def text_splitter(self):
        if self._text_splitter is None:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
        return self._text_splitter

    def _read_file(self, file_path: str) -> str:
        """Reads text from a file (txt, md, pdf)."""
        if not os.path.exists(file_path):
            raise ToolError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                import pypdf
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
            raise ToolError(f"Failed to read file {file_path}: {e}") from e

    def add_document(self, file_path: str):
        """Processes a file and adds it to the vector store."""
        logger.info("Adding document: %s", file_path)
        text = self._read_file(file_path)
        
        if not text.strip():
            logger.warning("File %s is empty.", file_path)
            return

        chunks = self.text_splitter.split_text(text)
        
        # Generate IDs based on filename and chunk index
        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file_path, "chunk_index": i} for i in range(len(chunks))]
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(chunks)
        
        from chromadb.api.types import Embedding, Metadata
        
        self.collection.add(
            documents=chunks,
            embeddings=cast(list[Embedding], embeddings),
            metadatas=cast(list[Metadata], metadatas),
            ids=ids
        )
        logger.info("Added %d chunks from %s", len(chunks), file_path)

    def search(self, query: str, n_results: int = 3) -> list[str]:
        """Searches for relevant document chunks."""
        query_embedding = self.embedding_model.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        if results['documents']:
            return results['documents'][0]
        return []

    def clear_database(self):
        """Clears all documents."""
        self.client.delete_collection(self.collection_name)
        self._collection = None # Force re-creation
        self.collection # Accessing property re-creates it
        logger.info("Database cleared.")
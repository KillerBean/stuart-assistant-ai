import pytest
from unittest.mock import MagicMock, mock_open
from stuart_ai.agents.rag.document_store import DocumentStore
from stuart_ai.core.exceptions import ToolError

@pytest.fixture
def document_store(mocker):
    # Mock dependencies that are imported inside properties or init
    mocker.patch('chromadb.PersistentClient')
    mocker.patch('langchain_ollama.OllamaEmbeddings')
    mocker.patch('langchain_text_splitters.RecursiveCharacterTextSplitter')
    
    store = DocumentStore()
    return store

def test_initialization(document_store):
    assert document_store.persist_directory.endswith("chroma_db")
    assert document_store.collection_name == "stuart_knowledge_base"

def test_client_property(document_store, mocker):
    mock_chroma = mocker.patch('chromadb.PersistentClient')
    client = document_store.client
    mock_chroma.assert_called_once()
    assert client == mock_chroma.return_value

def test_add_document_txt(document_store, mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data="Content of the file."))
    
    # Mock text splitter
    mock_splitter = document_store.text_splitter
    mock_splitter.split_text.return_value = ["Content of", "the file."]
    
    # Mock embedding model
    mock_embedding = document_store.embedding_model
    mock_embedding.embed_documents.return_value = [[0.1], [0.2]]
    
    # Mock collection
    mock_collection = document_store.collection
    
    document_store.add_document("test.txt")
    
    mock_collection.add.assert_called_once()
    call_kwargs = mock_collection.add.call_args[1]
    assert call_kwargs['documents'] == ["Content of", "the file."]
    assert len(call_kwargs['ids']) == 2

def test_add_document_empty_file(document_store, mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data="   ")) # Empty/Whitespace
    
    mock_collection = document_store.collection
    
    document_store.add_document("empty.txt")
    
    mock_collection.add.assert_not_called()

def test_add_document_file_not_found(document_store, mocker):
    mocker.patch('os.path.exists', return_value=False)
    
    with pytest.raises(ToolError, match="File not found"):
        document_store.add_document("missing.txt")

def test_add_document_pdf(document_store, mocker):
    mocker.patch('os.path.exists', return_value=True)
    
    # Mock pypdf
    mock_pdf_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "PDF Page Content"
    mock_pdf_reader.pages = [mock_page]
    
    mocker.patch('pypdf.PdfReader', return_value=mock_pdf_reader)
    mocker.patch('builtins.open', mock_open(read_data=b"PDF data"))
    
    # Mock split/embed
    document_store.text_splitter.split_text.return_value = ["PDF Page Content"]
    document_store.embedding_model.embed_documents.return_value = [[0.1]]
    
    document_store.add_document("doc.pdf")
    
    document_store.collection.add.assert_called_once()
    assert document_store.collection.add.call_args[1]['documents'] == ["PDF Page Content"]

def test_search(document_store):
    mock_embedding = document_store.embedding_model
    mock_embedding.embed_query.return_value = [0.1, 0.2]
    
    mock_collection = document_store.collection
    mock_collection.query.return_value = {'documents': [["Result 1", "Result 2"]]}
    
    results = document_store.search("query")
    
    assert results == ["Result 1", "Result 2"]
    mock_collection.query.assert_called_once()

def test_search_no_results(document_store):
    mock_collection = document_store.collection
    mock_collection.query.return_value = {'documents': []}
    
    results = document_store.search("query")
    
    assert results == []

def test_clear_database(document_store):
    mock_client = document_store.client
    
    document_store.clear_database()
    
    mock_client.delete_collection.assert_called_once_with("stuart_knowledge_base")
    # Verify collection is recreated on next access
    _ = document_store.collection
    mock_client.get_or_create_collection.assert_called()

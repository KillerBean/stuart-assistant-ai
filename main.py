import asyncio
import whisper
import speech_recognition as sr
from stuart_ai.core.config import settings
from stuart_ai.core.assistant import Assistant
from stuart_ai.core.logger import logger
from stuart_ai.llm.ollama_llm import OllamaLLM
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.agents.rag.document_store import DocumentStore
from stuart_ai.agents.rag.rag_agent import LocalRAGAgent
from stuart_ai.services.semantic_router import SemanticRouter
from stuart_ai.core.memory import ConversationMemory

async def main():
    logger.info("Initializing Stuart AI...")
    
    # 1. Initialize Core Services (LLM)
    logger.info("Initializing LLMs...")
    # Main LLM for complex tasks (RAG, Chat, Search)
    main_llm = OllamaLLM().get_llm_instance()
    
    # Dedicated, smaller LLM for fast routing
    logger.info(f"Initializing Router LLM ({settings.router_model})...")
    router_llm = OllamaLLM(model=settings.router_model).get_llm_instance()
    
    # 2. Initialize Agents & Tools
    logger.info("Initializing Web Search Agent...")
    web_search_agent = WebSearchAgent(llm=main_llm)

    logger.info("Initializing Local RAG Agent...")
    document_store = DocumentStore()
    local_rag_agent = LocalRAGAgent(llm=main_llm, document_store=document_store)
    
    # 3. Initialize Routing & Memory
    logger.info("Initializing Semantic Router and Memory...")
    semantic_router = SemanticRouter(llm=router_llm)
    memory = ConversationMemory()
    
    # 4. Initialize Speech Services
    logger.info(f"Loading Whisper model '{settings.whisper_model_size}' (this may take a moment)...")
    whisper_model = whisper.load_model(settings.whisper_model_size)
    
    speech_recognizer = sr.Recognizer()
    
    # 5. Initialize Assistant
    logger.info("Starting Assistant...")
    assistant = Assistant(
        llm=main_llm,
        web_search_agent=web_search_agent,
        local_rag_agent=local_rag_agent,
        semantic_router=semantic_router,
        memory=memory,
        whisper_model=whisper_model,
        speech_recognizer=speech_recognizer
    )
    
    logger.info("Stuart AI is ready!")
    await assistant.listen_continuously()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stuart AI stopped by user.")
    except (RuntimeError, OSError) as e:
        logger.critical("Critical error in main loop: %s", e)

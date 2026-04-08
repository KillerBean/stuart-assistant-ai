import asyncio
from faster_whisper import WhisperModel
import speech_recognition as sr
from stuart_ai.core.config import settings
from stuart_ai.core.assistant import Assistant
from stuart_ai.core.logger import logger
from stuart_ai.core.state import AssistantContext
from stuart_ai.llm.ollama_llm import OllamaLLM
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.agents.rag.document_store import DocumentStore
from stuart_ai.agents.rag.rag_agent import LocalRAGAgent
from stuart_ai.agents.content_agent import ContentAgent
from stuart_ai.agents.coding_agent import CodingAgent
from stuart_ai.services.semantic_router import SemanticRouter
from stuart_ai.core.memory import ConversationMemory


async def _start_api(context: AssistantContext):
    """Starts the FastAPI management server in the background."""
    try:
        import uvicorn  # pylint: disable=import-outside-toplevel
        from stuart_ai.api.app import app, set_context  # pylint: disable=import-outside-toplevel
        set_context(context)
        config = uvicorn.Config(app, host="0.0.0.0", port=settings.api_port, log_level="warning")
        server = uvicorn.Server(config)
        logger.info("Management API starting on port %d", settings.api_port)
        await server.serve()
    except ImportError:
        logger.warning("fastapi/uvicorn not installed — management API disabled")


async def main():
    logger.info("Initializing Stuart AI...")

    # 1. Initialize Core Services (LLM)
    logger.info("Initializing LLMs...")
    main_llm = OllamaLLM().get_llm_instance()

    logger.info("Initializing Router LLM (%s)...", settings.router_model)
    router_llm = OllamaLLM(model=settings.router_model).get_llm_instance()

    # 2. Initialize Agents & Tools
    logger.info("Initializing Web Search Agent...")
    web_search_agent = WebSearchAgent(llm=main_llm)

    logger.info("Initializing Local RAG Agent...")
    document_store = DocumentStore()
    local_rag_agent = LocalRAGAgent(llm=main_llm, document_store=document_store)

    logger.info("Initializing Content Agent...")
    content_agent = ContentAgent(llm=main_llm)

    logger.info("Initializing Coding Agent...")
    coding_agent = CodingAgent(llm=main_llm)

    # 3. Initialize Routing & Memory
    logger.info("Initializing Semantic Router and Memory...")
    semantic_router = SemanticRouter(llm=router_llm)
    memory = ConversationMemory()

    # 4. Initialize Speech Services
    logger.info("Loading Faster Whisper model '%s'...", settings.whisper_model_size)
    whisper_model = WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")
    speech_recognizer = sr.Recognizer()

    # 5. Initialize State Context
    context = AssistantContext()

    # 6. Initialize Assistant
    logger.info("Starting Assistant...")
    assistant = Assistant(
        llm=main_llm,
        web_search_agent=web_search_agent,
        local_rag_agent=local_rag_agent,
        semantic_router=semantic_router,
        memory=memory,
        whisper_model=whisper_model,
        speech_recognizer=speech_recognizer,
        context=context,
        content_agent=content_agent,
        coding_agent=coding_agent,
    )

    logger.info("Stuart AI is ready!")

    tasks = [asyncio.create_task(assistant.listen_continuously())]
    if settings.api_enabled:
        tasks.append(asyncio.create_task(_start_api(context)))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stuart AI stopped by user.")
    except (RuntimeError, OSError) as e:
        logger.critical("Critical error in main loop: %s", e)

import asyncio
import whisper
import speech_recognition as sr
from stuart_ai.core.assistant import Assistant
from stuart_ai.core.logger import logger
from stuart_ai.llm.ollama_llm import OllamaLLM
from stuart_ai.agents.web_search_agent import WebSearchAgent
from stuart_ai.services.semantic_router import SemanticRouter
from stuart_ai.core.memory import ConversationMemory

async def main():
    logger.info("Initializing Stuart AI...")
    
    # 1. Initialize Core Services (LLM)
    logger.info("Initializing LLM...")
    llm = OllamaLLM().get_llm_instance()
    
    # 2. Initialize Agents & Tools
    logger.info("Initializing Web Search Agent...")
    web_search_agent = WebSearchAgent(llm=llm)
    
    # 3. Initialize Routing & Memory
    logger.info("Initializing Semantic Router and Memory...")
    semantic_router = SemanticRouter(llm=llm)
    memory = ConversationMemory()
    
    # 4. Initialize Speech Services
    logger.info("Loading Whisper model (this may take a moment)...")
    # Using 'small' model as per previous configuration
    whisper_model = whisper.load_model("small")
    
    speech_recognizer = sr.Recognizer()
    
    # 5. Initialize Assistant
    logger.info("Starting Assistant...")
    assistant = Assistant(
        llm=llm,
        web_search_agent=web_search_agent,
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
    except Exception as e:
        logger.critical(f"Critical error in main loop: {e}")

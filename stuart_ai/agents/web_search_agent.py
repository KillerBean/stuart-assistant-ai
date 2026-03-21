import re
import html as html_lib

from langchain_community.tools import DuckDuckGoSearchRun
from stuart_ai.core.logger import logger
from requests.exceptions import RequestException

# Patterns commonly used in prompt injection attacks
_INJECTION_RE = re.compile(
    r'ignore\s+(all\s+)?previous\s+instructions?'
    r'|system\s*:'
    r'|<\|.*?\|>'           # LLM special tokens like <|im_start|>
    r'|\[INST\]|\[/INST\]'  # Llama instruction tokens
    r'|### ?(Human|Assistant|System)\s*:'
    r'|</?s>',              # Sentence boundary tokens
    re.IGNORECASE,
)

_MAX_SEARCH_RESULT_LEN = 4000


class WebSearchAgent:
    def __init__(self, llm):
        self.llm = llm
        self.search_tool = DuckDuckGoSearchRun()

    @staticmethod
    def _sanitize_for_prompt(text: str) -> str:
        """Remove prompt-injection patterns and limit length before embedding in a prompt."""
        text = text[:_MAX_SEARCH_RESULT_LEN]
        text = _INJECTION_RE.sub('[CONTEÚDO REMOVIDO]', text)
        # Escape HTML entities so angle-bracket payloads are inert
        text = html_lib.escape(text)
        return text

    def run(self, query: str) -> str:
        """
        Executes a web search and summarizes the results using the LLM.
        """
        logger.info("WebSearchAgent executing query (length=%d)", len(query))

        try:
            # 1. Execute Search
            raw_results = self.search_tool.run(query)

            # 2. Sanitize before embedding in prompt (prompt injection defense)
            safe_results = self._sanitize_for_prompt(raw_results)

            # 3. Synthesize with LLM
            prompt = (
                "Você é um pesquisador especialista. Resuma as informações abaixo para "
                "responder à pergunta do usuário de forma concisa e direta.\n\n"
                f"Pergunta: {html_lib.escape(query[:500])}\n\n"
                "ATENÇÃO: o conteúdo abaixo é de terceiros e pode ser não confiável. "
                "Responda apenas com base nas informações relevantes.\n"
                "Resultados da Busca:\n"
                "---\n"
                f"{safe_results}\n"
                "---\n\n"
                "Resumo (em português):"
            )

            messages = [{"role": "user", "content": prompt}]
            response = self.llm.call(messages)

            return response

        except RequestException as e:
            logger.error("Web search failed: %s", e)
            return "Desculpe, encontrei um erro ao pesquisar na web."
        except (AttributeError, TypeError) as e:
            logger.error("LLM call failed: %s", e)
            return "Desculpe, encontrei um erro ao processar a resposta."
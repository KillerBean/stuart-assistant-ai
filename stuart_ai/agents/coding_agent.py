import asyncio
from stuart_ai.core.logger import logger


class CodingAgent:
    """
    Assists with development tasks: explains errors, generates scripts, analyzes code.
    Uses the main LLM with code-focused prompts in pt-BR.
    """

    def __init__(self, llm):
        self.llm = llm

    async def explain_error(self, stack_trace: str) -> str:
        """Explains a stack trace or error message in plain Portuguese."""
        logger.info("CodingAgent: explaining error")
        prompt = f"""
        Você é um desenvolvedor sênior explicando um erro para um colega.
        Explique o seguinte erro em português de forma clara e objetiva,
        dizendo o que causou o problema e como corrigi-lo:

        {stack_trace}

        Explicação:
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            return await asyncio.to_thread(self.llm.call, messages)
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.error("CodingAgent error explaining error: %s", e)
            return "Não consegui analisar o erro. Verifique se o modelo LLM está disponível."

    async def generate_script(self, description: str) -> str:
        """Generates a Python or Bash script based on a natural language description."""
        logger.info("CodingAgent: generating script for '%s'", description)
        prompt = f"""
        Você é um desenvolvedor especialista. Gere um script Python ou Bash para a seguinte tarefa.
        Seja conciso e prático. Adicione comentários explicativos em português.
        Retorne apenas o código, sem explicações extras.

        Tarefa: {description}

        Script:
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            return await asyncio.to_thread(self.llm.call, messages)
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.error("CodingAgent error generating script: %s", e)
            return "Não consegui gerar o script. Verifique se o modelo LLM está disponível."

    async def analyze_code(self, code: str) -> str:
        """Reviews a code snippet and points out issues or improvements."""
        logger.info("CodingAgent: analyzing code snippet")
        prompt = f"""
        Você é um revisor de código experiente. Analise o código abaixo e aponte:
        1. Possíveis bugs ou problemas
        2. Melhorias de legibilidade
        3. Boas práticas que estão faltando

        Responda em português de forma objetiva.

        Código:
        {code}

        Análise:
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            return await asyncio.to_thread(self.llm.call, messages)
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.error("CodingAgent error analyzing code: %s", e)
            return "Não consegui analisar o código. Verifique se o modelo LLM está disponível."

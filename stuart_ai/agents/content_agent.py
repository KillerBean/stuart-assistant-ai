import asyncio
from stuart_ai.core.logger import logger


class ContentAgent:
    """
    Summarizes web articles and YouTube videos using LLM synthesis.
    Requires: trafilatura, youtube-transcript-api
    """

    def __init__(self, llm):
        self.llm = llm

    async def summarize_url(self, url: str) -> str:
        """Fetches and summarizes a web article from a URL."""
        try:
            import trafilatura  # pylint: disable=import-outside-toplevel
        except ImportError:
            return "Módulo trafilatura não instalado. Execute: uv add trafilatura"

        logger.info("ContentAgent: fetching URL '%s'", url)
        try:
            def fetch_and_extract():
                downloaded = trafilatura.fetch_url(url)
                if not downloaded:
                    return None
                return trafilatura.extract(downloaded)

            text = await asyncio.to_thread(fetch_and_extract)
            if not text:
                return f"Não consegui extrair conteúdo da URL: {url}"

            # Truncate to avoid token overflow
            text_truncated = text[:4000]

            prompt = f"""
            Você é um assistente que resume textos de forma concisa em português.
            Resumo o artigo abaixo em no máximo 5 pontos principais:

            {text_truncated}

            Resumo:
            """
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(self.llm.call, messages)
            return response

        except (OSError, ValueError, RuntimeError) as e:
            logger.error("ContentAgent error fetching URL: %s", e)
            return "Não consegui acessar o artigo. Verifique se a URL está correta."

    async def summarize_youtube(self, video_url: str) -> str:
        """Fetches transcript and summarizes a YouTube video."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound  # pylint: disable=import-outside-toplevel
        except ImportError:
            return "Módulo youtube-transcript-api não instalado. Execute: uv add youtube-transcript-api"

        logger.info("ContentAgent: fetching YouTube transcript for '%s'", video_url)
        try:
            video_id = self._extract_video_id(video_url)
            if not video_id:
                return "Não consegui identificar o ID do vídeo. Verifique a URL."

            def get_transcript():
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=["pt", "pt-BR", "en"]
                )
                return " ".join([entry["text"] for entry in transcript_list])

            transcript = await asyncio.to_thread(get_transcript)
            transcript_truncated = transcript[:4000]

            prompt = f"""
            Você é um assistente que resume vídeos do YouTube em português.
            Resuma o transcript abaixo em no máximo 5 pontos principais:

            {transcript_truncated}

            Resumo:
            """
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(self.llm.call, messages)
            return response

        except TranscriptsDisabled:
            return "Este vídeo não possui legendas disponíveis."
        except NoTranscriptFound:
            return "Não encontrei legendas em português ou inglês para este vídeo."
        except (OSError, ValueError, RuntimeError) as e:
            logger.error("ContentAgent error fetching YouTube: %s", e)
            return "Não consegui obter o transcript do vídeo."

    @staticmethod
    def _extract_video_id(url: str) -> str | None:
        """Extracts YouTube video ID from various URL formats."""
        import re  # pylint: disable=import-outside-toplevel
        patterns = [
            r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
            r"(?:embed/)([A-Za-z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

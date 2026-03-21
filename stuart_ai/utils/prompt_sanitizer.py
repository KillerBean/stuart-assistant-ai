"""
Shared prompt sanitization utilities.

Sanitize third-party content before embedding it in LLM prompts to
mitigate prompt injection attacks (e.g. malicious documents or web
pages that contain instructions targeting the LLM).
"""
import re
import html as html_lib

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

_MAX_CONTENT_LEN = 4000


def sanitize_external_content(text: str, max_len: int = _MAX_CONTENT_LEN) -> str:
    """
    Sanitize external/untrusted content before embedding in an LLM prompt.

    Applies three layers of defense:
    1. Length cap — prevents excessively long injections.
    2. Pattern removal — strips known prompt-hijacking patterns.
    3. HTML escaping — neutralises angle-bracket payloads.
    """
    text = text[:max_len]
    text = _INJECTION_RE.sub('[CONTEÚDO REMOVIDO]', text)
    text = html_lib.escape(text)
    return text

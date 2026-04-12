import json
import logging
import os
import re
import requests

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_PATH = 'tagger_system_prompt.md'
OLLAMA_URL         = 'http://localhost:11434/api/chat'

def _load_system_prompt() -> str:
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, 'r') as f:
            return f.read()
    logger.warning(f"'{SYSTEM_PROMPT_PATH}' not found. Using bare fallback prompt.")
    return "You are a content tagging assistant. Return only a JSON object with keys: tags (array), decision (keep|remove), reason (string)."

def _extract_json(text: str) -> str:
    """
    Ollama's behavior with assistant prefill is inconsistent — sometimes it
    includes the opening brace in the returned content, sometimes it doesn't.
    Normalize to a complete JSON object either way, then strip code fences.
    """
    if not text.lstrip().startswith('{'):
        text = '{' + text

    # Strip markdown fences if the model somehow added them anyway
    fenced = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if fenced:
        return fenced.group(1)

    return text.strip()

def main(transcript: str, model: str = 'gemma4:26b') -> dict:
    """
    Sends a transcript to a local Ollama instance and returns a dict with:
        tags     : list[str]
        decision : 'keep' | 'remove'
        reason   : str

    On any failure, returns a safe fallback dict so the caller never has to
    handle None.
    """
    fallback = {'tags': [], 'decision': 'remove', 'reason': 'Tagging failed — review manually.'}

    system_prompt = _load_system_prompt()

    payload = {
        'model': model,
        'messages': [
            {'role': 'system',    'content': system_prompt},
            {'role': 'user',      'content': f'Tag the following transcript:\n<transcript>{transcript}</transcript>'},
            {'role': 'assistant', 'content': '{'}  # prefill — forces the model to continue as JSON
        ],
        'format': 'json',
        'stream': False
    }

    try:
        logger.info(f"Sending transcript to Ollama ({model}) for tagging...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=500)
        response.raise_for_status()

        raw_content = response.json().get('message', {}).get('content', '')
        logger.debug(f"Raw model output: {raw_content}")

        cleaned = _extract_json(raw_content)
        result  = json.loads(cleaned)

        # Validate expected keys are present and well-typed
        tags     = result.get('tags', [])
        decision = result.get('decision', '')
        reason   = result.get('reason', '')

        if not isinstance(tags, list):
            raise ValueError(f"'tags' is not a list: {tags}")
        if decision not in ('keep', 'remove'):
            raise ValueError(f"'decision' is not 'keep' or 'remove': {decision}")

        logger.info(f"Tagging complete — decision: {decision}, tags: {tags}")
        return {'tags': tags, 'decision': decision, 'reason': reason}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse model output as JSON. Error: {e}\nRaw output: {raw_content!r}")#type: ignore
        return fallback
    except ValueError as e:
        logger.error(f"Model output failed validation. Error: {e}")
        return fallback
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to Ollama. Error: {e}")
        return fallback
    except Exception as e:
        logger.error(f"Unexpected error during tagging. Error: {e}")
        return fallback
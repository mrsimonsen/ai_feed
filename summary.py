import logging
import requests
import os

logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT_PATH = 'summarize_system_prompt.md'

def main(transcript: str, model: str = 'gemma4:e4b') -> str:
    '''
    Sends the full transcript to Ollama and returns a short structured
    extraction (topics, tools, application angle, enterprise signals).
    This output is intended as input for tagger.main(), not for display.
    '''
    if os.path.exists(SUMMARY_SYSTEM_PROMPT_PATH):
        with open(SUMMARY_SYSTEM_PROMPT_PATH, 'r') as f:
            system_prompt = f.read()
    else:
        logger.warning(f"'{SUMMARY_SYSTEM_PROMPT_PATH}' not found. Using fallback.")
        system_prompt = "Extract the key topics, tools, and practical angles from this transcript in bullet points. Be brief."

    url = "http://localhost:11434/api/chat"
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user',   'content': f'Extract the key information from this transcript:\n<transcript>{transcript}</transcript>'}
        ],
        'stream': False
    }

    try:
        logger.info(f'Sending transcript to Ollama ({model}) for extraction...')
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        extraction = result.get('message', {}).get('content', '').strip()
        logger.info('Extraction complete.')
        return extraction
    except requests.exceptions.RequestException as e:
        logger.error(f'Failed to connect to Ollama or extraction failed. Error: {e}')
        return ''
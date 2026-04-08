import logging
import requests
import os

logger = logging.getLogger(__name__)

def main(transcript, model="llama3"):
	'''
	Sends the transcript and system prompt to a local Ollama instance
	to generate a personalized summary.
	'''
	#load system prompt
	if os.path.exists("system_prompt.md"):
		with open("system_prompt.md", 'r') as f:
			system_prompt = f.read()
	else:
		logger.warning(f"'system_prompt.md' not found. Using default prompt.")
		system_prompt = "You are a helpful assistant that summarizes text."

	#extract transcript text
	with open(transcript, 'r') as f:
		text = f.read()
	
	#default Ollama API endpoint
	url = "http://localhost:11434/api/chat"

	payload = {
		'model': model,
		'message': [
			{'role': 'system', 'content': system_prompt},
			{'role': 'user', 'content': f'Please summarize the following transcript:\n<transcript>{text}</transcript>'}
		],
		'stream': False
	}

	try:
		logger.info(f'Sending {transcript} to Ollama ({model})...')
		response = requests.post(url, json=payload, timeout=300)
		response.raise_for_status()

		result = response.json()
		summary = result.get('message', {}).get('content', '')
		logger.info("Custom summary generated successfully.")
		return summary.strip()
	except requests.exceptions.RequestException as e:
		logger.error(f'Failed to connect to Ollama or generation failed. Error: {e}')
		return "Summary generation failed."
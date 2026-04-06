import whisper
import logging

logger = logging.getLogger(__name__)

def main(file, model='base'):
	'''
	Uses OpenAI's Whisper to transcribe a mp3 file into text
	file: mp3 audio file path
	model: Whisper model to use
	Model  | Speed     | Accuracy    | Memory Req
	tiny   | Fastest   | Lowest      | ~1 GB
	base   | Fast      | Good        | ~1 GB
	small  | Moderate  | High        | ~2 GB
	medium | Slow      | Very High   | ~5 GB
	large  | Very Slow | Exceptional | ~10 GB
	'''
	logger.info('Loading model...')
	model = whisper.load_model(model)

	logger.info('Transcribing...')
	result = model.transcribe(file, verbose=False)
	with open('data/transcript.txt') as f:
		f.write(result['text']) # type: ignore
	logger.info('Transcription complete.')


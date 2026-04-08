import requests
import logging
import whisper
import os
import yt_dlp
import re

logger = logging.getLogger(__name__)

def get_safe_filename(title):
	'''
	Creates a safe filename by replacing spaces with underscores 
	and stripping out any non-alphanumeric characters.
	'''
	name = title.replace(" ", '_')
	return re.sub(r'[^\w\-]', '', name)

def transcribe(name, model='base'):
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
	result = model.transcribe(f'{name}.mp3', verbose=False)
	logger.info('Transcription complete.')
	return result['text']

def download_youtube_audio(title, link):
	'''
	Uses yt-dlp to download the audio from a YouTube video and convert it to mp3.
	'''
	name = get_safe_filename(title)
	logger.info(f'Downloading YouTube audio: {name}')

	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192'
		}],
		'outtmpl': f'{name}.%(ext)s',
		'quiet': True
	}

	try:
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download([link])
		logger.info(f'Successfully downloaded YouTube audio.')
		return name
	except Exception as e:
		logger.error(f'Failed to download YouTube audio. Error: {e}')
		return None

def download_mp3(title, link):
	name = get_safe_filename(title)
	logger.info(f'Downloading {name}')
	try:
		#stream instead of loading whole file into memory
		response = requests.get(link, stream=True)
		response.raise_for_status()
		
		with open(f'{name}.mp3', 'wb') as f:
			for chunk in response.iter_content(chunk_size=8192):
				f.write(chunk)
		logger.info(f'Successfully downloaded.')
		return name

	except requests.exceptions.RequestException as e:
		logger.warning(f'Failed to download. Error: {e}')
	except Exception as e:
		logger.error(f'Unexpected error: {e}')

def main(episode):
	'''
	Takes a dictionary of recent episode meta data and downloads the mp3 audio.
	'''
	if 'youtube.com' in episode.audio_link:
		name = download_youtube_audio(episode.title, episode.audio_link)
	else:
		name = download_mp3(episode.title, episode.audio_link)
	if name:
		episode.summary = transcribe(name)
	#clean up .mp3
	os.remove(f'{name}.mp3')
	return episode

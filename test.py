import feed, config, download_transcribe, tagger
import logging


config.setup_logging()
logger = logging.getLogger(__name__)

logger.info('Starting feed extraction...')
recent_episodes = feed.load_untagged_episodes()
logger.info(f'Found {len(recent_episodes)} recent episodes.')

logger.info('Downloading & Transcribing new episodes')
summarized = []
recent_episodes = [recent_episodes[0]]
for episode in recent_episodes:
	episode = download_transcribe.main(episode)
	
	logging.info('Tagging')
	data = tagger.main(episode.summary)
	episode.tags = data.get('tags')
	episode.decision = data.get('decision')
	episode.relevance_note = data.get('reason')
	summarized.append(episode)
print(summarized[0].source,'|',summarized[0].title,'|',summarized[0].audio_link)
print(summarized[0].decision,'|',summarized[0].relevance_note)
print(summarized[0].tags)


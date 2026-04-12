import logging
import config
import feed, download_transcribe, tagger

if __name__ == "__main__":
	config.setup_logging()
	logger = logging.getLogger(__name__)

	logger.info('Starting feed extraction...')
	recent_episodes = feed.load_untagged_episodes()
	logger.info(f'Found {len(recent_episodes)} recent episodes.')

	logger.info('Downloading & Transcribing new episodes')
	summarized = []
	for episode in recent_episodes:
		episode = download_transcribe.main(episode)
		
		logging.info('Tagging...')
		tags, decision, reason = tagger.main(episode.summary)
		episode.tags = tags
		episode.decision = decision
		episode.relevance_note = reason
		summarized.append(episode)

	

	logger.info('Process complete.')
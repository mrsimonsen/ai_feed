import logging
import config
import feed, message, download_transcribe, summary

#RSS feeds
FEEDS={
	'IBM Technology': "https://www.youtube.com/feeds/videos.xml?playlist_id=UULFKWaEZ-_VweaEx1j62do_vQ",
	'The AI Daily Brief': "https://anchor.fm/s/f7cac464/podcast/rss",
	'The AI in Business Podcast': "https://techemergence.libsyn.com/rss",
	'Practical AI': "https://feeds.transistor.fm/practical-ai-machine-learning-data-science-llm"
}

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
		
		logging.info('Customizing summary')
		episode.summary = summary.main(episode.summary)
		summarized.append(episode)

	

	logger.info('Process complete.')
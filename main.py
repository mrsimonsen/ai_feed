import logging
import config
import feed, message, clean_up, download

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
	raw_data = feed.fetch_feed(FEEDS)
	recent_episodes = feed.parse_recent_episodes(raw_data)
	logger.info(f'Found {len(recent_episodes)} recent episodes.')

	logger.info('Downloading new episodes')
	#TODO: iterate through episodes and download them
	download.main(recent_episodes)

	logger.info('Transcribing episodes')
	#TODO: use whisper to transcribe downloaded episodes

	logging.info('Customizing summary')
	#TODO: use ollama with system prompt to generate custom summaries

	logger.info('creating email')
	email_body = message.format_email_body(recent_episodes)

	logger.info("Attempting transmission...")
	message.send_email(email_body)

	logging.info('Cleaning up...')
	#TODO: clean_up
	#clean_up.main()

	logger.info('Process complete.')
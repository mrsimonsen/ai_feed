import requests
import logging

#configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(levelname)s: %(message)s'
)

#RSS feeds
FEEDS={
	'IBM Technology': "https://youtube.com/feeds/videos.xml?channel_id=UCKWaEZ-_VweaEx1j62do_vQ",
	'The AI Daily Brief': "https://anchor.fm/s/f7cac464/podcast/rss",
	'The AI in Business Podcast': "https://techemergence.libsyn.com/rss",
	'Practical AI': "https://feeds.transistor.fm/practical-ai-machine-learning-data-science-llm"
}

def fetch_feeds(feeds_dict):
	'''
	Loops through a dictionary of RSS feeds, downloads the XML data,
	and safely handles any connection or HTTP errors.
	'''
	feed_data={}

	for name, url in feeds_dict.items():
		try:
			#timeout for unresponsive server
			response = requests.get(url, timeout=15)

			#raise a requests.exception.HTTPError if the status is 4xx or 5xx
			response.raise_for_status()

			#store successful data
			feed_data[name] = response.content
			logging.info(f"Successfully downloaded '{name}' ({len(response.text)} bytes).")

		except requests.exceptions.RequestException as e:
			#catches timeouts, connection errors, and bad HTTP status codes
			logging.error(f"Failed to download '{name}' from {url}. Error: {e}")
		
		except Exception as e:
			# fallback catch for other errors
			logging.error(f"Unexpected error processing '{name}'. Error: {e}")

	return feed_data

if __name__ == "__main__":
	data = fetch_feeds(FEEDS)
	print("Process complete")
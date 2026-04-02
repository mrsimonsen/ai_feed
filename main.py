import requests
import logging
import feedparser
import bleach
import html
import unicodedata
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

#configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(levelname)s: %(message)s'
)

HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

#RSS feeds
FEEDS={
	'IBM Technology': "https://www.youtube.com/feeds/videos.xml?playlist_id=UULFKWaEZ-_VweaEx1j62do_vQ",
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
			response = requests.get(url, headers=HEADERS, timeout=15)

			#raise a requests.exception.HTTPError if the status is 4xx or 5xx
			response.raise_for_status()

			feed_data[name] = response.content
			logging.info(f"Successfully downloaded '{name}' ({len(response.content)} bytes).")

		except requests.exceptions.RequestException as e:
			#catches timeouts, connection errors, and bad HTTP status codes
			logging.error(f"Failed to download '{name}' from {url}. Error: {e}")
		
		except Exception as e:
			# fallback catch for other errors
			logging.error(f"Unexpected error processing '{name}'. Error: {e}")

	return feed_data

def clean_html_text(raw_text):
	'''
	Sanitizes text by removing HTML tags, unescaping HTML entities,
	and stripping invisible or problematic Unicode characters.
	'''
	cleaned = bleach.clean(raw_text, tags=[], strip=True)
	cleaned = html.unescape(cleaned)
	cleaned = unicodedata.normalize('NFKD', cleaned)
	cleaned = cleaned.replace('\u2060', '')
	return cleaned.strip()

def parse_recent_episodes(feed_data):
	'''
	Parses raw RSS/XML data, extracts key fields, converts to Mountain Time,
	filters for the last 24 hours, and deduplicates items.
	'''
	#calculate cutoff time
	now_utc = datetime.now(timezone.utc)
	cutoff_time = now_utc - timedelta(hours=24)

	recent_episodes = []
	seen_ids = set()

	for feed_name, raw_xml in feed_data.items():
		parsed_feed = feedparser.parse(raw_xml)

		if parsed_feed.bozo:
			logging.warning(f"Feed '{feed_name}' is malformed: {parsed_feed.bozo_exception}")

		for entry in parsed_feed.entries:
			#remove duplicates
			unique_id = entry.get('id', entry.get('link', entry.get('title')))
			if unique_id in seen_ids:
				continue

			#check for valid publish time
			if not hasattr(entry, 'published_parsed') or not entry.published_parsed:
				logging.warning(f"Missing or unparsable date for '{unique_id}' in {feed_name}'. Skipping.")
				continue
			try:
				# struct_time has 9 items; datetime needs the first 6 (Y, M, D, H, M, S)
				dt_utc = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
			except ValueError as e:
				logging.warning(f"Invalid date values for '{unique_id}' in '{feed_name}'. Error: {e}")
				continue

			#filter for 24 hours
			if dt_utc < cutoff_time:
				continue

			#extract data
			seen_ids.add(unique_id)
			dt_mt = dt_utc.astimezone(ZoneInfo("America/Denver"))
			clean_title = clean_html_text(entry.get('title', 'No Title'))
			clean_description = clean_html_text(entry.get('summary', entry.get('description', 'No Description')))
			recent_episodes.append({
				'feed_name': feed_name,
				'title': clean_title,
				'description': clean_description,
				'publish_date_mt': dt_mt.strftime('%Y-%m-%d %I:%M %p %Z'),
				'link': entry.get('link', 'No Link')
			})
	
	return recent_episodes


if __name__ == "__main__":
	data = parse_recent_episodes(fetch_feeds(FEEDS))
	print("Process complete")
	print(data)
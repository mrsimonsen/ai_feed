import bleach
import feedparser
import html
import logging
import requests
import unicodedata
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class Episode():
	def __init__(self):
		self.source = 'No Source'
		self.title = 'No Title'
		self.pud_date_mt = datetime.now().strftime('%Y-%m-%d %I:%M %p %Z')
		self.duration = '0'
		self.episode_link = 'No Episode Link'
		self.audio_link = 'No Audio Link'
		self.summary = 'No Summary'

def fetch_feed(feeds_dict):
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

def parse_recent_episodes(feed_data, delta=24):
	'''
	Parses raw RSS/XML data, extracts key fields, converts to Mountain Time,
	filters for the last 24 hours, and deduplicates items.
	'''
	#calculate cutoff time
	now_utc = datetime.now(timezone.utc)
	cutoff_time = now_utc - timedelta(hours=delta)

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
				dt_utc = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) # type: ignore
			except ValueError as e:
				logging.warning(f"Invalid date values for '{unique_id}' in '{feed_name}'. Error: {e}")
				continue

			#filter for 24 hours
			if dt_utc < cutoff_time:
				continue

			#extract data
			seen_ids.add(unique_id)
			ep = Episode()
			ep.source = feed_name
			ep.title = clean_html_text(entry.get('title', 'No Title'))
			ep.pub_date_mt = dt_utc.astimezone(ZoneInfo("America/Denver")).strftime('%Y-%m-%d %I:%M %p %Z')#type: ignore
			ep.duration = entry.get('itunes_duration', 'No Duration')#type: ignore
			ep.episode_link = entry.get('link', 'No Episode Link')#type: ignore
			ep.audio_link = entry.get('enclosures', [])[0].get('href', 'No Audio Link')#type: ignore

			recent_episodes.append(ep)
	
	return recent_episodes
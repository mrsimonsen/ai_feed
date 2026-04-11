import logging
import pandas as pd

logger = logging.getLogger(__name__)

CONTENT_CSV = 'AI_resources__-_Content.csv'

class Episode():
	def __init__(self):
		self.source = 'No Source'
		self.title = 'No Title'
		self.audio_link = 'No Audio Link'
		self.tags = []
		self.relevance_note = ''

def load_untagged_episodes(csv_path=CONTENT_CSV):
	'''
	Reads the Content CSV exported from Google Sheets and returns a list
	of Episodes objects for every row that does not yet have tags assigned.

	Expected columns: Source, Date, Title, Tags, Link
	'''
	try:
		df = pd.read_csv(csv_path)
	except FileNotFoundError:
		logger.error(f"Content CSV not found at '{csv_path}'")
		return []
	except Exception as e:
		logger.error(f"Failed to read CSV. Error: {e}")
		return []
	
	required_cols = {'Source', 'Title', 'Link'}
	missing = required_cols - set(df.columns)
	if missing:
		logger.error(f"CSV missing expected columns: {missing}")
		return []
	
	if 'Tags' in df.columns:
		untagged = df[df['Tags'].isna() | (df['Tags'].astype(str).str.strip() == '')]
	else:
		logger.warning("No 'Tags' column found -treating all rows as untagged.")
		untagged = df

	episodes = []
	for _, row in untagged.iterrows():
		ep = Episode()
		ep.source = str(row.get('Source', 'No Source')).strip()
		ep.title = str(row.get('Title', 'No Title')).strip()
		ep.audio_link = str(row.get('Link', 'No Audio Link')).strip()

		episodes.append(ep)

	return episodes

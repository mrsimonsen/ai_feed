1. ~~Create a new branch
Branch off main (or transcription-&-LLM-summary if that has the Whisper/Ollama logic you want to build on). Name it something like csv-tagging.~~
2. ~~Update dependencies
Remove RSS-specific packages (feedparser, bleach) from requirements.txt since they're no longer needed. Add pandas for CSV reading.~~
3. Rewrite feed.py
Replace the RSS fetch and parse logic entirely. The new version should read the CSV exported from your Google Sheet, map each row to an Episode object (source, title, link), and return the list. No date filtering needed — process all rows that don't already have tags assigned.
4. Keep download_transcribe.py as-is
The download and Whisper transcription logic doesn't need to change. It already handles both YouTube and MP3 links, which covers your sources.
5. Rewrite system_prompt.md
This is the core logic change. The new prompt should instruct the LLM to return structured output (JSON) containing: a list of assigned tags drawn from the defined tag list, and a relevance decision — keep or remove — with a brief reason. The prompt should include the full tag list and descriptions so the model has the vocabulary to work with. Note: the model should be opinionated about relevance. If an episode is too technical (deep MLOps, chip manufacturing, academic research), too consumer-focused, or just doesn't map to any of your tags, it should flag it for removal rather than forcing a tag fit.
6. Rewrite summary.py → rename to tagger.py
Repurpose the Ollama API call to request structured JSON output instead of a free-text summary. Parse the response and attach the tags and relevance decision back onto the Episode object. Add error handling for malformed JSON responses.
7. Update main.py
Update the orchestration to use the new feed.py and tagger.py. Remove the email step — output isn't going to an inbox anymore.
8. Replace message.py with a CSV writer
Instead of formatting and sending an email, write the results back out to a CSV. Columns should match your Google Sheet: source, date, title, tags (comma-separated), link, and a new relevance_note column for the model's removal reasoning so you can review it before acting on it.
9. Update daily_email.yml or create a new GitHub Action
The scheduled trigger and email secrets are no longer relevant. Either disable the workflow or replace it with a manually triggered workflow_dispatch-only action, since this is something you'll run on demand rather than on a schedule.

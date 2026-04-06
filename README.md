# Daily Media Aggregator

## Project Overview
This project is a custom Python automation script designed to aggregate daily podcast episodes and YouTube videos from a specific set of creators, transcribe the audio using OpenAI's Whisper, and deliver tailored updates directly to my inbox.

**The "Why":** The goal is to get a highly relevant, curated daily update of new AI content. While originally built as a simple deterministic RSS parser, the project has evolved to leverage local AI tools to extract deeper insights. By downloading the media, utilizing Whisper for automated transcription, and preparing the text for local LLMs (like Ollama) to perform custom summarization, this pipeline creates a powerful, personalized information feed. It ensures that I get specific, prompt-driven summaries of the content I care about, directly from the source material.

**Tracked Sources:**
* IBM Technology (YouTube)
* The AI Daily Brief (Podcast)
* The AI in Business (Podcast)
* Practical AI (Podcast)

**Core Pipeline & Roadmap:**
* ✅ **RSS Aggregation:** Fetches, deduplicates, and filters episodes published in the last 24 hours.
* ✅ **Automated Transcription:** Downloads MP3 audio streams and transcribes them locally using OpenAI's Whisper model.
* 🚧 **Custom LLM Summarization (WIP):** Planned integration with an LLM to replace basic RSS descriptions with custom, system-prompted summaries of the full transcripts.
* ✅ **Email Delivery:** Automatically formats and dispatches a clean daily email report via GitHub Actions.

## Customization

### The `system_prompt.md` File
To ensure the LLM generates highly relevant insights rather than generic overviews, the Ollama integration will reference a local `system_prompt.md` file. This file acts as the guiding persona for the summarization process. 

You should customize this file to include details about your work, goals, and background so the LLM can extract what matters most to you. For example, your `system_prompt.md` can instruct the model to specifically highlight podcast discussions relevant to your current job search, pull out practical tips for utilizing AI transcription and summarization workflows, or even flag tech events and news relevant to the Conifer, Colorado area. By feeding the LLM this personal context, the daily email becomes a targeted briefing rather than just a list of episodes.
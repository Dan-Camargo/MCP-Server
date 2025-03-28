# Combined Services MCP Server

A Model Context Protocol (MCP) server that provides tools for weather information and YouTube transcript extraction.

## Features

### Weather Tools
- Get active weather alerts for specific >>>UNITED STATES<<< states
- Get detailed weather forecasts for any location using coordinates
- Real-time data from National Weather Service API

### YouTube Transcript Tools
- Extract transcripts from YouTube videos using video URLs or IDs
- Support for multiple languages
- Handles various YouTube URL formats (youtube.com, youtu.be)
- Simple and efficient transcript formatting

## Installation

1. Make sure you have Python 3.12 or higher installed
2. Install the dependencies:
```bash
pip install -e .
```

## Usage

Run the server:
```bash
python combined_server.py
```

The server provides the following tools:

### Weather Tools

#### get_alerts
Get active weather alerts for a specific state.

Parameters:
- `state` (string): Two-letter state code (e.g., 'CA', 'NY')

Example:
```python
result = await get_alerts("CA")
```

#### get_forecast
Get weather forecast for a specific location.

Parameters:
- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

Example:
```python
result = await get_forecast(37.7749, -122.4194)  # San Francisco coordinates
```

### YouTube Transcript Tool

#### get_transcript
Extract transcript from a YouTube video.

Parameters:
- `url` (string): YouTube video URL or ID
- `lang` (string, optional): Language code for transcript (e.g., 'en', 'ko'). Defaults to 'en'

Example:
```python
# Using a YouTube URL
result = await get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Using a video ID
result = await get_transcript("dQw4w9WgXcQ")

# Using a different language
result = await get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", lang="ko")
```

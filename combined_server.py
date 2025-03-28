from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs
import re
import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("combined-services")

# Weather Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Weather Functions
async def new_nws_request(url: str) -> dict[str, Any] | None:

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

# YouTube Transcript Functions
def extract_youtube_id(input_url: str) -> str:
    """Extract YouTube video ID from various URL formats or direct ID input."""
    if not input_url:
        raise ValueError("YouTube URL or ID is required")

    #try parsing as URL
    try:
        url = urlparse(input_url)
        if url.hostname == "youtu.be":
            return url.path[1:]
        elif "youtube.com" in url.hostname:
            video_id = parse_qs(url.query).get("v", [None])[0]
            if not video_id:
                raise ValueError(f"Invalid YouTube URL: {input_url}")
            return video_id
    except ValueError:
        #not a URL, check if it's a direct video ID
        if re.match(r"^[a-zA-Z0-9_-]{11}$", input_url):
            return input_url
        
    raise ValueError(f"Could not extract video ID from: {input_url}")

def format_transcript(transcript: list[dict]) -> str:
    """Format transcript lines into readable text."""
    return " ".join(
        line["text"].strip() 
        for line in transcript 
        if line["text"].strip()
    )

# Weather Tools
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get active weather alerts for a specific state."""
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await new_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await new_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await new_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

# YouTube Transcript Tool
@mcp.tool()
async def get_transcript(url: str, lang: str = "en") -> str:
    """Extract transcript from a YouTube video URL or ID.
    
    Args:
        url: YouTube video URL or ID
        lang: Language code for transcript
    """
    try:
        video_id = extract_youtube_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        return format_transcript(transcript)
    except Exception as e:
        return f"Failed to retrieve transcript: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# initialize the mcp server
mcp = FastMCP('weather')


# constats
NWS_API_BASE = 'https://api.weather.gov'
USER_AGENT = 'weather-app/1.0'

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Makes a request to the NWS API with proper error handling."""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/geo+json'
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return None

def format_alert(feature: dict) -> str:
    """Format an alert deature into a readable string."""
    props = feature['properties']
    return f'''
        Event: {props.get('event', 'unknown')}
        Area: {props.get('area', 'unknown')}
        Severity: {props.get('severity', 'unknown')}
        Status: {props.get('status', 'unknown')}
        Start: {props.get('start', 'unknown')}
        End: {props.get('end', 'unknown')}
        Description: {props.get('description', 'unknown')}
        Instruction: {props.get('instruction', 'unknown')}
    '''

@mcp.tool()
async def get_alert(state: str) -> str:
    """
    Get wather alets for a US state.

    Args:
        state: Two-letter US state code(e.g. CA, NY)
    """
    url = f'{NWS_API_BASE}/alerts/active/area/{state}'
    data = await make_nws_request(url)
    if not data or 'features' not in data:
        return 'No active alerts found.'

    if not data['features']:
        return 'No active alerts found.'

    alerts = [format_alert(feature) for feature in data['features']]
    return '\n---\n'.join(alerts)


# Mcp config resource
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"

@mcp.resource("echo://{message}")
def echo(message: str) -> str:
    """Echo a message"""
    return f'Resource echo: {message}'

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")
NEWS_API_BASE = "https://api.weather.gov/"
USER_AGENT = "weather-app/1.0"

async def make_news_request(url :str) -> dict[str,any] | None:
    """
    Make a request to NWS API with proper error handling.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept":"application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url,headers=headers,timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception:
            return "I can't access the weather API right now. Please try again later."

def format_alert(feature:dict) -> str:
    """
    Format an altert feature into readable string
    """
    props = feature["properties"]
    return f"""
    Event : {props.get("event","Unknown")}
    Area : {props.get("areaDesc","Unknown")}
    Severity : {props.get("severity","Unknown")}
    Description : {props.get("description","Unknown")}
    Instruction : {props.get("instruction","Unknown")}        
    """
@mcp.tool()

async def get_alerts(state: str) -> str:
    print(f"[DEBUG] Fetching weather alerts for state: {state}")
    url = f"{NEWS_API_BASE}alerts/active?area={state}"
    data = await make_news_request(url)

    if not data or "features" not in data:
        print("[DEBUG] No data or no 'features' key in response.")
        return "Unable to fetch alerts or no alerts found"
    
    if not data["features"]:
        print("[DEBUG] No active alerts in 'features'.")
        return "No active alerts"
    
    alerts = [format_alert(feature) for feature in data["features"]]
    print(f"[DEBUG] Found {len(alerts)} alerts")
    return "\n--\n".join(alerts)

@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """ 
    echo a messagge as resource
    """
    return f"Resource echo : {message}"



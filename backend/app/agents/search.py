import logging
from typing import Dict, Any
from app.services.serpapi_service import serpapi_service
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

def search_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Hotel Search Agent: Queries SerpAPI / Google Hotels for active listings matching location constraints.
    """
    preferences = state.get("preferences", {})
    location = preferences.get("location", "New York")
    check_in = state.get("check_in", "2026-06-15")
    check_out = state.get("check_out", "2026-06-20")
    
    log_messages = state.get("logs", [])
    errors = state.get("errors", [])
    
    log_messages.append(f"Hotel Search Agent active: Contacting SerpAPI Google Hotels for destination '{location}'...")
    
    try:
        hotels = serpapi_service.search_hotels(
            destination=location,
            check_in=check_in,
            check_out=check_out
        )
        # Limit candidate hotels to top 4 to avoid massive sequential LLM API latency
        hotels = hotels[:4]
        log_messages.append(f"Search completed: Retrieved {len(hotels)} candidate hotels in '{location}'.")
    except Exception as e:
        errors.append(f"SearchAgent node failure: {str(e)}")
        log_messages.append(f"Search failed: {str(e)}")
        hotels = []

    return {
        "raw_hotels": hotels,
        "logs": log_messages,
        "errors": errors
    }

from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    # Inputs
    user_query: str
    check_in: str
    check_out: str
    
    # Processed preferences
    preferences: Dict[str, Any]
    
    # Collected search results
    raw_hotels: List[Dict[str, Any]]
    
    # Analytics
    pricing_metrics: Dict[str, Any]
    
    # Review summaries (RAG output)
    review_insights: Dict[str, Any]
    
    # Outputs
    recommendations: List[Dict[str, Any]]
    
    # Flow telemetry and logging
    errors: List[str]
    logs: List[str]

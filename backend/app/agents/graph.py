import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.preference import preference_agent_node
from app.agents.search import search_agent_node
from app.agents.pricing import pricing_agent_node
from app.agents.review import review_agent_node
from app.agents.recommend import recommendation_agent_node

logger = logging.getLogger(__name__)

# Initialize the LangGraph builder
workflow = StateGraph(AgentState)

# Add agent nodes to the graph
workflow.add_node("preference_analysis", preference_agent_node)
workflow.add_node("hotel_search", search_agent_node)
workflow.add_node("pricing_analysis", pricing_agent_node)
workflow.add_node("review_analysis", review_agent_node)
workflow.add_node("recommendation", recommendation_agent_node)

# Define execution transitions
workflow.add_edge(START, "preference_analysis")
workflow.add_edge("preference_analysis", "hotel_search")
workflow.add_edge("hotel_search", "pricing_analysis")
workflow.add_edge("pricing_analysis", "review_analysis")
workflow.add_edge("review_analysis", "recommendation")
workflow.add_edge("recommendation", END)

# Compile into executable application graph
compiled_graph = workflow.compile()

def run_agent_pipeline(query: str, check_in: str, check_out: str) -> Dict[str, Any]:
    """Runs the compiled LangGraph pipeline for hotel recommendations."""
    initial_state = {
        "user_query": query,
        "check_in": check_in,
        "check_out": check_out,
        "preferences": {},
        "raw_hotels": [],
        "pricing_metrics": {},
        "review_insights": {},
        "recommendations": [],
        "errors": [],
        "logs": []
    }
    
    try:
        final_state = compiled_graph.invoke(initial_state)
        return final_state
    except Exception as e:
        logger.error(f"Pipeline execution crash: {str(e)}")
        # Provide fail-safe structured response if pipeline completely breaks
        return {
            "user_query": query,
            "check_in": check_in,
            "check_out": check_out,
            "preferences": {"location": "Error State", "budget_limit": 0.0, "amenities": [], "trip_style": "unknown"},
            "raw_hotels": [],
            "pricing_metrics": {"avg_price": 0.0, "max_price": 0.0, "min_price": 0.0, "hotel_pricing_analysis": {}},
            "review_insights": {},
            "recommendations": [],
            "errors": [f"Pipeline Execution Error: {str(e)}"],
            "logs": ["Orchestrator Error: Graph traversal crashed."]
        }

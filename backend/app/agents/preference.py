import json
import logging
import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

class ExtractedPreferences(BaseModel):
    location: str = Field(..., description="The target destination city, country, or region (e.g., Kyoto, Seattle, Miami).")
    budget_limit: float = Field(default=250.0, description="Max budget per night in USD. Extract numbers from text like '$300/night', 'under 150'. If completely unspecified, default to 250.0")
    amenities: List[str] = Field(default=[], description="List of amenities, features or characteristics requested (e.g., wifi, spa, pool, pet-friendly, breakfast, quiet).")
    trip_style: str = Field(default="leisure", description="Style of trip: leisure, business, luxury, budget, family, romantic, boutique, adventure.")

def parse_preferences_fallback(query: str) -> Dict[str, Any]:
    """Fallback simple regex parser if LLM execution fails or API keys are missing."""
    # Location extraction: look for "in [City]"
    loc_match = re.search(r"\bin\s+([A-Za-z\s]+?)(?:for|with|under|at|near|check|\b|$)", query, re.IGNORECASE)
    location = loc_match.group(1).strip() if loc_match else "San Francisco"
    
    # Budget extraction: look for numbers preceded by $ or followed by /night
    budget = 250.0
    budget_match = re.search(r"(?:\$\s*|budget\s+around\s+|under\s+)(\d+)", query, re.IGNORECASE)
    if budget_match:
        budget = float(budget_match.group(1))
    
    # Amenities search
    amenity_keywords = ["spa", "pool", "gym", "wifi", "breakfast", "parking", "pet", "kitchen", "beach", "luxury"]
    found_amenities = [kw for kw in amenity_keywords if kw in query.lower()]
    
    # Trip style search
    trip_style = "leisure"
    for style in ["business", "family", "romantic", "luxury", "budget", "boutique"]:
        if style in query.lower():
            trip_style = style
            break
            
    return {
        "location": location,
        "budget_limit": budget,
        "amenities": found_amenities,
        "trip_style": trip_style
    }

def preference_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Extracts travel preferences from the user's natural language query.
    """
    query = state.get("user_query", "")
    log_messages = state.get("logs", [])
    errors = state.get("errors", [])
    
    log_messages.append("Preference Analysis Agent active: Parsing search preferences...")
    
    # Check for Groq API Key
    if not settings.GROQ_API_KEY or "your_groq_api_key_here" in settings.GROQ_API_KEY:
        log_messages.append("Groq API key missing. Running fallback rule-based parser.")
        prefs = parse_preferences_fallback(query)
    else:
        try:
            # Instantiate Groq Client via LangChain
            llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model_name=settings.LLM_MODEL,
                temperature=0.0
            )
            
            # Use structured output parser
            structured_llm = llm.with_structured_output(ExtractedPreferences)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a Travel Preference Extraction Agent. Your job is to analyze "
                    "the user's query and extract structured hotel search details. "
                    "Always extract a location, a budget per night, a list of amenities/features, "
                    "and a general trip style. Return valid structured outputs."
                )),
                ("human", "User Query: {query}")
            ])
            
            chain = prompt | structured_llm
            result = chain.invoke({"query": query})
            
            prefs = {
                "location": result.location,
                "budget_limit": result.budget_limit,
                "amenities": result.amenities,
                "trip_style": result.trip_style
            }
        except Exception as e:
            errors.append(f"PreferenceAgent LLM failure: {str(e)}")
            log_messages.append(f"LLM parsing failed, applying fallback parser: {str(e)}")
            prefs = parse_preferences_fallback(query)

    log_messages.append(f"Preferences Extracted: Destination='{prefs['location']}', Budget=${prefs['budget_limit']}, Style='{prefs['trip_style']}', Amenities={prefs['amenities']}")
    
    return {
        "preferences": prefs,
        "logs": log_messages,
        "errors": errors
    }

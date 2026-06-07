import logging
from typing import Dict, Any
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

def pricing_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Pricing Analysis Agent: Analyzes distributions, computes averages, 
    calculates value scores, and evaluates budget compatibility.
    """
    raw_hotels = state.get("raw_hotels", [])
    preferences = state.get("preferences", {})
    budget_limit = preferences.get("budget_limit", 250.0)
    
    log_messages = state.get("logs", [])
    errors = state.get("errors", [])
    
    log_messages.append("Pricing Analysis Agent active: Performing price evaluation...")
    
    if not raw_hotels:
        log_messages.append("No hotels found for pricing evaluation.")
        return {
            "pricing_metrics": {
                "avg_price": 0.0,
                "max_price": 0.0,
                "min_price": 0.0,
                "hotel_pricing_analysis": {}
            },
            "logs": log_messages
        }

    prices = [h["price_per_night"] for h in raw_hotels]
    avg_price = sum(prices) / len(prices)
    max_price = max(prices)
    min_price = min(prices)
    
    log_messages.append(f"Price statistics: Avg=${avg_price:.2f}, Range=[${min_price:.2f} - ${max_price:.2f}], Budget Limit=${budget_limit:.2f}")

    hotel_analysis = {}
    for hotel in raw_hotels:
        name = hotel["hotel_name"]
        price = hotel["price_per_night"]
        rating = hotel.get("rating", 4.0)
        
        # Calculate pricing value score:
        # A formula incorporating:
        # 1. Rating (out of 5): higher rating is better
        # 2. Price relative to average: cheaper is better
        price_ratio = avg_price / price if price > 0 else 1.0
        # Clamp ratio to prevent extreme outliers
        price_ratio = min(max(price_ratio, 0.5), 2.0) 
        
        # Calculate score (1 to 10 scale)
        rating_component = (rating / 5.0) * 10.0
        price_component = price_ratio * 5.0
        value_score = round(0.5 * rating_component + 0.5 * price_component, 1)
        value_score = min(max(value_score, 1.0), 10.0)
        
        # Calculate savings relative to budget limit or average price
        savings = max(0.0, budget_limit - price)
        is_deal = price < avg_price
        
        hotel_analysis[name] = {
            "value_score": value_score,
            "savings": round(savings, 2),
            "is_deal": is_deal,
            "compared_to_avg_percent": round(((price - avg_price) / avg_price) * 100, 1) if avg_price > 0 else 0.0
        }
        
    metrics = {
        "avg_price": round(avg_price, 2),
        "max_price": round(max_price, 2),
        "min_price": round(min_price, 2),
        "hotel_pricing_analysis": hotel_analysis
    }
    
    log_messages.append(f"Completed pricing analysis for {len(raw_hotels)} properties.")
    
    return {
        "pricing_metrics": metrics,
        "logs": log_messages,
        "errors": errors
    }

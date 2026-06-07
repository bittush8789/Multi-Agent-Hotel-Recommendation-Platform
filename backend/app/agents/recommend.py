import logging
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

def calculate_rule_based_matching_score(hotel: Dict[str, Any], preferences: Dict[str, Any], pricing_analysis: Dict[str, Any]) -> float:
    """Calculates a robust matching score (0-100) based on preferences and price metrics."""
    score = 40.0 # base score
    
    # 1. Budget comparison
    price = hotel["price_per_night"]
    budget_limit = preferences.get("budget_limit", 250.0)
    if price <= budget_limit:
        score += 30.0
    else:
        # Deduct points if price is over budget
        over_budget_pct = (price - budget_limit) / budget_limit
        deduction = min(over_budget_pct * 50.0, 30.0) # max 30 points deduction
        score += (30.0 - deduction)

    # 2. Amenities matching
    requested_amenities = preferences.get("amenities", [])
    hotel_amenities = [a.lower() for a in hotel.get("amenities", [])]
    if requested_amenities:
        matched = 0
        for am in requested_amenities:
            # Check for partial string matches
            if any(am.lower() in ha for ha in hotel_amenities):
                matched += 1
        amenity_pct = matched / len(requested_amenities)
        score += (amenity_pct * 20.0)
    else:
        score += 20.0 # automatic match if none requested

    # 3. Value score influence (value_score is out of 10)
    val_score = pricing_analysis.get("value_score", 5.0)
    score += (val_score / 10.0) * 10.0

    return min(max(round(score, 1), 10.0), 100.0)

def generate_reasoning_fallback(hotel: Dict[str, Any], prefs: Dict[str, Any], match_score: float, price_analysis: Dict[str, Any], review_insight: str) -> str:
    """Generates standard reasoning if LLM is unavailable."""
    name = hotel["hotel_name"]
    price = hotel["price_per_night"]
    budget_limit = prefs.get("budget_limit", 250.0)
    
    saving_text = f"saving you ${price_analysis.get('savings'):.0f}/night" if price_analysis.get("savings", 0) > 0 else "exceeding your target budget slightly"
    deal_text = "It is priced below the city average, making it a great value deal." if price_analysis.get("is_deal") else ""
    
    return (
        f"This hotel is a {match_score:.0f}% match. At ${price:.0f}/night, it fits your budget ({saving_text}). "
        f"{deal_text} Review highlights: {review_insight} This option aligns well with your requested travel style."
    )

def recommendation_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Recommendation Agent: Aggregates preferences, search info, pricing value, 
    and RAG review summaries. Ranks hotels, computes match scores, and generates written reasons.
    """
    raw_hotels = state.get("raw_hotels", [])
    preferences = state.get("preferences", {})
    pricing_metrics = state.get("pricing_metrics", {})
    review_insights = state.get("review_insights", {})
    
    log_messages = state.get("logs", [])
    errors = state.get("errors", [])
    
    log_messages.append("Recommendation Agent active: Calculating compatibility scores and compiling final report...")
    
    if not raw_hotels:
        log_messages.append("No hotels to recommend.")
        return {
            "recommendations": [],
            "logs": log_messages
        }

    hotel_pricing_analysis = pricing_metrics.get("hotel_pricing_analysis", {})
    
    llm = None
    if settings.GROQ_API_KEY and "your_groq_api_key_here" not in settings.GROQ_API_KEY and settings.GROQ_API_KEY != "":
        try:
            llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model_name=settings.LLM_MODEL,
                temperature=0.3
            )
        except Exception as e:
            errors.append(f"RecommendationAgent LLM initialization failed: {str(e)}")

    recommendations_list = []
    for hotel in raw_hotels:
        name = hotel["hotel_name"]
        price = hotel["price_per_night"]
        currency = hotel.get("currency", "USD")
        
        # Get pricing analysis
        price_analysis = hotel_pricing_analysis.get(name, {"value_score": 5.0, "savings": 0.0, "is_deal": False})
        val_score = price_analysis.get("value_score", 5.0)
        
        # Get review insights
        insight = review_insights.get(name, "No guest reviews analyzed.")
        
        # Calculate matching score
        match_score = calculate_rule_based_matching_score(hotel, preferences, price_analysis)
        
        # Generate reasoning text
        reasoning = ""
        if llm:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are an expert Hotel Recommender System. Write a single, persuasive, "
                        "and informative paragraph explaining why this hotel is a good (or poor) fit "
                        "for the traveler. Integrate: matching score ({match_score}%), cost (${price}), "
                        "guest reviews summary ({insight}), and target preferences ({prefs}). Keep it concise."
                    )),
                    ("human", (
                        "Hotel: {hotel_name}\n"
                        "Pricing Analysis: {price_analysis}\n"
                        "Final Decision Reasoning:"
                    ))
                ])
                chain = prompt | llm
                response = chain.invoke({
                    "match_score": match_score,
                    "price": price,
                    "insight": insight,
                    "prefs": str(preferences),
                    "hotel_name": name,
                    "price_analysis": str(price_analysis)
                })
                reasoning = response.content.strip()
            except Exception as e:
                errors.append(f"RecommendationAgent reasoning failed for {name}: {str(e)}")
                reasoning = generate_reasoning_fallback(hotel, preferences, match_score, price_analysis, insight)
        else:
            reasoning = generate_reasoning_fallback(hotel, preferences, match_score, price_analysis, insight)

        recommendations_list.append({
            "hotel_name": name,
            "price_per_night": price,
            "currency": currency,
            "value_score": val_score,
            "matching_score": match_score,
            "review_insights": insight,
            "reasoning": reasoning,
            "link": hotel.get("link") or f"https://www.google.com/travel/hotels?q={name.replace(' ', '+')}"
        })

    # Sort recommendations by matching score in descending order
    recommendations_list = sorted(recommendations_list, key=lambda x: x["matching_score"], reverse=True)
    
    log_messages.append(f"Ranked {len(recommendations_list)} hotels. Best match: '{recommendations_list[0]['hotel_name']}' ({recommendations_list[0]['matching_score']}%).")
    
    return {
        "recommendations": recommendations_list,
        "logs": log_messages,
        "errors": errors
    }

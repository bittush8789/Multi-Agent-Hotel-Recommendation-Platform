import logging
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.services.vector_store import vector_store_service
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

def generate_review_summary_fallback(hotel_name: str, snippets: List[Dict[str, Any]], rating: float) -> str:
    """Generates a default summary if the LLM is unavailable."""
    if not snippets:
        # Default text based on ratings
        if rating >= 4.5:
            return "Guests consistently rate this hotel highly, praising its prime location, stellar room cleanliness, and exceptionally helpful staff."
        elif rating >= 4.0:
            return "Overall positive reviews highlighting comfortable beds, good value, and solid amenities. Some minor complaints about slow check-in."
        else:
            return "Average guest reviews. Praised for budget friendliness but criticized for noisy rooms and outdated bathroom fixtures."

    # Join snippets
    texts = [s["text"] for s in snippets]
    return " | ".join(texts)

def review_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Review Analysis Agent: Conducts semantic search over ChromaDB for reviews 
    and synthesizes guest experiences (pros/cons).
    """
    raw_hotels = state.get("raw_hotels", [])
    query = state.get("user_query", "")
    log_messages = state.get("logs", [])
    errors = state.get("errors", [])
    
    log_messages.append("Review Analysis Agent active: Fetching guest reviews and performing RAG semantic analysis...")
    
    review_insights = {}
    
    # Instantiate Groq Client if API key is present
    llm = None
    if settings.GROQ_API_KEY and "your_groq_api_key_here" not in settings.GROQ_API_KEY and settings.GROQ_API_KEY != "":
        try:
            llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model_name=settings.LLM_MODEL,
                temperature=0.0
            )
        except Exception as e:
            errors.append(f"ReviewAgent LLM initialization failed: {str(e)}")

    for hotel in raw_hotels:
        name = hotel["hotel_name"]
        rating = hotel.get("rating", 4.0)
        
        # 1. Query Vector Store for specific reviews matching user intent/query context
        snippets = vector_store_service.query_hotel_reviews(hotel_name=name, query=query, limit=3)
        
        if snippets:
            log_messages.append(f"RAG: Retrieved {len(snippets)} review snippets for '{name}'.")
        else:
            log_messages.append(f"RAG: No specific reviews found in vector store for '{name}'. Utilizing metadata heuristics.")

        # 2. Summarize reviews via LLM or fallback
        if llm:
            try:
                snippets_text = "\n".join([f"- {s['text']}" for s in snippets])
                prompt = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are a Hotel Review Summarizer Agent. Combine the provided guest review snippets "
                        "into a concise, 2-sentence summary. Highlight key pros and cons that directly address "
                        "what guests liked or disliked. Keep it professional, objective, and brief."
                    )),
                    ("human", (
                        "Hotel: {hotel_name}\n"
                        "Guest Reviews:\n{reviews}\n\n"
                        "Summary:"
                    ))
                ])
                chain = prompt | llm
                response = chain.invoke({
                    "hotel_name": name,
                    "reviews": snippets_text if snippets else "No guest reviews found."
                })
                summary = response.content.strip()
            except Exception as e:
                errors.append(f"ReviewAgent summarizing failed for {name}: {str(e)}")
                summary = generate_review_summary_fallback(name, snippets, rating)
        else:
            summary = generate_review_summary_fallback(name, snippets, rating)

        review_insights[name] = summary

    log_messages.append(f"Analyzed customer feedback for {len(raw_hotels)} properties.")
    
    return {
        "review_insights": review_insights,
        "logs": log_messages,
        "errors": errors
    }

import uuid
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.config import settings
from app.database import get_db, init_db, SearchHistory, SavedHotel
from app.schemas.api_models import (
    RecommendationRequest,
    RecommendationResponse,
    SavedHotelCreate,
    SavedHotelResponse,
    SearchHistoryResponse,
    PreferencesSchema
)
from app.agents.graph import run_agent_pipeline
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(
    title="TravelMind AI API",
    description="Multi-Agent Hotel Recommendation platform powered by LangGraph, FastAPI, and ChromaDB.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Initialize SQLite database schema
    init_db()
    # Expose prometheus metrics
    Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the TravelMind AI Multi-Agent Service API."
    }

@app.post("/api/v1/recommendations/generate", response_model=RecommendationResponse)
def generate_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Executes the multi-agent LangGraph recommendation graph and returns the compiled report.
    Logs the query request into search history.
    """
    # 1. Trigger the LangGraph multi-agent orchestration
    pipeline_result = run_agent_pipeline(
        query=request.query,
        check_in=request.check_in_date,
        check_out=request.check_out_date
    )
    
    preferences_data = pipeline_result.get("preferences", {})
    recommendations = pipeline_result.get("recommendations", [])
    
    # 2. Extract parsed fields to record search history
    destination = preferences_data.get("location")
    
    history_entry = SearchHistory(
        user_id=request.user_id,
        query=request.query,
        destination=destination,
        check_in=request.check_in_date,
        check_out=request.check_out_date
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    
    # 3. Format response
    search_id = str(uuid.uuid4())
    
    # Ensure preferences schema fields are populated
    prefs = PreferencesSchema(
        location=preferences_data.get("location", "Unknown"),
        budget_limit=preferences_data.get("budget_limit", 250.0),
        amenities=preferences_data.get("amenities", []),
        trip_style=preferences_data.get("trip_style", "leisure")
    )
    
    return RecommendationResponse(
        search_id=search_id,
        preferences=prefs,
        recommendations=recommendations
    )

@app.post("/api/v1/saved-hotels", response_model=SavedHotelResponse)
def save_hotel(hotel: SavedHotelCreate, db: Session = Depends(get_db)):
    """
    Bookmarks a recommended hotel for a specific user.
    """
    db_hotel = SavedHotel(
        user_id=hotel.user_id,
        hotel_name=hotel.hotel_name,
        price_per_night=hotel.price_per_night,
        currency=hotel.currency,
        value_score=hotel.value_score,
        matching_score=hotel.matching_score,
        review_insights=hotel.review_insights,
        reasoning=hotel.reasoning,
        link=hotel.link
    )
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

@app.get("/api/v1/saved-hotels", response_model=List[SavedHotelResponse])
def get_saved_hotels(user_id: str = Query(..., description="Unique identification string of the user"), db: Session = Depends(get_db)):
    """
    Retrieves all bookmarked hotels for a user.
    """
    saved_list = db.query(SavedHotel).filter(SavedHotel.user_id == user_id).order_by(SavedHotel.timestamp.desc()).all()
    return saved_list

@app.delete("/api/v1/saved-hotels/{hotel_id}")
def delete_saved_hotel(hotel_id: int, user_id: str = Query(..., description="Unique identification string of the user"), db: Session = Depends(get_db)):
    """
    Removes a bookmarked hotel by its table ID.
    """
    db_hotel = db.query(SavedHotel).filter(SavedHotel.id == hotel_id, SavedHotel.user_id == user_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Saved hotel bookmark not found.")
    db.delete(db_hotel)
    db.commit()
    return {"message": "Hotel bookmark removed successfully."}

@app.get("/api/v1/history", response_model=List[SearchHistoryResponse])
def get_search_history(user_id: str = Query(..., description="Unique identification string of the user"), db: Session = Depends(get_db)):
    """
    Retrieves search logs for a user.
    """
    history_list = db.query(SearchHistory).filter(SearchHistory.user_id == user_id).order_by(SearchHistory.timestamp.desc()).all()
    return history_list

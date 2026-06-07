from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RecommendationRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identification string")
    query: str = Field(..., description="Natural language prompt describing travel/hotel preferences")
    check_in_date: str = Field(..., description="Check-in date formatted as YYYY-MM-DD")
    check_out_date: str = Field(..., description="Check-out date formatted as YYYY-MM-DD")

class PreferencesSchema(BaseModel):
    location: str
    budget_limit: float
    amenities: List[str]
    trip_style: str

class HotelRecommendation(BaseModel):
    hotel_name: str
    price_per_night: float
    currency: str = "USD"
    value_score: float = Field(..., description="Score 1-10 evaluated by the pricing analysis agent")
    matching_score: float = Field(..., description="Percentage match out of 100 based on preferences")
    review_insights: str = Field(..., description="Summarized review feedback pros and cons")
    reasoning: str = Field(..., description="Qualitative agent reasoning explaining the score")
    link: Optional[str] = Field(default=None, description="Direct web link to book or view details of the hotel")

class RecommendationResponse(BaseModel):
    search_id: str
    preferences: PreferencesSchema
    recommendations: List[HotelRecommendation]

class SavedHotelCreate(BaseModel):
    user_id: str
    hotel_name: str
    price_per_night: Optional[float] = None
    currency: str = "USD"
    value_score: Optional[float] = None
    matching_score: Optional[float] = None
    review_insights: Optional[str] = None
    reasoning: Optional[str] = None
    link: Optional[str] = None

class SavedHotelResponse(BaseModel):
    id: int
    user_id: str
    hotel_name: str
    price_per_night: Optional[float]
    currency: str
    value_score: Optional[float]
    matching_score: Optional[float]
    review_insights: Optional[str]
    reasoning: Optional[str]
    link: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class SearchHistoryResponse(BaseModel):
    id: int
    user_id: str
    query: str
    destination: Optional[str]
    check_in: Optional[str]
    check_out: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

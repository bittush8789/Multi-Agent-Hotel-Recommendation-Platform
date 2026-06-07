import requests
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class SerpAPIService:
    def __init__(self):
        self.api_key = settings.SERPAPI_API_KEY
        self.base_url = "https://serpapi.com/search.json"

    def search_hotels(self, destination: str, check_in: str, check_out: str) -> List[Dict[str, Any]]:
        """
        Search hotels via SerpAPI google_hotels engine.
        If API key is dummy/missing, or on error, falls back to a generated mock list of hotels
        for that destination.
        """
        # If API key is not set or is placeholder, fall back to mock data
        if not self.api_key or "your_serpapi_api_key_here" in self.api_key or self.api_key == "":
            logger.warning("SerpAPI key not configured. Falling back to mock data.")
            return self._generate_mock_hotels(destination)

        params = {
            "engine": "google_hotels",
            "q": f"hotels in {destination}",
            "check_in_date": check_in,
            "check_out_date": check_out,
            "api_key": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Parse results
            properties = data.get("properties", [])
            if not properties:
                logger.warning(f"No hotels found in SerpAPI response for {destination}. Falling back to mock.")
                return self._generate_mock_hotels(destination)

            hotels_list = []
            for prop in properties:
                # Extract pricing details
                rate_info = prop.get("rate_per_night", {})
                price = rate_info.get("extracted_lowest") or rate_info.get("lowest")
                if isinstance(price, str):
                    # parse "$120" -> 120
                    price = float(price.replace("$", "").replace(",", "").strip())
                elif price is None:
                    price = 150.0 # fallback default price
                else:
                    price = float(price)

                # Extract amenities (which can be list of strings or list of objects)
                raw_amenities = prop.get("amenities", [])
                amenities = []
                for am in raw_amenities:
                    if isinstance(am, str):
                        amenities.append(am)
                    elif isinstance(am, dict) and "name" in am:
                        amenities.append(am["name"])

                hotel = {
                    "hotel_name": prop.get("name", "Unknown Hotel"),
                    "price_per_night": price,
                    "currency": "USD",
                    "rating": prop.get("overall_rating", 4.0),
                    "reviews_count": prop.get("reviews", 10),
                    "amenities": amenities if amenities else ["Free Wi-Fi", "Air Conditioning"],
                    "description": prop.get("description", f"A beautiful property located in the heart of {destination}."),
                    "thumbnail": prop.get("thumbnail", ""),
                    "link": prop.get("link") or f"https://www.google.com/travel/hotels?q={prop.get('name', '').replace(' ', '+')}"
                }
                hotels_list.append(hotel)

            return hotels_list

        except Exception as e:
            logger.error(f"Error fetching from SerpAPI: {str(e)}. Falling back to mock data.")
            return self._generate_mock_hotels(destination)

    def _generate_mock_hotels(self, destination: str) -> List[Dict[str, Any]]:
        """Generates realistic mock hotel data for safety fallback."""
        destination_clean = destination.title()
        return [
            {
                "hotel_name": f"{destination_clean} Grand Plaza & Spa",
                "price_per_night": 240.0,
                "currency": "USD",
                "rating": 4.7,
                "reviews_count": 342,
                "amenities": ["Free Wi-Fi", "Spa", "Pool", "Fitness Center", "Restaurant", "Bar"],
                "description": f"Luxury hotel offering premier service and spa facilities in downtown {destination_clean}.",
                "thumbnail": "",
                "link": f"https://www.google.com/travel/hotels?q={destination_clean}+Grand+Plaza+and+Spa"
            },
            {
                "hotel_name": f"Boutique Haven {destination_clean}",
                "price_per_night": 180.0,
                "currency": "USD",
                "rating": 4.5,
                "reviews_count": 198,
                "amenities": ["Free Wi-Fi", "Breakfast Included", "Bicycle Rental", "Air Conditioning"],
                "description": f"A charming, intimate boutique experience close to local cultural spots in {destination_clean}.",
                "thumbnail": "",
                "link": f"https://www.google.com/travel/hotels?q=Boutique+Haven+{destination_clean}"
            },
            {
                "hotel_name": f"Budget Inn {destination_clean}",
                "price_per_night": 85.0,
                "currency": "USD",
                "rating": 3.9,
                "reviews_count": 512,
                "amenities": ["Free Wi-Fi", "Air Conditioning", "Free Parking"],
                "description": f"Affordable lodging featuring clean, basic rooms located conveniently near transit in {destination_clean}.",
                "thumbnail": "",
                "link": f"https://www.google.com/travel/hotels?q=Budget+Inn+{destination_clean}"
            },
            {
                "hotel_name": f"{destination_clean} Sanctuary Resort",
                "price_per_night": 390.0,
                "currency": "USD",
                "rating": 4.9,
                "reviews_count": 87,
                "amenities": ["Free Wi-Fi", "Private Beach/Garden", "Spa", "All Inclusive", "Room Service"],
                "description": f"Premium, secluded retreat offering world-class services and custom tours around {destination_clean}.",
                "thumbnail": "",
                "link": f"https://www.google.com/travel/hotels?q={destination_clean}+Sanctuary+Resort"
            },
            {
                "hotel_name": f"Business Suite {destination_clean}",
                "price_per_night": 145.0,
                "currency": "USD",
                "rating": 4.2,
                "reviews_count": 250,
                "amenities": ["Free Wi-Fi", "Meeting Rooms", "Laundry Service", "Airport Shuttle"],
                "description": f"Modern business hotel offering workspaces and high-speed connectivity in {destination_clean}.",
                "thumbnail": "",
                "link": f"https://www.google.com/travel/hotels?q=Business+Suite+{destination_clean}"
            }
        ]
# Export singleton
serpapi_service = SerpAPIService()

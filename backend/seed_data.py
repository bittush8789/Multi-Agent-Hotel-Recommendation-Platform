import sys
import os

# Append current directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
from app.services.vector_store import vector_store_service

def seed_reviews():
    print("Initializing SQLite Database tables...")
    init_db()
    print("Database tables initialized successfully.")

    print("Clearing and populating ChromaDB reviews vector store...")
    vector_store_service.clear_database()

    destinations = ["Kyoto", "Seattle", "Miami", "San Francisco", "New York"]
    
    # Generate realistic guest reviews for each mock hotel in each destination
    for city in destinations:
        print(f"Seeding reviews for {city} hotels...")
        
        # 1. Grand Plaza & Spa
        grand_plaza_reviews = [
            f"The on-site thermal spa at {city} Grand Plaza was absolutely therapeutic. The mineral pools are world-class.",
            f"Exceptional hospitality and room service. The panoramic view of {city} from our suite was stunning.",
            f"A premium stay but expensive. The restaurant food was exquisite, though spa appointments must be booked days in advance.",
            "Loved the state-of-the-art gym and large indoor swimming pool. Everything was immaculately clean.",
            "The front desk staff greeted us with complimentary drinks. A truly luxurious experience."
        ]
        vector_store_service.add_reviews(f"{city} Grand Plaza & Spa", grand_plaza_reviews)

        # 2. Boutique Haven
        boutique_haven_reviews = [
            f"Boutique Haven {city} is an absolute gem. Quiet rooms, bespoke local art, and charming wooden architecture.",
            f"Rented bicycles from the front desk and explored the historic district nearby. Perfectly located.",
            "The room was cozy and charming, though a bit compact. The complimentary home-style breakfast was delicious.",
            f"A quiet retreat tucked away from the noisy main streets of {city}. Great coffee shop right next door.",
            "The staff was incredibly welcoming and gave us a custom map of local dining secrets."
        ]
        vector_store_service.add_reviews(f"Boutique Haven {city}", boutique_haven_reviews)

        # 3. Budget Inn
        budget_inn_reviews = [
            f"Simple, clean, and extremely affordable. Literally right next to the {city} transit line, making navigation simple.",
            "Rooms are small and basic, but perfect if you are just looking for a cheap place to sleep and shower.",
            "Wi-Fi was fast and free parking was a huge bonus. A bit noisy since it faces a major road.",
            "No luxury bells and whistles here, but the air conditioning worked perfectly and beds were comfortable.",
            "Excellent budget value for backpackers and solo travelers who want to save money."
        ]
        vector_store_service.add_reviews(f"Budget Inn {city}", budget_inn_reviews)

        # 4. Sanctuary Resort
        sanctuary_resort_reviews = [
            f"A breathtaking, ultra-private sanctuary resort in {city}. The gardens and private outdoor bathtubs are magical.",
            "Impeccable five-star service. They arranged a private local tour guide for us. Pure luxury.",
            "Incredible tranquility and peace. Perfect for honeymoons or milestone events. Worth the massive price tag.",
            "The dining experience was Michelin-level. Local ingredients and custom wine pairings served in our villa.",
            "Secluded, quiet, and completely away from crowds. The wellness treatments were exceptional."
        ]
        vector_store_service.add_reviews(f"{city} Sanctuary Resort", sanctuary_resort_reviews)

        # 5. Business Suite
        business_suite_reviews = [
            f"Highly efficient business hotel in {city}. Excellent workspace in the room and reliable high-speed Wi-Fi.",
            "Close to the convention center and financial offices. The meeting rooms were easy to reserve.",
            "Clean and comfortable rooms with a great breakfast buffet. Gym was open 24 hours.",
            "The airport shuttle was on time and very convenient. Good desk setup with plenty of power outlets.",
            "Ideal hotel for business travelers or digital nomads looking to stay productive on the road."
        ]
        vector_store_service.add_reviews(f"Business Suite {city}", business_suite_reviews)

    print("ChromaDB vector store seeding completed successfully!")

if __name__ == "__main__":
    seed_reviews()

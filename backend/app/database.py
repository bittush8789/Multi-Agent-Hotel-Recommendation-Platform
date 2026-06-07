from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Setup SQLAlchemy engine and session
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    query = Column(Text, nullable=False)
    destination = Column(String(100), nullable=True)
    check_in = Column(String(50), nullable=True)
    check_out = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SavedHotel(Base):
    __tablename__ = "saved_hotels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    hotel_name = Column(String(200), nullable=False)
    price_per_night = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    value_score = Column(Float, nullable=True)
    matching_score = Column(Float, nullable=True)
    review_insights = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    link = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database helper to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
    # Automated migration: add 'link' column if it does not exist
    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE saved_hotels ADD COLUMN link TEXT;"))
    except Exception:
        pass

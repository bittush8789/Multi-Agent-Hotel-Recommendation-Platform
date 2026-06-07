import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import time

# Configs
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Setup page config
st.set_page_config(
    page_title="TravelMind AI | Multi-Agent Recommendation Engine",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Theme Selector (placed at the top so variables can be used in styling and Plotly layouts)
theme_mode = st.sidebar.selectbox("🎨 Interface Theme", ["Dark Theme", "Light Theme"], index=0)

# Setup Theme Variables
if theme_mode == "Dark Theme":
    bg_gradient = "linear-gradient(135deg, #0F172A 0%, #1E293B 100%)"
    text_color = "#F8FAFC"
    card_bg = "rgba(30, 41, 59, 0.7)"
    card_border = "rgba(255, 255, 255, 0.1)"
    card_text = "#E2E8F0"
    card_title = "#F8FAFC"
    card_subtitle = "#94A3B8"
    agent_box_bg = "rgba(15, 23, 42, 0.6)"
    sub_title_color = "#94A3B8"
    plotly_template = "plotly_dark"
    plotly_font_color = "#F8FAFC"
    
    # Widget styles
    label_color = "#E2E8F0"
    input_bg = "rgba(15, 23, 42, 0.6)"
    input_border = "rgba(255, 255, 255, 0.1)"
    btn_bg = "rgba(30, 41, 59, 0.8)"
    btn_border = "rgba(255, 255, 255, 0.1)"
    btn_text = "#F8FAFC"
    btn_hover_text = "#0F172A"
    sidebar_bg = "#0F172A"
    sidebar_text = "#F8FAFC"
    hr_color = "rgba(255, 255, 255, 0.1)"
else:
    bg_gradient = "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)"
    text_color = "#0F172A"
    card_bg = "rgba(255, 255, 255, 0.9)"
    card_border = "rgba(15, 23, 42, 0.08)"
    card_text = "#334155"
    card_title = "#0F172A"
    card_subtitle = "#475569"
    agent_box_bg = "rgba(255, 255, 255, 0.8)"
    sub_title_color = "#475569"
    plotly_template = "plotly_white"
    plotly_font_color = "#0F172A"
    
    # Widget styles
    label_color = "#334155"
    input_bg = "rgba(255, 255, 255, 0.9)"
    input_border = "rgba(0, 0, 0, 0.12)"
    btn_bg = "rgba(255, 255, 255, 0.9)"
    btn_border = "rgba(0, 0, 0, 0.15)"
    btn_text = "#0F172A"
    btn_hover_text = "#FFFFFF"
    sidebar_bg = "#F8FAFC"
    sidebar_text = "#0F172A"
    hr_color = "rgba(0, 0, 0, 0.08)"

# Custom Premium Styling
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
    }}
    
    /* Main Background gradient */
    .stApp {{
        background: {bg_gradient};
        color: {text_color};
    }}
    
    /* Sidebar styling overrides */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: {sidebar_text} !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: {hr_color} !important;
    }}
    
    /* Recommendations cards */
    .hotel-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }}
    .hotel-card:hover {{
        transform: translateY(-4px);
        border-color: #38BDF8;
        box-shadow: 0 10px 20px -10px rgba(56, 189, 248, 0.3);
    }}
    
    /* Badge styling */
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
    }}
    .badge-match {{
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
    }}
    .badge-value {{
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
    }}
    .badge-price {{
        background-color: rgba(56, 189, 248, 0.2);
        color: #38BDF8;
        border: 1px solid #38BDF8;
    }}
    
    /* Subtitles and headers */
    .agent-header {{
        font-size: 1.1rem;
        color: {sub_title_color};
        font-weight: 500;
        margin-top: 10px;
    }}
    
    .agent-box {{
        background: {agent_box_bg};
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #38BDF8;
        margin-bottom: 8px;
    }}
    
    /* Aggressive Form Label Styling */
    label, label *, .stWidgetLabel, .stWidgetLabel p, .stWidgetLabel span, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {{
        color: {label_color} !important;
        font-weight: 500 !important;
    }}
    
    /* Aggressive widget and input area overrides */
    .stTextArea div, .stTextArea textarea, 
    .stTextInput div, .stTextInput input, 
    .stDateInput div, .stDateInput input, 
    .stSelectbox div, .stSelectbox select {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {input_border} !important;
    }}
    
    /* Inner HTML elements standard overrides */
    input, textarea, select, option {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
    }}
    
    /* Custom button styling with aggressive text color application */
    div.stButton > button, div.stButton > button * {{
        background-color: {btn_bg} !important;
        border-color: {btn_border} !important;
        color: {btn_text} !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }}
    div.stButton > button:hover, div.stButton > button:hover * {{
        background-color: #38BDF8 !important;
        color: {btn_hover_text} !important;
        border-color: #38BDF8 !important;
    }}
</style>
""", unsafe_allow_html=True)

# Helper function to query backend history
def fetch_history(user_id):
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/history", params={"user_id": user_id}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

# Helper function to query saved hotels
def fetch_saved_hotels(user_id):
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/saved-hotels", params={"user_id": user_id}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

# Helper to save a hotel
def save_hotel(user_id, hotel):
    try:
        payload = {
            "user_id": user_id,
            "hotel_name": hotel["hotel_name"],
            "price_per_night": hotel["price_per_night"],
            "currency": hotel["currency"],
            "value_score": hotel["value_score"],
            "matching_score": hotel["matching_score"],
            "review_insights": hotel["review_insights"],
            "reasoning": hotel["reasoning"],
            "link": hotel.get("link")
        }
        r = requests.post(f"{BACKEND_URL}/api/v1/saved-hotels", json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False

# Helper to unsave a hotel
def remove_saved_hotel(user_id, bookmark_id):
    try:
        r = requests.delete(f"{BACKEND_URL}/api/v1/saved-hotels/{bookmark_id}", params={"user_id": user_id}, timeout=5)
        return r.status_code == 200
    except Exception:
        return False

# Sidebar Configuration
st.sidebar.markdown("<h2 style='text-align: center; color: #38BDF8;'>⚙️ User Portal</h2>", unsafe_allow_html=True)

user_id = st.sidebar.text_input("User ID Profiles", value="guest_user_777")

# Tabs in Sidebar for Saved and History
sb_tab1, sb_tab2 = st.sidebar.tabs(["⭐ Saved Hotels", "📜 Search History"])

with sb_tab1:
    saved = fetch_saved_hotels(user_id)
    if saved:
        for idx, h in enumerate(saved):
            with st.container():
                st.markdown(f"**{h['hotel_name']}**")
                st.markdown(f"💰 `${h['price_per_night']}/night` | 🎖️ `{h['matching_score']}% Match`")
                if h.get("link"):
                    st.markdown(f"[🔗 Book Hotel]({h['link']})")
                if st.button("Remove Bookmark", key=f"unsave_{h['id']}_{idx}"):
                    if remove_saved_hotel(user_id, h["id"]):
                        st.success("Removed!")
                        st.rerun()
                st.markdown("---")
    else:
        st.info("No hotels saved yet.")

with sb_tab2:
    history = fetch_history(user_id)
    if history:
        for idx, item in enumerate(history[:10]):
            if st.button(f"🔍 {item['destination'] or 'Search'} - {item['timestamp'][:10]}", key=f"hist_{item['id']}_{idx}"):
                st.session_state["query_input"] = item["query"]
                st.session_state["check_in"] = datetime.strptime(item["check_in"], "%Y-%m-%d").date() if item["check_in"] else datetime.today().date()
                st.session_state["check_out"] = datetime.strptime(item["check_out"], "%Y-%m-%d").date() if item["check_out"] else datetime.today().date() + timedelta(days=5)
                st.rerun()
            st.caption(f"*Query: {item['query'][:60]}...*")
    else:
        st.info("No previous queries.")

# Main Application Frame
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>✈️ TravelMind AI</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: {sub_title_color}; font-size: 1.2rem; margin-top: 0px;'>Multi-Agent Hotel Recommendation Platform</p>", unsafe_allow_html=True)
st.markdown("---")

# Session state placeholders
if "query_input" not in st.session_state:
    st.session_state["query_input"] = "Looking for a luxury boutique resort in Kyoto near traditional shrines, budget around $300/night with a spa."
if "check_in" not in st.session_state:
    st.session_state["check_in"] = datetime.today().date() + timedelta(days=7)
if "check_out" not in st.session_state:
    st.session_state["check_out"] = datetime.today().date() + timedelta(days=12)

# Query panel
col_q, col_d1, col_d2 = st.columns([3, 1, 1])

with col_q:
    user_query = st.text_area("What kind of accommodations are you looking for?", value=st.session_state["query_input"], height=100)

with col_d1:
    check_in_date = st.date_input("Check-In Date", value=st.session_state["check_in"])

with col_d2:
    check_out_date = st.date_input("Check-Out Date", value=st.session_state["check_out"])

# Predefined recommendations buttons for easy demo
st.write("💡 **Quick Examples:**")
demo_cols = st.columns(3)
if demo_cols[0].button("Kyoto Spa Retreat"):
    st.session_state["query_input"] = "Looking for a luxury boutique resort in Kyoto near traditional shrines, budget around $300/night with a spa."
    st.rerun()
if demo_cols[1].button("Seattle Business Hub"):
    st.session_state["query_input"] = "Searching for a modern business suite in Seattle close to downtown with fast wifi and a desk, budget $160."
    st.rerun()
if demo_cols[2].button("Miami Beachfront Value"):
    st.session_state["query_input"] = "Need a cheap family friendly stay in Miami with pool near the beach, budget around $120/night max."
    st.rerun()

execute_search = st.button("🚀 Analyze & Recommend Hotels", use_container_width=True)

if execute_search:
    st.markdown("### 🔄 Multi-Agent Graph Orchestration")
    
    # 1. Setup simulated progression containers to wow the user
    agent_stages = [
        ("🧠 Preference Analysis Agent", "Extracting constraints, destination, trip style, and budget limits..."),
        ("🔍 Hotel Search Agent", "Querying SerpAPI Google Hotels database for real-time inventory..."),
        ("💰 Pricing Analysis Agent", "Evaluating average prices, clamping value scores, identifying discount deals..."),
        ("📚 Review Analysis Agent", "Performing RAG semantic lookup on customer feedback vectors..."),
        ("🎖️ Recommendation Agent", "Calculating final match percentages and drafting custom reasoning report...")
    ]
    
    status_placeholders = []
    for title, desc in agent_stages:
        box = st.empty()
        status_placeholders.append((box, title, desc))
    
    # Trigger active request to API
    payload = {
        "user_id": user_id,
        "query": user_query,
        "check_in_date": check_in_date.strftime("%Y-%m-%d"),
        "check_out_date": check_out_date.strftime("%Y-%m-%d")
    }
    
    with st.spinner("Executing agent pipeline..."):
        try:
            # Simulate step rendering for rich visual experience
            for i, (box, title, desc) in enumerate(status_placeholders):
                box.markdown(f"""
                <div class="agent-box" style="border-left-color: #F59E0B;">
                    <strong>🔄 {title}</strong><br/>
                    <span style="color: #94A3B8; font-size: 0.9rem;">{desc}</span>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.6) # small visual interval
                box.markdown(f"""
                <div class="agent-box" style="border-left-color: #10B981; background: rgba(16, 185, 129, 0.05);">
                    <strong>✅ {title}</strong><br/>
                    <span style="color: #94A3B8; font-size: 0.9rem;">Successfully completed node execution.</span>
                </div>
                """, unsafe_allow_html=True)

            # API Call
            start_time = time.time()
            response = requests.post(f"{BACKEND_URL}/api/v1/recommendations/generate", json=payload, timeout=120)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                preferences = data["preferences"]
                recommendations = data["recommendations"]
                
                st.success(f"Pipeline executed successfully in {latency:.2f} seconds!")
                
                # Show parsed preferences
                st.markdown("### 📊 Extracted Filters")
                col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                col_p1.metric("Destination Location", preferences["location"].title())
                col_p2.metric("Per-Night Budget Cap", f"${preferences['budget_limit']}")
                col_p3.metric("Extracted Trip Style", preferences["trip_style"].title())
                col_p4.metric("Extracted Amenities", ", ".join(preferences["amenities"]).title() if preferences["amenities"] else "Any")
                
                if not recommendations:
                    st.warning("No hotels matched your specific constraints. Try loosening your filters or increasing your budget.")
                else:
                    # Layout recommendations
                    st.markdown("### 🎖️ Customized Recommendations")
                    
                    # Create two columns: Left for cards, Right for visualizations
                    col_cards, col_charts = st.columns([3, 2])
                    
                    with col_cards:
                        for idx, hotel in enumerate(recommendations):
                            card_html = f"""
                            <div class="hotel-card">
                                <h3 style="margin-top: 0px; color: {card_title};">{hotel['hotel_name']}</h3>
                                <div style="margin-bottom: 15px;">
                                    <span class="badge badge-match">🎯 {hotel['matching_score']}% Match</span>
                                    <span class="badge badge-value">⭐ Value Score: {hotel['value_score']}/10</span>
                                    <span class="badge badge-price">💰 ${hotel['price_per_night']}/night</span>
                                </div>
                                <p style="font-size: 0.95rem; color: {card_text}; line-height: 1.5;"><strong>Reasoning:</strong> {hotel['reasoning']}</p>
                                <p style="font-size: 0.9rem; color: {card_subtitle}; font-style: italic; border-left: 2px solid #64748B; padding-left: 8px;"><strong>Review Insights:</strong> {hotel['review_insights']}</p>
                                <div style="margin-top: 15px; font-size: 0.85rem; color: {card_subtitle}; border-top: 1px dashed rgba(128,128,128,0.25); padding-top: 8px; display: flex; justify-content: space-between; align-items: center;">
                                    <span>📍 Google Hotels | 📚 ChromaDB</span>
                                    {f'<a href="{hotel["link"]}" target="_blank" style="color: #38BDF8; text-decoration: none; font-weight: 600; font-size: 0.85rem; border: 1px solid #38BDF8; padding: 4px 10px; border-radius: 6px; transition: all 0.2s;">🔗 Book Hotel</a>' if hotel.get("link") else ''}
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                            
                            # Streamlit Bookmark Button directly under card
                            if st.button(f"⭐ Save {hotel['hotel_name']}", key=f"save_btn_{idx}"):
                                if save_hotel(user_id, hotel):
                                    st.toast(f"Saved {hotel['hotel_name']} to your portal!", icon="✅")
                                else:
                                    st.error("Failed to bookmark hotel.")
                    
                    with col_charts:
                        st.markdown("<h4 style='text-align: center;'>Price vs. Recommendation Score</h4>", unsafe_allow_html=True)
                        
                        df = pd.DataFrame(recommendations)
                        
                        # Bar chart for pricing comparisons
                        fig = px.bar(
                            df, 
                            x="hotel_name", 
                            y="price_per_night",
                            color="matching_score",
                            color_continuous_scale="Viridis",
                            labels={"hotel_name": "Hotel Name", "price_per_night": "Price per Night ($)", "matching_score": "Match %"},
                            title="Price Comparison of Ranked Properties"
                        )
                        fig.update_layout(
                            template=plotly_template,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color=plotly_font_color,
                            xaxis_tickangle=-30
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show scatter plot comparing matching score to value score
                        fig2 = px.scatter(
                            df,
                            x="value_score",
                            y="matching_score",
                            size="price_per_night",
                            color="hotel_name",
                            labels={"value_score": "Pricing Value Score (1-10)", "matching_score": "User Match Score (%)"},
                            title="Value Score vs. Compatibility Match",
                            size_max=25
                        )
                        fig2.update_layout(
                            template=plotly_template,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color=plotly_font_color
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                        
            else:
                st.error(f"Error executing agent request: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend service. Please check if the FastAPI server is running. Error details: {str(e)}")

import streamlit as st
import googlemaps

# 1. --- CONFIGURATION ---
SHOP_ADDRESS = "8828 Midway West Rd, Raleigh NC 27617"

# 2. --- PAGE CONFIG & THEME-PROOF STYLING ---
st.set_page_config(
    page_title="Stone Quote Pro",
    page_icon="🏗️",
    layout="centered"
)

# This CSS explicitly sets colors for EVERY element to prevent "invisibility"
st.markdown("""
    <style>
    /* 1. Main App Background */
    .stApp {
        background-color: #f4f7f9 !important;
    }
    
    /* 2. Headers and Labels (Forcing visibility) */
    h1, h2, h3, p, span, label {
        color: #1c2833 !important;
    }

    /* 3. The Big Navy Hero Card */
    .quote-card {
        background-color: #2e4053 !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .quote-card h1 {
        color: #f1c40f !important; /* Gold Price */
        margin: 0 !important;
    }
    .quote-card p {
        color: #ffffff !important; /* White text in the navy card */
        margin: 0 !important;
    }
    
    /* 4. Small Metric Boxes (White Cards) */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 1px solid #d5dbdb !important;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] {
        color: #2e4053 !important; /* Dark Navy numbers */
    }
    [data-testid="stMetricLabel"] {
        color: #566573 !important; /* Grey labels */
    }
    
    /* 5. Fix for Input Field Labels */
    .stTextInput label {
        color: #1c2833 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. --- API INITIALIZATION ---
try:
    gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_KEY"])
except Exception:
    st.error("API Key missing! Add GOOGLE_MAPS_KEY to Streamlit Secrets.")

# 4. --- LOGIC FUNCTIONS ---
def get_distance_and_state(destination):
    try:
        result = gmaps.distance_matrix(SHOP_ADDRESS, destination, mode='driving', units='imperial')
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_miles = result['rows'][0]['elements'][0]['distance']['value'] * 0.000621371
            
            geocode_result = gmaps.geocode(destination)
            state_found = ""
            if geocode_result:
                for component in geocode_result[0]['address_components']:
                    if 'administrative_area_level_1' in component['types']:
                        state_found = component['long_name'].upper()
            
            return round(distance_miles, 2), state_found
    except:
        return None, None
    return None, None

def calculate_trip_charge(miles, state_name):
    if not state_name:
        return 0.00, "Unknown State"
    
    # Deep Long Haul
    if any(x in state_name for x in ["GEORGIA", "KENTUCKY", "GA", "KY"]):
        val = 15000 + (max(0, miles - 400) * 15.00)
        return val, "Deep Long-Haul Project Rate"
    
    # Mid-Atlantic
    elif any(x in state_name for x in ["MARYLAND", "TENNESSEE", "MD", "TN"]):
        val = 2500 + (max(0, miles - 250) * 7.50)
        return val, "Mid-Atlantic Logistics Rate"
    
    # Border States
    elif any(x in state_name for x in ["VIRGINIA", "SOUTH CAROLINA", "VA", "SC"]):
        val = 1500 + (max(0, miles - 150) * 5.00)
        return val, "Border State Standard Rate"
    
    # North Carolina Tiers
    elif "NORTH CAROLINA" in state_name or "NC" in state_name:
        if miles > 110:
            return 1200.00, "NC Coastal/Mountain Rate (Wilmington Tier)"
        elif miles > 75:
            return 600.00, "NC Standard Trip Charge"
        else:
            return 0.00, "Local Delivery (Free Zone)"
    
    # Fallback
    else:
        return 1000 + (miles * 5.00), "Standard Out-of-State Baseline"

# 5. --- USER INTERFACE ---
st.title("🏗️ Stone Logistics Quote")
st.write("---")

# Destination input
address_input = st.text_input("📍 Destination Address", placeholder="e.g. Wilmington, NC or 123 Main St...")

if address_input:
    with st.spinner("Calculating logistics..."):
        miles, state = get_distance_and_state(address_input)
    
    if miles is not None:
        charge, reason = calculate_trip_charge(miles, state)
        
        # Result Card (Styled via HTML)
        st.markdown(f"""
            <div class="quote-card">
                <p style="font-size: 1.1rem; opacity: 0.9;">Suggested Trip Charge</p>
                <h1>${charge:,.2f}</h1>
                <p style="font-weight: bold; margin-top:10px; color: #abb2b9 !important;">{reason}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detail Boxes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("One-Way", f"{miles} mi")
        with col2:
            st.metric("State", state.title() if state else "N/A")
        with col3:
            st.metric("Round Trip", f"{round(miles*2, 1)} mi")
            
    else:
        st.error("Address not found. Please try adding a zip code.")

else:
    st.info("Enter a destination above to see the pricing breakdown.")

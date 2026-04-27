import streamlit as st
import googlemaps

# Configuration
SHOP_ADDRESS = "8828 Midway West Rd, Raleigh NC 27617"

# --- Page Config ---
st.set_page_config(
    page_title="Stone Quote Pro",
    page_icon="🏗️",
    layout="centered"
)

# --- Updated Custom CSS for Visibility ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f4f7f9;
    }
    
    /* The Big Hero Quote Card */
    .quote-card {
        background-color: #2e4053;
        color: #f1c40f !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* The Metric Boxes (White Cards) */
    [data-testid="stMetricValue"] {
        color: #1c2833 !important; /* Force dark navy text */
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #566573 !important; /* Force grey label text */
        font-weight: 600 !important;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #d5dbdb;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ... [keep your existing API and calculation functions the same] ...

# --- Updated Detail Columns (Bottom of Script) ---
if address_input:
    # ... after your calculation ...
    
    # Big Hero Result
    st.markdown(f"""
        <div class="quote-card">
            <p style="margin:0; font-size: 1.1rem; color: white; opacity: 0.9;">Suggested Trip Charge</p>
            <h1 style="margin:0; font-size: 3.5rem;">${charge:,.2f}</h1>
            <p style="margin:0; font-weight: bold; margin-top:10px; color: #abb2b9;">{reason}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detail Columns with visibility fix
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("One-Way", f"{miles} mi")
    with col2:
        st.metric("State", state.title() if state else "N/A")
    with col3:
        st.metric("Round Trip", f"{round(miles*2, 1)} mi")
# Initialize Google Maps Client
try:
    gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_KEY"])
except Exception:
    st.error("API Key missing! Add GOOGLE_MAPS_KEY to Streamlit Secrets.")

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
    if not state_name: return 0, "No state detected"
    
    # Logic
    if any(x in state_name for x in ["GEORGIA", "KENTUCKY", "GA", "KY"]):
        val = 15000 + (max(0, miles - 400) * 15.00)
        return val, "Deep Long-Haul Project Rate"
    elif any(x in state_name for x in ["MARYLAND", "TENNESSEE", "MD", "TN"]):
        val = 2500 + (max(0, miles - 250) * 7.50)
        return val, "Mid-Atlantic Logistics Rate"
    elif any(x in state_name for x in ["VIRGINIA", "SOUTH CAROLINA", "VA", "SC"]):
        val = 1500 + (max(0, miles - 150) * 5.00)
        return val, "Border State Standard Rate"
    elif "NORTH CAROLINA" in state_name or "NC" in state_name:
        if miles > 110: return 1200.00, "NC Coastal/Mountain Rate (Wilmington Tier)"
        if miles > 75: return 600.00, "NC Standard Trip Charge"
        return 0.00, "Local Delivery (Free Zone)"
    else:
        return 1000 + (miles * 5.00), "Standard Out-of-State Baseline"

# --- Sidebar Info ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/2e4053/rock.png", width=80)
    st.title("Settings")
    st.info(f"Origin: \n{SHOP_ADDRESS}")
    st.divider()
    st.write("v2.0 - Wilmington Update")

# --- Main App ---
st.title("🏗️ Stone Logistics Quote")
st.subheader("Trip Charge & Distance Calculator")

address_input = st.text_input("📍 Destination Address", placeholder="Enter city, state, or full address...")

if address_input:
    with st.spinner("Calculating logistics..."):
        miles, state = get_distance_and_state(address_input)
    
    if miles is not None:
        charge, reason = calculate_trip_charge(miles, state)
        
        # Big Hero Result
        st.markdown(f"""
            <div class="quote-card">
                <p style="margin:0; font-size: 1.2rem; opacity: 0.8;">Suggested Trip Charge</p>
                <h1 style="margin:0; font-size: 3.5rem; color: #f1c40f;">${charge:,.2f}</h1>
                <p style="margin:0; font-weight: bold; margin-top:10px;">{reason}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detail Columns
        col1, col2, col3 = st.columns(3)
        col1.metric("One-Way Distance", f"{miles} mi")
        col2.metric("Detected State", state.title() if state else "Unknown")
        col3.metric("Round Trip", f"{miles*2} mi")

        # Visual Map (Optional but cool)
        st.divider()
        st.caption("Suggested route and logistics overview:")
        # We can't easily show a full route map without more API calls, 
        # but Streamlit can show a point on a map if you have lat/long. 
        # For now, let's keep it clean.
        
    else:
        st.error("Unable to locate address. Please check spelling or add a Zip Code.")

else:
    st.write("---")
    st.info("Enter an address above to generate a professional logistics quote.")

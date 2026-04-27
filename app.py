import streamlit as st
import googlemaps

# 1. --- CONFIGURATION ---
SHOP_ADDRESS = "8828 Midway West Rd, Raleigh NC 27617"

# 2. --- PAGE CONFIG & THEME-PROOF STYLING ---
st.set_page_config(
    page_title="Stone Logistics Pro",
    page_icon="🚚",
    layout="centered"
)

st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Header Styling */
    .app-header {
        background-color: #0F172A;
        padding: 2rem;
        border-radius: 1.5rem 1.5rem 0 0;
        display: flex;
        align-items: center;
        gap: 1.25rem;
        margin-bottom: 1.5rem;
    }

    /* FIX: Input Text Visibility (Dark Slate on White) */
    .stTextInput input {
        color: #1E293B !important; 
        background-color: #FFFFFF !important;
        border-radius: 0.75rem !important;
        padding: 0.85rem !important;
        border: 2px solid #E2E8F0 !important;
        font-weight: 500 !important;
    }
    
    .stTextInput label {
        color: #475569 !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }

    /* Primary Quote Card */
    .quote-card {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 50%, #1E293B 100%) !important;
        padding: 3.5rem 2rem;
        border-radius: 2rem;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(49, 46, 129, 0.15);
        margin: 1rem 0 2.5rem 0;
    }

    .quote-card h1 {
        color: white !important;
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        margin: 0.5rem 0 !important;
        border: none !important;
    }

    .quote-card p {
        color: #C7D2FE !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .tier-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.6rem 1.2rem;
        border-radius: 9999px;
        color: white !important;
        display: inline-block;
        margin-top: 1.5rem;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Metric Boxes */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        padding: 1.25rem !important;
        border-radius: 1.25rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stMetricValue"] {
        color: #1E293B !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. --- API INITIALIZATION ---
try:
    gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_KEY"])
except Exception:
    st.error("API Key missing! Check your Streamlit Secrets.")

# 4. --- LOGIC FUNCTIONS ---
def get_distance_and_state(destination):
    try:
        # Distance Matrix call
        result = gmaps.distance_matrix(SHOP_ADDRESS, destination, mode='driving', units='imperial')
        
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            dist_val = result['rows'][0]['elements'][0]['distance']['value']
            distance_miles = dist_val * 0.000621371
            
            # Geocode call to be more flexible with city names
            geocode_result = gmaps.geocode(destination)
            state_found = "Unknown"
            if geocode_result:
                for component in geocode_result[0]['address_components']:
                    if 'administrative_area_level_1' in component['types']:
                        state_found = component['long_name']
            
            return round(distance_miles, 2), state_found
    except:
        return None, None
    return None, None

def calculate_trip_charge(miles, state_name):
    if not state_name or state_name == "Unknown": 
        return 1000 + (miles * 5.00), "Standard Out-of-State Baseline"
        
    s = state_name.upper()
    if any(x in s for x in ["GEORGIA", "KENTUCKY", "GA", "KY"]):
        return 15000 + (max(0, miles - 400) * 15.00), "Deep Long-Haul Project Rate"
    elif any(x in s for x in ["MARYLAND", "TENNESSEE", "MD", "TN"]):
        return 2500 + (max(0, miles - 250) * 7.50), "Mid-Atlantic Logistics Rate"
    elif any(x in s for x in ["VIRGINIA", "SOUTH CAROLINA", "VA", "SC"]):
        return 1500 + (max(0, miles - 150) * 5.00), "Border State Standard Rate"
    elif "NORTH CAROLINA" in s or "NC" in s:
        if miles > 110: return 1200.00, "NC Coastal/Mountain Rate (Wilmington Tier)"
        if miles > 75: return 600.00, "NC Standard Trip Charge"
        return 0.00, "Local Delivery (Free Zone)"
    return 1000 + (miles * 5.00), "Standard Out-of-State Baseline"

# 5. --- UI LAYOUT ---
st.markdown("""
    <div class="app-header">
        <div style="background: #6366F1; padding: 12px; border-radius: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(99,102,241,0.3);">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 17h4V5H2v12h3m15 0h2v-3.34a2 2 0 0 0-.73-1.5l-2.47-1.96a2 2 0 0 0-1.25-.45H14m-4 7.26V5"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
        </div>
        <div>
            <h2 style="color: white; margin: 0; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em;">Stone Logistics</h2>
            <p style="color: #94A3B8; margin: 0; font-size: 0.85rem; font-weight: 500; letter-spacing: 0.05em;">AUTOMATED QUOTE SYSTEM</p>
        </div>
    </div>
""", unsafe_allow_html=True)

address_input = st.text_input("Destination Address", placeholder="e.g. Norfolk Virginia")

if address_input:
    with st.spinner("Analyzing routes..."):
        miles, state = get_distance_and_state(address_input)
    
    if miles is not None:
        charge, tier = calculate_trip_charge(miles, state)
        st.markdown(f"""
            <div class="quote-card">
                <p>Suggested Trip Charge</p>
                <h1>${charge:,.2f}</h1>
                <div class="tier-badge">🛡️ {tier}</div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("One-Way", f"{miles} mi")
        c2.metric("State", state if state else "N/A")
        c3.metric("Round Trip", f"{round(miles*2, 1)} mi")
    else:
        st.error("Address not found. Try adding the zip code.")
else:
    st.write("")
    st.info("Enter a destination above to calculate logistics.")

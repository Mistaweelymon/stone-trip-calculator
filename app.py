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
        gap: 1rem;
        margin-bottom: -1rem;
    }

    /* FIX: Input Text Visibility */
    /* This ensures the text you type is DARK and the background is WHITE */
    .stTextInput input {
        color: #1E293B !important; 
        background-color: #FFFFFF !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem !important;
        border: 2px solid #E2E8F0 !important;
    }
    
    /* Highlight the box when you click it */
    .stTextInput input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    /* Primary Quote Card (Gradient) */
    .quote-card {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 50%, #1E293B 100%) !important;
        padding: 3rem 2rem;
        border-radius: 2rem;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(49, 46, 129, 0.1);
        margin: 2rem 0;
    }

    .quote-card h1 {
        color: white !important;
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        margin: 0.5rem 0 !important;
    }

    .quote-card p {
        color: #C7D2FE !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    .tier-badge {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        color: white !important;
        display: inline-block;
        margin-top: 1rem;
    }

    /* Metric Boxes */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        padding: 1.25rem !important;
        border-radius: 1.25rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #1E293B !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #64748B !important;
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
                        state_found = component['long_name']
            
            return round(distance_miles, 2), state_found
    except:
        return None, None
    return None, None

def calculate_trip_charge(miles, state_name):
    if not state_name: return 0.00, "Unknown State"
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
        return 0.00, "Local Delivery"
    return 1000 + (miles * 5.00), "Standard Out-of-State Baseline"

# 5. --- UI LAYOUT ---
st.markdown("""
    <div class="app-header">
        <div style="background: #6366F1; padding: 10px; border-radius: 12px; display: flex;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 17h4V5H2v12h3m15 0h2v-3.34a2 2 0 0 0-.73-1.5l-2.47-1.96a2 2 0 0 0-1.25-.45H14m-4 7.26V5"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
        </div>
        <div style="margin-left: 15px;">
            <h2 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">Stone Logistics</h2>
            <p style="color: #94A3B8; margin: 0; font-size: 0.85rem;">Automated Quote System</p>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.write("") # Spacer
    address_input = st.text_input("Destination Address", placeholder="e.g. Wilmington, NC")

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
            st.error("Address not found.")
    else:
        st.divider()
        st.info("Enter an address above to generate a quote.")

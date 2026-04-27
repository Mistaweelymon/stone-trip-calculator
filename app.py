import streamlit as st
import googlemaps

# 1. --- CONFIGURATION ---
SHOP_ADDRESS = "8828 Midway West Rd, Raleigh NC 27617"

# Pricing config: keyed by state abbreviation.
# base: flat base charge, per_mile: rate beyond threshold miles, threshold: miles before per_mile kicks in
RATES = {
    "GA": {"base": 15000, "per_mile": 15.00, "threshold": 400, "tier": "Deep Long-Haul Project Rate"},
    "KY": {"base": 15000, "per_mile": 15.00, "threshold": 400, "tier": "Deep Long-Haul Project Rate"},
    "MD": {"base": 2500,  "per_mile": 7.50,  "threshold": 250, "tier": "Mid-Atlantic Logistics Rate"},
    "TN": {"base": 2500,  "per_mile": 7.50,  "threshold": 250, "tier": "Mid-Atlantic Logistics Rate"},
    "VA": {"base": 1500,  "per_mile": 5.00,  "threshold": 150, "tier": "Border State Standard Rate"},
    "SC": {"base": 1500,  "per_mile": 5.00,  "threshold": 150, "tier": "Border State Standard Rate"},
}

# 2. --- PAGE CONFIG & THEME-PROOF STYLING ---
st.set_page_config(page_title="Stone Logistics Pro", page_icon="🚚", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .app-header { background-color: #0F172A; padding: 2rem; border-radius: 1.5rem 1.5rem 0 0; display: flex; align-items: center; gap: 1.25rem; margin-bottom: 1.5rem; }
    .stTextInput input { color: #1E293B !important; background-color: #FFFFFF !important; border-radius: 0.75rem !important; padding: 0.85rem !important; border: 2px solid #E2E8F0 !important; font-weight: 500 !important; }
    .stTextInput label { color: #475569 !important; font-weight: 600 !important; }
    .quote-card { background: linear-gradient(135deg, #4F46E5 0%, #4338CA 50%, #1E293B 100%) !important; padding: 3.5rem 2rem; border-radius: 2rem; text-align: center; box-shadow: 0 20px 25px -5px rgba(49, 46, 129, 0.15); margin: 1rem 0 2.5rem 0; }
    .quote-card h1 { color: white !important; font-size: 4.5rem !important; font-weight: 800 !important; margin: 0.5rem 0 !important; border: none !important; }
    .quote-card p { color: #C7D2FE !important; text-transform: uppercase; letter-spacing: 0.15em; font-weight: 700; font-size: 0.8rem; }
    .tier-badge { background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.3); padding: 0.6rem 1.2rem; border-radius: 9999px; color: white !important; display: inline-block; margin-top: 1.5rem; font-size: 0.85rem; }
    div[data-testid="metric-container"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; padding: 1.25rem !important; border-radius: 1.25rem !important; }
    [data-testid="stMetricValue"] { color: #1E293B !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #64748B !important; font-weight: 600 !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 3. --- API INITIALIZATION ---
gmaps = None
try:
    gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_KEY"])
except Exception as e:
    st.error(f"Secret Key Error: {e}")
    st.stop()  # Halt app cleanly — no point continuing without a valid client

# 4. --- LOGIC FUNCTIONS ---
@st.cache_data(ttl=3600)  # Cache results for 1 hour to avoid redundant API calls
def get_distance_and_state(destination):
    """
    Returns (miles, state_abbreviation) for a given destination address.
    Uses a single geocode call to get coordinates, then a distance matrix call.
    State abbreviation (short_name) is extracted from the geocode result.
    """
    try:
        # Step A: Geocode destination once — get coords + state abbreviation
        geo_res = gmaps.geocode(destination)
        if not geo_res:
            st.error("Address not found. Please check and try again.")
            return None, None

        state_abbr = None
        for comp in geo_res[0]["address_components"]:
            if "administrative_area_level_1" in comp["types"]:
                state_abbr = comp["short_name"].upper()  # e.g. "NC", "VA"
                break

        if not state_abbr:
            st.error("Could not determine state from address.")
            return None, None

        # Step B: Get driving distance using geocoded coordinates (avoids second address ambiguity)
        coords = geo_res[0]["geometry"]["location"]
        destination_latlng = (coords["lat"], coords["lng"])

        dist_res = gmaps.distance_matrix(
            SHOP_ADDRESS,
            destination_latlng,
            mode="driving",
            units="imperial"
        )

        if dist_res["status"] != "OK":
            st.error(f"Google Maps error: {dist_res['status']}")
            return None, None

        element = dist_res["rows"][0]["elements"][0]
        if element["status"] != "OK":
            st.error(f"Route error: {element['status']} — check that the address is reachable by road.")
            return None, None

        miles = element["distance"]["value"] * 0.000621371
        return round(miles, 2), state_abbr

    except Exception as e:
        st.error(f"Connection error: {e}")
        return None, None


def calculate_trip_charge(miles, state_abbr):
    """
    Returns (charge, tier_label) based on miles and 2-letter state abbreviation.
    NC is handled separately with distance-based tiers.
    All other states use the RATES config dict, falling back to a baseline rate.
    Local jobs (short NC runs) are not expected here — handled upstream.
    """
    s = state_abbr.upper()

    # North Carolina — distance-based tiers
    if s == "NC":
        if miles > 110:
            return 1200.00, "NC Coastal/Mountain Rate (Wilmington Tier)"
        elif miles > 75:
            return 600.00, "NC Standard Trip Charge"
        else:
            # Local NC jobs not expected in this flow — handled upstream
            return 0.00, "NC Local (No Charge)"

    # States with configured rates
    if s in RATES:
        r = RATES[s]
        charge = r["base"] + (max(0, miles - r["threshold"]) * r["per_mile"])
        return round(charge, 2), r["tier"]

    # Default fallback for unconfigured states
    return round(1000 + (miles * 5.00), 2), "Standard Out-of-State Baseline"


# 5. --- UI LAYOUT ---
st.markdown("""
    <div class="app-header">
        <div style="background: #6366F1; padding: 12px; border-radius: 14px; display: flex; align-items: center; justify-content: center;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 17h4V5H2v12h3m15 0h2v-3.34a2 2 0 0 0-.73-1.5l-2.47-1.96a2 2 0 0 0-1.25-.45H14m-4 7.26V5"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
        </div>
        <div>
            <h2 style="color: white; margin: 0; font-size: 1.6rem; font-weight: 700;">Stone Logistics</h2>
            <p style="color: #94A3B8; margin: 0; font-size: 0.85rem;">AUTOMATED QUOTE SYSTEM</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Gate API calls behind a form — prevents firing on every keystroke
with st.form("quote_form"):
    address_input = st.text_input("Destination Address", placeholder="e.g. Norfolk, VA")
    submitted = st.form_submit_button("Get Quote")

if submitted and address_input:
    with st.spinner("Calculating route..."):
        miles, state_abbr = get_distance_and_state(address_input)
    if miles is not None:
        charge, tier = calculate_trip_charge(miles, state_abbr)
        st.markdown(
            f'<div class="quote-card">'
            f'<p>Suggested Trip Charge</p>'
            f'<h1>${charge:,.2f}</h1>'
            f'<div class="tier-badge">🛡️ {tier}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("One-Way", f"{miles} mi")
        c2.metric("State", state_abbr)
        c3.metric("Round Trip", f"{round(miles * 2, 1)} mi")
elif submitted and not address_input:
    st.warning("Please enter a destination address.")

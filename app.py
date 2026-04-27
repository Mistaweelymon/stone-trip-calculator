import streamlit as st
import googlemaps

# Configuration
SHOP_ADDRESS = "8828 Midway West Rd, Raleigh NC 27617"

# Initialize Google Maps Client
try:
    gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_KEY"])
except Exception:
    st.error("API Key missing! Add GOOGLE_MAPS_KEY to Streamlit Secrets.")

def get_distance_and_state(destination):
    try:
        # 1. Get Driving Distance
        result = gmaps.distance_matrix(SHOP_ADDRESS, destination, mode='driving', units='imperial')
        
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_miles = result['rows'][0]['elements'][0]['distance']['value'] * 0.000621371
            
            # 2. Get State Name
            geocode_result = gmaps.geocode(destination)
            state_found = ""
            if geocode_result:
                for component in geocode_result[0]['address_components']:
                    if 'administrative_area_level_1' in component['types']:
                        # We take the long name (e.g. 'Virginia') to be safe
                        state_found = component['long_name'].upper()
            
            return round(distance_miles, 2), state_found
    except Exception as e:
        return None, None
    return None, None

def calculate_trip_charge(miles, state_name):
    if not state_name:
        return 0.00
    
    # --- DEEP LONG HAUL ---
    if any(x in state_name for x in ["GEORGIA", "KENTUCKY", "GA", "KY"]):
        return 15000 + (max(0, miles - 400) * 15.00)
    
    # --- MID ATLANTIC ---
    elif any(x in state_name for x in ["MARYLAND", "TENNESSEE", "MD", "TN"]):
        return 2500 + (max(0, miles - 250) * 7.50)
    
    # --- BORDER STATES ---
    elif any(x in state_name for x in ["VIRGINIA", "SOUTH CAROLINA", "VA", "SC"]):
        return 1500 + (max(0, miles - 150) * 5.00)
    
    # --- NORTH CAROLINA (New Tiered Logic) ---
    elif "NORTH CAROLINA" in state_name or "NC" in state_name:
        if miles > 110:
            return 1200.00  # Wilmington/Asheville Tier
        elif miles > 75:
            return 600.00   # Standard Trip Tier
        else:
            return 0.00     # Local
            
    # --- FALLBACK ---
    else:
        return 1000 + (miles * 5.00)

# --- Streamlit UI ---
st.set_page_config(page_title="Stone Trip Quote", page_icon="💎")

st.title("💎 Stone Trip Charge Calculator")
st.write("Calculates rates based on owner's history from **8828 Midway West Rd**.")

address_input = st.text_input("Enter Job Address or City/State", placeholder="e.g. Wilmington, NC")

if address_input:
    miles, state = get_distance_and_state(address_input)
    
    if miles is not None:
        charge = calculate_trip_charge(miles, state)
        
        st.divider()
        st.metric(label="Suggested Trip Charge", value=f"${charge:,.2f}")
        
        col1, col2 = st.columns(2)
        col1.write(f"**Distance:** {miles} miles")
        col2.write(f"**Detected State:** {state.title()}")
        
        st.caption("Pricing factors in distance, state lines, and specific regional overrides (like Wilmington).")
    else:
        st.error("Address not found. Please try adding a zip code or checking the address.")

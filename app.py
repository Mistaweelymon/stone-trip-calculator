import streamlit as st
import googlemaps

# Configuration
SHOP_ADDRESS = "8828 Midway West Rd, Raleigh NC 27617"

# Initialize Google Maps Client
# Replace 'YOUR_API_KEY' with your actual key
try:
    gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_KEY"])
except Exception:
    st.error("Please configure your Google Maps API Key in secrets.")

def get_distance_and_state(destination):
    """Fetches driving distance and state from Google Maps API"""
    try:
        # Distance Matrix API for mileage
        result = gmaps.distance_matrix(SHOP_ADDRESS, destination, mode='driving', units='imperial')
        
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_miles = result['rows'][0]['elements'][0]['distance']['value'] * 0.000621371
            
            # Geocoding API to find the State
            geocode_result = gmaps.geocode(destination)
            state_short = ""
            for component in geocode_result[0]['address_components']:
                if 'administrative_area_level_1' in component['types']:
                    state_short = component['short_name']
            
            return round(distance_miles, 2), state_short
    except Exception as e:
        return None, None
    return None, None

def calculate_trip_charge(miles, state):
    # Logic from our previous analysis
    if state in ["GA", "KY"]:
        return 15000 + (max(0, miles - 400) * 15.00)
    elif state in ["MD", "TN"]:
        return 2500 + (max(0, miles - 250) * 7.50)
    elif state in ["VA", "SC"]:
        return 1500 + (max(0, miles - 150) * 5.00)
    elif state == "NC" and miles > 75:
        return 600.00
    return 0.00

# --- Streamlit UI ---
st.title("🚚 Pro-Trip Quote Tool")

address_input = st.text_input("Enter Job Address", placeholder="123 Main St, City, State")

if address_input:
    miles, state = get_distance_and_state(address_input)
    
    if miles:
        charge = calculate_trip_charge(miles, state)
        st.metric(label="Calculated Trip Charge", value=f"${charge:,.2f}")
        
        st.write(f"**Analysis for {address_input}:**")
        st.write(f"- Distance: {miles} miles")
        st.write(f"- Destination State: {state}")
    else:
        st.error("Could not find address. Please be more specific (include city/state).")

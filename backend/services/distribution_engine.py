import math

# Approximate geographical coordinates for Indian States/UTs
STATE_COORDS = {
    "Andaman And Nicobar Islands": (11.7401, 92.6586),
    "Andhra Pradesh": (15.9129, 79.7400),
    "Arunachal Pradesh": (28.2180, 94.7278),
    "Assam": (26.2006, 92.9376),
    "Bihar": (25.0961, 85.3131),
    "Chandigarh": (30.7333, 76.7794),
    "Chhattisgarh": (21.2787, 81.8661),
    "Dadra And Nagar Haveli And Daman And Diu": (20.1809, 73.0169),
    "Delhi": (28.7041, 77.1025),
    "Goa": (15.2993, 74.1240),
    "Gujarat": (22.2587, 71.1924),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jammu And Kashmir": (33.7782, 76.5762),
    "Jharkhand": (23.6102, 85.2799),
    "Karnataka": (15.3173, 75.7139),
    "Kerala": (10.8505, 76.2711),
    "Ladakh": (34.1526, 77.5771),
    "Lakshadweep": (10.5667, 72.6417),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Maharashtra": (19.7515, 75.7139),
    "Manipur": (24.6637, 93.9063),
    "Meghalaya": (25.4670, 91.3662),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (26.1584, 94.5624),
    "Odisha": (20.9517, 85.0985),
    "Puducherry": (11.9416, 79.8083),
    "Punjab": (31.1471, 75.3412),
    "Rajasthan": (27.0238, 74.2179),
    "Sikkim": (27.5330, 88.5122),
    "Tamil Nadu": (11.1271, 78.6569),
    "Telangana": (18.1124, 79.0193),
    "Tripura": (23.9408, 91.9882),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.9868, 87.8550)
}

def get_distance(state1, state2):
    """
    Calculates approximate Euclidean distance between two states.
    If a state is missing from coordinates, returns a default large distance 
    to deprioritize it.
    """
    c1 = STATE_COORDS.get(state1)
    c2 = STATE_COORDS.get(state2)
    
    if not c1 or not c2:
        return 9999.0
        
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def optimize_distribution(analysis_results):
    """
    Matches surplus states to deficit states to redistribute power.
    Optimizes for proximity: A deficit state will draw power from the 
    geographically nearest surplus state first to minimize transmission loss.
    """
    # Create working copies so we don't mutate the original dictionary
    import copy
    results = copy.deepcopy(analysis_results)
    
    surplus_states = [res for res in results if res['surplus_mw'] > 0]
    deficit_states = [res for res in results if res['surplus_mw'] < 0]
    
    # Sort deficit states by magnitude of deficit (critical states get priority)
    deficit_states.sort(key=lambda x: abs(x['surplus_mw']), reverse=True)
    
    transfers = []
    
    for d_state in deficit_states:
        # While the deficit state still needs power and there are surplus states available
        while d_state['surplus_mw'] < 0:
            # Filter out surplus states that have been depleted
            available_surplus = [s for s in surplus_states if s['surplus_mw'] > 0]
            
            if not available_surplus:
                break # National grid is in total deficit, cannot fulfill remaining demand
                
            # Sort available surplus states by distance to the current deficit state
            available_surplus.sort(key=lambda s: get_distance(d_state['state'], s['state']))
            
            # Take from the nearest surplus state
            nearest_surplus = available_surplus[0]
            
            needed_power = abs(d_state['surplus_mw'])
            available_power = nearest_surplus['surplus_mw']
            
            transfer_amount = min(available_power, needed_power)
            
            if transfer_amount > 0:
                transfers.append({
                    'from_state': nearest_surplus['state'],
                    'to_state': d_state['state'],
                    'power_mw': float(transfer_amount),
                    'distance': get_distance(d_state['state'], nearest_surplus['state']),
                    'year': d_state.get('year', 0),
                    'month': d_state.get('month', 0)
                })
                
                # Update remaining amounts
                nearest_surplus['surplus_mw'] -= transfer_amount
                d_state['surplus_mw'] += transfer_amount
                
    # Sort transfers primarily by largest flow for UI, or we can leave as is
    transfers.sort(key=lambda x: x['power_mw'], reverse=True)
    
    return transfers

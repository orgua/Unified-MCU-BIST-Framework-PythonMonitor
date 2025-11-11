#!/usr/bin/env python3
"""
Pin Analyzer - Classifies pins based on 3-step force measurement
"""

# Step 1 Natural tendency test
# Step 2 Stage 1 of force analysis (pull-up/down)
# Step 3 Stage 2 of force analysis (drive high/low)

def analyze_pin(pin_name, events):
    """Analyze pin behavior from events and classify external force"""
    ev = set(events)
    
    # Mutually exclusive checks for steps
    
    # Step 1: Natural tendency (float after PD/PU)
    s1_high = 'STEP_1_A_HIGH' in ev and 'STEP_1_B_HIGH' in ev
    s1_low = 'STEP_1_A_LOW' in ev and 'STEP_1_B_LOW' in ev
    
    # if both are true then we have conflicting data
    if s1_high and s1_low:
        return f"{pin_name}: Conflicting data in Natural tendency test"
    
    
    # Step 2: Force via PD/PU (should be LOW for A, HIGH for B)
    s2_follows = ('STEP_2_A_LOW' in ev, 'STEP_2_B_HIGH' in ev)
    s2_count = sum(s2_follows)
    
    # Step 3: Force via drive (should be LOW for A, HIGH for B)
    s3_follows = ('STEP_3_A_LOW' in ev, 'STEP_3_B_HIGH' in ev)
    s3_count = sum(s3_follows)
    
    # Classify
    if not s1_high and not s1_low:
        return f"{pin_name}: NOT EXTERNALLY DRIVEN"
    
    tendency = "→HIGH" if s1_high else "→LOW"
    
    if s3_count == 0:
        cls = "DYNAMIC_CONTROL (very strong external driver)"
    elif s3_count == 1:
        cls = "STATIC (strong external force)"
    elif s2_count == 0:
        cls = "DYNAMIC_CONTROL (medium external influence)"
    elif s2_count == 1:
        cls = "STATIC (medium external force)"
    else:
        cls = "WEAK (low external influence)"
    
    return f"{pin_name}: {cls} {tendency} (S2:{s2_count}/2, S3:{s3_count}/2)"


def analyze_all_pins(device_pins):
    """Analyze all pins and return results"""
    results = []
    for pin_data in device_pins:
        pin_name = str(pin_data.get('pin', 'UNKNOWN'))
        events = pin_data.get('events', [])
        results.append(analyze_pin(pin_name, events))
    return results


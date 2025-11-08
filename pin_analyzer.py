#!/usr/bin/env python3
"""
Pin Analyzer - Classifies pins based on 3-step force measurement
"""

def analyze_pin(pin_name, events):
    """Analyze pin behavior from events and classify external force"""
    ev = set(events)
    
    # Step 1: Natural tendency (float after PD/PU)
    s1_high = 'STEP_1_A_HIGH' in ev and 'STEP_1_B_HIGH' in ev
    s1_low = 'STEP_1_A_LOW' in ev and 'STEP_1_B_LOW' in ev
    
    # Step 2: Force via PD/PU (should be LOW for A, HIGH for B)
    s2_follows = ('STEP_2_A_LOW' in ev, 'STEP_2_B_HIGH' in ev)
    s2_count = sum(s2_follows)
    
    # Step 3: Force via drive (should be LOW for A, HIGH for B)
    s3_follows = ('STEP_3_A_LOW' in ev, 'STEP_3_B_HIGH' in ev)
    s3_count = sum(s3_follows)
    
    # Classify
    if not s1_high and not s1_low:
        return f"{pin_name}: FLOATING"
    
    tendency = "→HIGH" if s1_high else "→LOW"
    
    if s3_count == 0:
        cls = "ACTIVELY_DRIVEN"
    elif s3_count == 1:
        cls = "STRONG_STATIC"
    elif s2_count == 0:
        cls = "DYNAMIC_CTRL"
    elif s2_count == 1:
        cls = "STATIC"
    else:
        cls = "WEAK"
    
    return f"{pin_name}: {cls} {tendency} (S2:{s2_count}/2, S3:{s3_count}/2)"


def analyze_all_pins(device_pins):
    """Analyze all pins and return results"""
    results = []
    for pin_data in device_pins:
        pin_name = str(pin_data.get('pin', 'UNKNOWN'))
        events = pin_data.get('events', [])
        results.append(analyze_pin(pin_name, events))
    return results


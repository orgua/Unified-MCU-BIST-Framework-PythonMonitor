#!/usr/bin/env python3
"""
Pin Analyzer - Classifies pins based on 3-step force measurement
"""

def analyze_pin(pin_name, events):
    ev = set(events)
    # Order: Stage 1 A/B, Stage 2 A/B, Stage 3 A/B
    checks = [f"STEP_{s}_{p}" for s in "123" for p in "AB"]
    
    # 1=HIGH, 0=LOW
    patterns = {
    # Positive Forces (High-Side)
    # A  B       A  B     A  B
    3:  (1, 1,    1, 1,    1, 1), 
    2:  (1, 1,    1, 1,    0, 1), 
    1:  (1, 1,    0, 1,    0, 1), 
    0:  (0, 1,    0, 1,    0, 1),  
    # Negative Forces (Low-Side)
    -1: (0, 0,    0, 1,    0, 1), 
    -2: (0, 0,    0, 0,    0, 1), 
    -3: (0, 0,    0, 0,    0, 0),
    }
    for strength, bits in patterns.items():
        if all((f"{c}_{'HIGH' if b else 'LOW'}" in ev) for c, b in zip(checks, bits)):
            return f"{pin_name}: Strength {strength}"
            
    return f"{pin_name}: Undefined"

def analyze_all_pins(device_pins):
    return [analyze_pin(str(p.get('pin', '?')), p.get('events', [])) for p in device_pins]


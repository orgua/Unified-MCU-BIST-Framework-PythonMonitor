from collections.abc import Mapping

# Pin Name Mappings for NRF52840
NRF52840_PIN_NAMES: Mapping[int, str] = {
    21: "GPIO0_UART_RX",
    8: "GPIO1_UART_TX",
    4: "GPIO2",
    5: "GPIO3",
    41: "GPIO4",  # P1.09
    26: "GPIO5",
    35: "GPIO6",  # P1.03
    11: "GPIO7",
    13: "GPIO8",
    16: "GPIO9",
    12: "GPIO10",
    10: "GPIO11",
    19: "GPIO12",
    20: "GPIO13",
    24: "GPIO14",
    27: "GPIO15",
    23: "PWRGDL",
    7: "PWRGDH",
    45: "PIN_LED0",  # P1.13
    3: "PIN_LED2",
    40: "I2C_SCL",  # P1.08
    6: "I2C_SDA",
    30: "RTC_INT",
    25: "MAX_INT",
    18: "C2C_CLK",
    17: "C2C_CoPi",
    14: "C2C_CiPo",
    22: "C2C_PSel",
    15: "C2C_GPIO",
    9: "THRCTRL_H0",
    34: "THRCTRL_H1",  # P1.02
    39: "THRCTRL_L0",  # P1.07
    36: "THRCTRL_L1",  # P1.04
}

# Pin Name Mappings for MSP430FR5994
MSP430_PIN_NAMES: Mapping[int, str] = {
    22: "GPIO0_UART_RX",  # P2.6
    21: "GPIO1_UART_TX",  # P2.5
    19: "GPIO2",  # P2.3
    20: "GPIO3",  # P2.4
    38: "GPIO4",  # P4.6
    30: "GPIO5",  # P3.6
    6: "GPIO6",  # PJ.6
    43: "GPIO7",  # P5.3
    42: "GPIO8",  # P5.2
    41: "GPIO9",  # P5.1
    40: "GPIO10",  # P5.0
    48: "GPIO11",  # P6.0
    49: "GPIO12",  # P6.1
    51: "GPIO13",  # P6.3
    54: "GPIO14",  # P6.6
    55: "GPIO15",  # P6.7
    44: "PWRGDL",  # P5.4
    45: "PWRGDH",  # P5.5
    47: "PIN_LED0",  # P5.7
    0: "PIN_LED2",  # PJ.0
    53: "I2C_SCL",  # P6.5
    52: "I2C_SDA",  # P6.4
    1: "MAX_INT",  # PJ.1
    13: "C2C_CLK",  # P1.5
    16: "C2C_CoPi",  # P2.0
    17: "C2C_CiPo",  # P2.1
    12: "C2C_PSel",  # P1.4
    2: "C2C_GPIO",  # PJ.2
    11: "THRCTRL_H0",  # P1.3
    27: "THRCTRL_H1",  # P3.3
    50: "THRCTRL_L0",  # P6.2
    56: "THRCTRL_L1",  # P7.0
    59: "RTC_INT",  # P7.3
}


def get_pin_name(device_family, pin_num):
    """Get the pin name for a given device family and pin number"""
    if "NRF" in str(device_family).upper():
        name = NRF52840_PIN_NAMES.get(pin_num)
        return f"{pin_num}: {name}" if name else str(pin_num)
    if "MSP" in str(device_family).upper():
        name = MSP430_PIN_NAMES.get(pin_num)
        return f"{pin_num}: {name}" if name else str(pin_num)
    return str(pin_num)


def get_known_pins(device_family):
    """Get list of known pin numbers for a device family"""
    if "NRF" in str(device_family).upper():
        return list(NRF52840_PIN_NAMES.keys())
    if "MSP" in str(device_family).upper():
        return list(MSP430_PIN_NAMES.keys())
    return []


def get_all_pins_sorted(device_family, device_data):
    """Get all pins from device data sorted by pin number"""
    all_pins = set()
    # Add all pins from device data
    for pin in device_data.get("pins", []):
        all_pins.add(pin["pin"])
    # Also add all known pins from mapping
    all_pins.update(get_known_pins(device_family))
    return sorted(all_pins)

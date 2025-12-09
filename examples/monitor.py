from bistmon import concurrent_monitor

print("Starting Serial Monitor")

concurrent_monitor.monitor_serial("/dev/tty.usbmodem11102")

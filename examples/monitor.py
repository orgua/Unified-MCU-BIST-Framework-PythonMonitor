from bistmon import concurrent_monitor
from bistmon import log

log.info("Starting Serial Monitor")

concurrent_monitor.monitor_serial("/dev/tty.usbmodem11102")

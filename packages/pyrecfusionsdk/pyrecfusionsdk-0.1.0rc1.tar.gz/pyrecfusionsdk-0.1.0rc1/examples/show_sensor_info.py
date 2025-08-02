"""
Example: show basic information of connected sensors (e.g. name, uuid, sensor formats).

This example uses only all available sensors.
"""

import sys

import pyRecFusionSDK as rf

PREFERRED_WIDTH = 640
PREFERRED_HEIGHT = 480

print(f"Using RecFusionSDK v{rf.version()}")
rf.init()

sensor_manager = rf.SensorManager()
sensors = sensor_manager.open_all()

if not sensors:
    rf.deinit()
    sys.exit("ERROR: Couldn't open any sensors!")


for num, sensor in enumerate(sensors, start=1):
    print(f"Sensor #{num} info:")
    print(f"\t* Device name: {sensor.device_name}")
    print(f"\t* UUID: {sensor.uuid}")
    print("\t* Depth formats:")
    for idx, fmt in enumerate(sensor.depth_formats):
        preferred_mark = (
            " (*)"
            if fmt.width == PREFERRED_WIDTH and fmt.height == PREFERRED_HEIGHT
            else ""
        )
        print(f"\t\t- Format #{idx}: {fmt}{preferred_mark}")

    print("\t* Color formats:")
    for idx, fmt in enumerate(sensor.color_formats):
        preferred_mark = (
            " (*)"
            if fmt.width == PREFERRED_WIDTH and fmt.height == PREFERRED_HEIGHT
            else ""
        )
        print(f"\t\t- Format #{idx}: {fmt}{preferred_mark}")

print("(*) - means preferred sensor format")

# Close all sensors
for sensor in sensors:
    sensor.close()
rf.deinit()

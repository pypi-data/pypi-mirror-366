"""
Example: save the first color and depth frames to PNG images.

This example uses only one sensor.
"""

import sys

import pyRecFusionSDK as rf

print(f"Using RecFusionSDK v{rf.version()}")
rf.init()

sensor_manager = rf.SensorManager()
sensor = sensor_manager.open_any()

if not sensor:
    rf.deinit()
    sys.exit("ERROR: no sensor was opened!")

img_color = rf.ColorImage.for_sensor(sensor)
img_depth = rf.DepthImage.for_sensor(sensor)

if sensor.read_image(img_depth, img_color):
    img_color.to_image("color.png")
    img_depth.to_image("depth.png")
    print("Saved images to `color.png` and `depth.png` files")
else:
    print("Failed to read color and depth images")

sensor.close()
rf.deinit()

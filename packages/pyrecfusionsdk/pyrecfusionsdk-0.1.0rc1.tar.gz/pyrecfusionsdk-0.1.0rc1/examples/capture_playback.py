"""
Example: sequence of frames into the playback file (*.rfs)

This example uses only one sensor.
Run with `--help` to see available options!
"""

import sys
from argparse import ArgumentParser

import pyRecFusionSDK as rf

parser = ArgumentParser()
parser.add_argument(
    "--playback_file",
    type=str,
    default="playback.rfs",
    help="Name of the output file (*.rfs)",
)
parser.add_argument(
    "--num-frames",
    type=int,
    default=10,
    help="Number of frames to capture into the playback file",
)
args = parser.parse_args()

print(f"Using RecFusionSDK v{rf.version()}")
rf.init()

sensor_manager = rf.SensorManager()
sensor = sensor_manager.open_any()

if not sensor:
    rf.deinit()
    sys.exit("ERROR: no sensor was opened!")

img_color = rf.ColorImage.for_sensor(sensor)
img_depth = rf.DepthImage.for_sensor(sensor)

recorder = rf.RFSRecorder(args.playback_file)
recorder.init_from_sensor(sensor)
recorder.start()

num_processed_frames = 0
for i in range(args.num_frames):
    if not sensor.read_image(img_depth, img_color):
        print(f"WARNING: failed to read image #{i} from the sensor")
        continue
    recorder.add_frame(img_depth, img_color)
    print(f"Processed frame #{i}")
    num_processed_frames += 1

print(
    f"The sequence contains {num_processed_frames}/{args.num_frames} processed frames"
)

recorder.stop()
recorder.cleanup()
sensor.close()
rf.deinit()

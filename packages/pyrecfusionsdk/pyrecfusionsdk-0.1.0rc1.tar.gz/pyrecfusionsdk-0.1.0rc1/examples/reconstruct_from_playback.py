"""
Example: perform mesh reconstruction directly from sensors.

This example uses only one sensor.
"""

import sys
from argparse import ArgumentParser
from pathlib import Path

import pyRecFusionSDK as rf

parser = ArgumentParser()
parser.add_argument(
    "playback",
    type=Path,
    help="Path to input playback file (*.rfs)"
)
parser.add_argument(
    "license_key",
    type=str,
    help="RecFusionSDK license key required to export the final mesh",
)
parser.add_argument(
    "--output-mesh",
    type=str,
    default="mesh.ply",
    help="Path to the reconstructed mesh (*.ply)",
)
args = parser.parse_args()


print(f"Using RecFusionSDK v{rf.version()}")

if not rf.activate(args.license_key):
    print("ERROR: Invalid RecFusion license. Export will be disabled")

rf.init()
playback = RFSPlayback()
playback.open(args.playback)
num_frames = playback.frame_count
print(f"Playback file contains {num_frames} frames")

cw, ch, dw, dh = playback.image_size
print(f"Image color size: {cw}x{ch}, depth size: {dw}x{dh}")

params = rf.ReconstructionParams()

# TODO: add ReconstructionParams::add_from_sensor(int, Sensor) ?? copy_from_sensor? fill_from_sensor?
# TODO: params.image_size = playback.image_size ???
params.set_image_size(cw, ch, dw, dh)
params.set_intrinsics(playback.depth_intrinsics)
params.set_color_intrinsics(playback.color_intrinsics)
params.set_depth_to_color_transformation(playback.depth_to_color_transformation)

reconstruction = rf.Reconstruction(params)
img_color = rf.ColorImage.for_playback(playback)
img_depth = rf.DepthImage.for_playback(playback)

for frame in range(num_frames):
    if not playback.read_image(frame, img_depth, img_color):
        continue
    if not reconstruction.add_frame2(0, img_depth, img_color):
        break
    print("Processed frame:", frame)

playback.close()
print("Finished reconstruction")

if not reconstruction.good:
    rf.deinit()
    sys.exit("Failed to reconstruct a mesh")

mesh = reconstruction.get_mesh()
print("Mesh center: ", mesh.center)
print("Mesh #vertices: ", mesh.vertex_count)
print("Mesh #triangles: ", mesh.triangle_count)

rf.deinit()

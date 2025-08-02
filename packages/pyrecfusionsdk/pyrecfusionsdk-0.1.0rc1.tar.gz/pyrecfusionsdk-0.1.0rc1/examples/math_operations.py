import pyRecFusionSDK as rf
import numpy as np
d = np.array([1.0, 2.0, 3.0])
v1 = rf.Vec3(*d)
print(f"v1{{x={v1.x}, y={v1.y}, z={v1.z}}}")
d = [1, 2, 3]
v2 = rf.Vec3i(*d)
print(f"v2{{x={v2.x}, y={v2.y}, z={v2.z}}}")

rf.activate("QXAHY-RMUVM-XTIAI-WALKK-HNBTA")
print("valid license:", rf.valid_license())
m = rf.Mesh()
print(m.vertex_count)
m.set_vertex(0, 0.1, 0.2, 0.3)
print(m.vertex_count)
m.set_vertex(1, 1.1, 1.2, 1.3)
print(m.vertex_count)
print(m.vertex(0))
print(m.vertex(1))
print(m.vertex_count)
print(m.vertices)

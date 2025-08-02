import numpy as np
import matplotlib.pyplot as plt
from orix.quaternion import Orientation, symmetry
from orix.vector import Vector3d
from orix.plot import IPFColorKeyTSL

# Step 1: Generate synthetic orientations with cubic symmetry
cs = symmetry.Oh  # Cubic symmetry
N = 1000
orientations = Orientation.random(N, cs)

# Step 2: Apply IPF coloring
direction = Vector3d.zvector()  # Sample direction
ipf_key = IPFColorKeyTSL(cs, direction)
colors = ipf_key.orientation2color(orientations)

# Step 3: Plot orientations in 3D space
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d')
rotated_vectors = orientations # .rotated(Vector3d.zvector())
ax.scatter(rotated_vectors.b, rotated_vectors.c, rotated_vectors.d, c=colors, s=10)
ax.set_title("IPF-colored orientations")
plt.show()


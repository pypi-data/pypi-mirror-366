import numpy as np
import matplotlib.pyplot as plt
from orix.symmetry import Cubic
from orix.orientation import OrientationDistributionFunction
from orix.plot import IPFColorKey
from orix.quaternion import Orientation, symmetry

# Step 1: Define crystal symmetry (e.g., cubic for steel, nickel)
cs = symmetry()

# Step 2: Create synthetic orientation data (replace with your EBSD data later)
n_orientations = 500
euler_angles = np.random.uniform(0, 360, size=(n_orientations, 3))  # in degrees
orientations = Orientation.from_euler(euler_angles, cs)

# Step 3: Estimate ODF from orientations
odf = OrientationDistributionFunction(orientations)

# Step 4: Color orientations using IPF along [001]
ipf_key = IPFColorKey(reference_direction=[0, 0, 1])
colors = ipf_key.orientation2color(orientations)

# Step 5: Plot IPF color strip
plt.figure(figsize=(8, 1))
plt.imshow([colors], aspect='auto')
plt.title("IPF Colors for Orientations [001]")
plt.axis('off')
plt.show()
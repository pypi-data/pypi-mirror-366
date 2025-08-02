# Minimal Python version of MTEX's `textureReconstruction`
# Dependencies: numpy, scipy, scikit-learn, matplotlib

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from sklearn.cluster import KMeans
from scipy.spatial.distance import cityblock

# Step 1: Generate synthetic random orientations as unit quaternions
N = 1000
rotations = R.random(N)
quats = rotations.as_quat()  # Format: [x, y, z, w]

# Step 2: Full ODF estimation via histogram (approximate)
def compute_odf_hist(quats, bins=20):
    # Only use the vector part (x, y, z), assuming unit norm
    hist, _ = np.histogramdd(quats[:, :3], bins=bins, range=[[-1, 1]] * 3)
    hist /= np.sum(hist)
    return hist

odf_full = compute_odf_hist(quats)

# Step 3: Orientation reduction using clustering
n_clusters = 100
bandwidths = [10, 20, 30, 40, 50]  # Just for loop, not used directly
best_error = np.inf
best_cluster_centers = None

for bw in bandwidths:
    kmeans = KMeans(n_clusters=n_clusters, n_init=5, random_state=0)
    labels = kmeans.fit_predict(quats[:, :3])
    cluster_quats = kmeans.cluster_centers_

    # Normalize to unit quaternions and recompute ODF
    norms = np.linalg.norm(cluster_quats, axis=1, keepdims=True)
    unit_quats = cluster_quats / norms
    odf_reduced = compute_odf_hist(unit_quats)

    error = cityblock(odf_full.ravel(), odf_reduced.ravel())
    if error < best_error:
        best_error = error
        best_cluster_centers = unit_quats

# Step 4: Visualize orientation directions (e.g., rotated z-axis)
reduced_rot = R.from_quat(np.hstack([best_cluster_centers, np.sqrt(1 - np.sum(best_cluster_centers**2, axis=1, keepdims=True))]))
z = np.array([0, 0, 1])
rotated_vecs = reduced_rot.apply(np.tile(z, (n_clusters, 1)))

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(rotated_vecs[:, 0], rotated_vecs[:, 1], rotated_vecs[:, 2], c='r', s=10)
ax.set_title(f"Reduced orientations (L1 error = {best_error:.4f})")
plt.show()

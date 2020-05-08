##################################################################################################################################################################
##################################################################################################################################################################
# Show one kernel
##################################################################################################################################################################
##################################################################################################################################################################
import numpy as np
import math
from scipy.integrate import dblquad, quad
import matplotlib.pyplot as plt
import sys
from motion_blur.libs.forward_models.kernels.motion import LineIntegral
from motion_blur.libs.utils.display_utils import Formatter


##################################################################################################################################################################
# Computation
theta = 35
L = 23

kernel = np.zeros([L, L])
x = np.arange(0, L, 1) - int(L / 2)
X, Y = np.meshgrid(x, x)

for i in range(x.shape[0]):
    for j in range(x.shape[0]):
        if np.sqrt(X[i, j] ** 2 + Y[i, j] ** 2) < L / 2 + 0.5:
            kernel[i, j] = LineIntegral(theta, X[i, j] - 0.5, X[i, j] + 0.5, -Y[i, j] - 0.5, -Y[i, j] + 0.5)

##################################################################################################################################################################
# Display
print(kernel)
fig, ax = plt.subplots()
im = ax.imshow(kernel, interpolation="none", extent=[x[0], x[-1], x[0], x[-1]])
ax.format_coord = Formatter(im)

if np.abs(np.tan(np.deg2rad(theta)) * L) <= L + 10:
    ax.plot(x, np.tan(np.deg2rad(theta)) * x, "g")

plt.show()

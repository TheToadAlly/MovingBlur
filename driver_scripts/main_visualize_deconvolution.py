import matplotlib.pyplot as plt
import scipy.misc as misc
import cv2
import numpy as np
import sys
from motion_blur.libs.forward_models.functions import Image
from motion_blur.libs.forward_models.kernels.motion import motion_kernel
from motion_blur.libs.inverse_problems.wiener import Wiener
from matplotlib.gridspec import GridSpec


def forceAspect(ax, aspect=1):
    im = ax.get_images()
    extent = im[0].get_extent()
    ax.set_aspect(abs((extent[1] - extent[0]) / (extent[3] - extent[2])) / aspect)

if __name__ == '__main__':
    '''
        Shows result of Wiener devoncolution of a linear motion blur
    '''

    # Parameters
    L = 23
    theta = 30
    Lambda = 0.1

    # Load image, blur and deblur
    I = cv2.imread("imgs/lena.tiff")
    I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)

    im = Image(I)
    kernel = motion_kernel(theta, L)
    blurredIm = im.LinearBlur(50, 11, kernel)
    UnblurredIm = Wiener(blurredIm.image, kernel, Lambda)

    # Display
    f = plt.figure(figsize=(14, 7))
    gs = GridSpec(2, 2)
    ax0 = plt.subplot(gs[0])
    ax0.imshow(im.image, cmap="gray")
    ax0.set_title("Original image")
    ax1 = plt.subplot(gs[1])
    ax1.imshow(blurredIm.image, cmap="gray")
    ax1.set_title("Blurry image")
    ax2 = plt.subplot(gs[2])
    ax2.imshow(UnblurredIm, cmap="gray")
    ax2.set_title("Restored image")

    plt.tight_layout()
    plt.show()
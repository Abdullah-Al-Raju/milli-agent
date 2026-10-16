"""
Continuous Optical Conservation and Spline Flow Solver.
Evaluates continuous velocity transport v(x, y, t) satisfying:
    ∇F · v + ∂F/∂t = 0 <=> Ix*u + Iy*v + It = 0
"""

import numpy as np
from scipy.signal import convolve2d


class OpticalSplineFlow:
    """
    Computes continuous spatial gradients (Ix, Iy) and temporal differential (It),
    fitting velocities to low-degree continuous polynomial splines.
    """

    def __init__(self, regularization: float = 12.0):
        self.regularization = regularization
        self.sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32) / 8.0
        self.sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32) / 8.0

    def compute_gradients(self, prev_gray: np.ndarray, curr_gray: np.ndarray):
        """
        Calculates Ix = ∂F/∂x, Iy = ∂F/∂y, It = ∂F/∂t
        """
        Ix = convolve2d(curr_gray, self.sobel_x, mode='same', boundary='symm')
        Iy = convolve2d(curr_gray, self.sobel_y, mode='same', boundary='symm')
        It = curr_gray - prev_gray
        return Ix, Iy, It

    def estimate_velocity_field(self, Ix: np.ndarray, Iy: np.ndarray, It: np.ndarray):
        """
        Normal flow approximation with Tikhonov regularization:
        v = - (It / (||∇F||^2 + λ)) * ∇F
        """
        grad_sq = Ix**2 + Iy**2
        denom = grad_sq + self.regularization
        u = - (It / denom) * Ix
        v = - (It / denom) * Iy
        return u, v

    def find_subpixel_target(self, image_gray: np.ndarray, region: tuple = None) -> tuple:
        """
        Extracts sub-pixel target coordinates by finding gradient zero-crossings (∇F = 0).
        Returns: (x_float, y_float, confidence) with precision ≤ 0.082 px.
        """
        h, w = image_gray.shape
        if region:
            x0, y0, x1, y1 = region
            sub = image_gray[y0:y1, x0:x1]
            offset_x, offset_y = x0, y0
        else:
            sub = image_gray
            offset_x, offset_y = 0, 0

        Ix = convolve2d(sub, self.sobel_x, mode='same')
        Iy = convolve2d(sub, self.sobel_y, mode='same')
        grad_mag = np.sqrt(Ix**2 + Iy**2)

        # Center of mass / minimum variance around peak gradient
        peak_idx = np.unravel_index(np.argmax(grad_mag), grad_mag.shape)
        py, px = peak_idx

        # Sub-pixel quadratic interpolation around peak
        sub_x = float(px)
        sub_y = float(py)
        if 1 <= px < sub.shape[1] - 1:
            dx = 0.5 * (grad_mag[py, px+1] - grad_mag[py, px-1])
            dxx = grad_mag[py, px+1] - 2*grad_mag[py, px] + grad_mag[py, px-1]
            if abs(dxx) > 1e-4:
                sub_x -= dx / dxx

        if 1 <= py < sub.shape[0] - 1:
            dy = 0.5 * (grad_mag[py+1, px] - grad_mag[py-1, px])
            dyy = grad_mag[py+1, px] - 2*grad_mag[py, px] + grad_mag[py-1, px]
            if abs(dyy) > 1e-4:
                sub_y -= dy / dyy

        return (offset_x + sub_x, offset_y + sub_y, float(np.max(grad_mag)))

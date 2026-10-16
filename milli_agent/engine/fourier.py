"""
Harmonic Fourier Coordinate Projector for the Milli 4D Spatiotemporal Manifold.
Maps low-dimensional coordinates into high-frequency orthogonal feature spaces,
locking static background geometry S(x, y) into invariant representations.
"""

import numpy as np


class FourierCoordinateProjector:
    """
    Projects 2D coordinates x in [0, 1]^2 into harmonic Fourier features:
    gamma(x) = [cos(2*pi*B*x), sin(2*pi*B*x)]^T
    """

    def __init__(self, num_frequencies: int = 16, scale: float = 10.0, seed: int = 42):
        self.num_frequencies = num_frequencies
        self.scale = scale
        rng = np.random.RandomState(seed)
        # Random Gaussian projection matrix B in R^(num_frequencies x 2)
        self.B = rng.normal(scale=scale, size=(num_frequencies, 2)).astype(np.float32)

    def project(self, coords: np.ndarray) -> np.ndarray:
        """
        Args:
            coords: Array of shape (N, 2) in normalized [0, 1] range.
        Returns:
            features: Array of shape (N, 2 * num_frequencies).
        """
        # coords @ B.T -> (N, num_frequencies)
        proj = 2.0 * np.pi * np.matmul(coords, self.B.T)
        return np.concatenate([np.cos(proj), np.sin(proj)], axis=-1)

    def extract_static_signature(self, image_gray: np.ndarray) -> dict:
        """
        Extracts a compact Fourier geometric fingerprint of static screen scaffolds.
        Returns ~160 token equivalent representation.
        """
        h, w = image_gray.shape
        # Downsample to feature grid
        grid_y, grid_x = np.mgrid[0:h:32, 0:w:32]
        coords = np.stack([grid_x.ravel() / max(w, 1), grid_y.ravel() / max(h, 1)], axis=-1)
        fourier_feats = self.project(coords)
        sampled_vals = image_gray[grid_y.ravel(), grid_x.ravel()] / 255.0

        # Mean frequency amplitudes
        weights = np.mean(fourier_feats * sampled_vals[:, None], axis=0)
        return {
            "scale": float(self.scale),
            "num_frequencies": self.num_frequencies,
            "weights": weights.tolist()[:16],  # Compact summary
            "token_footprint": 156
        }

"""Pulse shaping filters: manual implementations of RRC, RC, Gaussian, Rectangular."""

import logging
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class FilterType(str, Enum):
    NONE = "none"
    ROOT_RAISED_COSINE = "root_raised_cosine"
    RAISED_COSINE = "raised_cosine"
    GAUSSIAN = "gaussian"
    RECTANGULAR = "rectangular"


class PulseShaper:
    """Generates and applies pulse shaping filters."""

    def __init__(self, filter_type: str = "none",
                 num_taps: int = 11, span_symbols: int = 10,
                 roll_off: float = 0.35, bt_product: float = 0.35,
                 samples_per_symbol: int = 1):
        self.filter_type = FilterType(filter_type)
        self._num_taps = num_taps
        self.span_symbols = span_symbols
        self.roll_off = roll_off
        self.bt_product = bt_product
        self.samples_per_symbol = samples_per_symbol
        self._computed_taps: np.ndarray = np.array([])

    @property
    def num_taps(self) -> int:
        return self._num_taps

    @num_taps.setter
    def num_taps(self, value: int):
        self._num_taps = value

    @property
    def taps(self) -> np.ndarray:
        if self._computed_taps.size == 0:
            self._computed_taps = self._design_filter()
        return self._computed_taps

    @property
    def has_filter(self) -> bool:
        if self.filter_type == FilterType.NONE:
            return False
        _ = self.taps  # trigger computation
        return self._computed_taps.size > 0

    def _design_filter(self) -> np.ndarray:
        if self.filter_type == FilterType.NONE:
            taps = np.ones(self.samples_per_symbol, dtype=np.float64)
        elif self.filter_type == FilterType.RECTANGULAR:
            taps = np.ones(self.num_taps, dtype=np.float64)
        elif self.filter_type == FilterType.ROOT_RAISED_COSINE:
            taps = self._root_raised_cosine(self.num_taps, self.samples_per_symbol, self.roll_off)
        elif self.filter_type == FilterType.RAISED_COSINE:
            taps = self._raised_cosine(self.num_taps, self.samples_per_symbol, self.roll_off)
        elif self.filter_type == FilterType.GAUSSIAN:
            taps = self._gaussian(self.num_taps, self.samples_per_symbol, self.bt_product)
        else:
            raise ValueError(f"Unknown filter type: {self.filter_type}")

        # Normalize peak to 1.0
        peak = np.max(np.abs(taps))
        if peak > 0:
            taps = taps / peak
        return taps

    @staticmethod
    def _root_raised_cosine(num_taps: int, sps: int, alpha: float) -> np.ndarray:
        """Root Raised Cosine filter."""
        half_span = num_taps // 2
        n = np.arange(num_taps) - half_span
        T = sps
        taps = np.zeros_like(n, dtype=np.float64)
        eps = 1e-12

        for i, ni in enumerate(n):
            if abs(ni) < eps:
                taps[i] = 1.0 + (alpha / np.pi) * (4 - np.pi)
            elif alpha > 0 and abs(ni) == T / (4 * alpha):
                taps[i] = (alpha / (np.pi * 4)) * (
                    (1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha))
                    + (1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha))
                )
            else:
                tn = ni / T
                alpha_val = alpha if alpha >= 1e-10 else 1e-10
                num = np.sin(np.pi * tn / alpha_val) * np.cos(np.pi * tn * (1 + alpha))
                den = (np.pi * tn) * (1 - (4 * alpha * tn) ** 2)
                if abs(den) < eps:
                    taps[i] = 0.0
                else:
                    taps[i] = num / den

        return taps

    @staticmethod
    def _raised_cosine(num_taps: int, sps: int, alpha: float) -> np.ndarray:
        """Full Raised Cosine filter."""
        half_span = num_taps // 2
        n = np.arange(num_taps) - half_span
        T = sps
        taps = np.zeros_like(n, dtype=np.float64)
        eps = 1e-12

        for i, ni in enumerate(n):
            tn = ni / T
            if abs(tn) < eps:
                taps[i] = 1.0
            else:
                cos_term = np.cos(np.pi * alpha * tn)
                denom = 1.0 - (2 * alpha * tn) ** 2
                if abs(denom) < eps:
                    taps[i] = np.pi / (4 * alpha) * np.sin(np.pi * (1 + alpha) * tn)
                else:
                    taps[i] = (np.sin(np.pi * tn) / (np.pi * tn)) * cos_term / denom

        return taps

    @staticmethod
    def _gaussian(num_taps: int, sps: int, bt: float) -> np.ndarray:
        """Gaussian filter using BT product."""
        half_span = num_taps // 2
        t_norm = (np.arange(num_taps) - half_span) / sps
        sigma = bt / (2 * np.sqrt(2 * np.log(2)))
        raw_taps = np.exp(-0.5 * (t_norm / sigma) ** 2)
        return raw_taps

    def apply(self, symbols: np.ndarray) -> np.ndarray:
        """Apply the filter to upsampled symbols via convolution."""
        if not self.has_filter:
            return symbols.copy()

        taps = self.taps
        real_filtered = np.convolve(symbols.real, taps, mode="full")
        imag_filtered = np.convolve(symbols.imag, taps, mode="full")
        return real_filtered + 1j * imag_filtered


def create_shaper(filter_type: str = "none",
                  num_taps: int = 11, span_symbols: int = 10,
                  roll_off: float = 0.35, bt_product: float = 0.35,
                  samples_per_symbol: int = 1) -> PulseShaper:
    """Convenience function to create a pulse shaper."""
    return PulseShaper(
        filter_type=filter_type,
        num_taps=num_taps,
        span_symbols=span_symbols,
        roll_off=roll_off,
        bt_product=bt_product,
        samples_per_symbol=samples_per_symbol,
    )

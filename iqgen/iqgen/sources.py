"""Data sources: generate bitstreams for signal generation."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def generate(self, num_bits: int) -> np.ndarray:
        """Generate a bitstream."""
        ...


class RandomDataSource(DataSource):
    """Random binary bit generation."""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        if self.seed is not None:
            self._rng = np.random.default_rng(self.seed)
        else:
            self._rng = np.random.default_rng()

    def generate(self, num_bits: int) -> np.ndarray:
        if num_bits <= 0:
            logger.warning("Requested 0 or negative bits from random source")
            return np.array([], dtype=np.float64)

        bits = self._rng.integers(0, 2, size=num_bits)
        return bits.astype(np.float64)


class FileDataSource(DataSource):
    """Read bits from a binary file."""

    def __init__(self, file_path: str, bit_order: str = "lsb_first",
                 payload_bytes: Optional[int] = None):
        self.file_path = file_path
        self.bit_order = bit_order
        self.payload_bytes = payload_bytes

        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Input file not found: {file_path}")

    def generate(self, num_bits: int) -> np.ndarray:
        file_size = Path(self.file_path).stat().st_size
        read_bytes = self.payload_bytes or file_size
        read_bytes = min(read_bytes, file_size)

        if read_bytes <= 0:
            logger.warning("Requested 0 bytes from file source")
            return np.array([], dtype=np.float64)

        with open(self.file_path, "rb") as f:
            data = f.read(read_bytes)

        num_produced_bits = len(data) * 8
        if num_produced_bits < num_bits:
            logger.warning(
                f"File contains {num_produced_bits} bits, "
                f"requested {num_bits}. Using available bits."
            )
            num_bits = num_produced_bits

        bits = np.zeros(num_produced_bits, dtype=np.float64)
        for byte_idx in range(len(data)):
            byte_val = data[byte_idx]
            for bit_pos in range(8):
                if self.bit_order == "lsb_first":
                    bit_idx = byte_idx * 8 + bit_pos
                    bits[bit_idx] = float((byte_val >> bit_pos) & 1)
                else:
                    bit_idx = byte_idx * 8 + (7 - bit_pos)
                    bits[bit_idx] = float((byte_val >> bit_pos) & 1)

        return bits[:num_bits]


class BitstringDataSource(DataSource):
    """Read bits from an inline bitstring."""

    def __init__(self, bitstring: str):
        self.bitstring = bitstring

    def generate(self, num_bits: int) -> np.ndarray:
        s = self.bitstring.strip()
        total = len(s)
        if total < num_bits:
            logger.warning(
                f"Bitstring has {total} bits, requested {num_bits}. "
                f"Using all available bits."
            )
            num_bits = total

        bits = np.zeros(num_bits, dtype=np.float64)
        for i in range(num_bits):
            bits[i] = float(s[i] == "1")
        return bits


class ConfigDataSource(DataSource):
    """Configuration-based bit source."""

    def __init__(self, seed: int = 42):
        self._rng = np.random.default_rng(seed)

    def generate(self, num_bits: int) -> np.ndarray:
        if num_bits <= 0:
            return np.array([], dtype=np.float64)
        return self._rng.integers(0, 2, size=num_bits).astype(np.float64)


SOURCE_REGISTRY = {
    "random": RandomDataSource,
    "file": FileDataSource,
    "bitstring": BitstringDataSource,
    "config": ConfigDataSource,
}


def create_data_source(source: str, **kwargs) -> DataSource:
    """Factory function to create a data source."""
    source_class = SOURCE_REGISTRY.get(source)
    if source_class is None:
        raise ValueError(
            f"Unknown data source '{source}'. "
            f"Valid: {sorted(SOURCE_REGISTRY.keys())}"
        )
    return source_class(**kwargs)

"""Modulation mappers: bit-to-symbol mapping for all supported modulation types.

All constellations use Gray coding. Differential variants encode symbol as
rotation from the previous symbol. OQPSK returns (I, Q) separately for
offset processing.
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class ModulationType(str, Enum):
    BPSK = "bpsk"
    DBPSK = "dbpsk"
    QPSK = "qpsk"
    DQPSK = "dqpsk"
    PI4_QPSK = "pi4_qpsk"
    OQPSK = "oqpsk"
    PSK8 = "8psk"
    D8PSK = "d8psk"
    PI4_8PSK = "pi4_8psk"


# Gray code lookup tables
BPSK_GRAY_CONSTELLATION = [np.pi, 0.0]

QPSK_GRAY_CONSTELLATION = [
    0.0,            # 00 -> phase 0
    np.pi / 2,      # 01 -> phase 90
    np.pi,          # 11 -> phase 180
    3 * np.pi / 2,  # 10 -> phase 270
]

PSK8_GRAY_ORDER = [0, 1, 3, 2, 6, 7, 5, 4]

PI4_QPSK_SET_A = [0.0, np.pi / 2, np.pi, 3 * np.pi / 2]
PI4_QPSK_SET_B = [np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4, 7 * np.pi / 4]


def _bits_to_int(bits: np.ndarray) -> int:
    val = 0
    for b in bits:
        val = (val << 1) | int(round(b))
    return val


def _int_to_bits(value: int, num_bits: int) -> np.ndarray:
    bits = np.zeros(num_bits, dtype=np.float64)
    for i in range(num_bits - 1, -1, -1):
        bits[i] = value & 1
        value >>= 1
    return bits


class ModulationMapper(ABC):
    """Base class for modulation mappers."""

    def __init__(self, bits_per_symbol: int, gray_coding: bool = True,
                 initial_phase: float = 0.0):
        self.bits_per_symbol = bits_per_symbol
        self.gray_coding = gray_coding
        self.initial_phase = initial_phase

    @abstractmethod
    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        """Map a flat bit array to complex symbols."""
        ...

    def __call__(self, bit_array: np.ndarray) -> np.ndarray:
        return self.map_symbols(bit_array)


class BPSKMapper(ModulationMapper):
    """Binary PSK: 1 bit per symbol, constellation at +1/-1."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        num_symbols = len(bit_array)
        symbols = np.zeros(num_symbols, dtype=np.complex128)
        for i in range(num_symbols):
            bit = int(round(bit_array[i]))
            phase = BPSK_GRAY_CONSTELLATION[bit]
            symbols[i] = np.exp(1j * phase)
        return symbols


class DBPSKMapper(ModulationMapper):
    """Differential BPSK: encodes as rotation from previous symbol."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        num_symbols = len(bit_array)
        symbols = np.zeros(num_symbols, dtype=np.complex128)

        prev_phase = self.initial_phase
        for i in range(num_symbols):
            bit = int(round(bit_array[i]))
            rotation = 0.0 if bit == 0 else np.pi
            prev_phase = (prev_phase + rotation) % (2 * np.pi)
            symbols[i] = np.exp(1j * prev_phase)
        return symbols


class QPSKMapper(ModulationMapper):
    """QPSK: 2 bits per symbol, Gray coded."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        if len(bit_array) % 2 != 0:
            bit_array = np.append(bit_array, 0.0)

        num_symbols = len(bit_array) // 2
        symbols = np.zeros(num_symbols, dtype=np.complex128)

        for i in range(num_symbols):
            bits = bit_array[2 * i:2 * i + 2]
            idx = _bits_to_int(bits)
            phase = QPSK_GRAY_CONSTELLATION[idx]
            symbols[i] = np.exp(1j * phase)
        return symbols


class DQPSKMapper(ModulationMapper):
    """Differential QPSK: encodes as rotation from previous symbol."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        if len(bit_array) % 2 != 0:
            bit_array = np.append(bit_array, 0.0)

        num_symbols = len(bit_array) // 2
        symbols = np.zeros(num_symbols, dtype=np.complex128)

        prev_phase = self.initial_phase
        for i in range(num_symbols):
            bits = bit_array[2 * i:2 * i + 2]
            idx = _bits_to_int(bits)
            rotation = QPSK_GRAY_CONSTELLATION[idx]
            prev_phase = (prev_phase + rotation) % (2 * np.pi)
            symbols[i] = np.exp(1j * prev_phase)
        return symbols


class PI4QPSKMapper(ModulationMapper):
    """Pi/4 QPSK: rotates between two constellation sets by pi/4."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        if len(bit_array) % 2 != 0:
            bit_array = np.append(bit_array, 0.0)

        num_symbols = len(bit_array) // 2
        symbols = np.zeros(num_symbols, dtype=np.complex128)

        for i in range(num_symbols):
            bits = bit_array[2 * i:2 * i + 2]
            idx = _bits_to_int(bits)

            if i % 2 == 0:
                phase = PI4_QPSK_SET_A[idx]
            else:
                phase = PI4_QPSK_SET_B[idx]

            symbols[i] = np.exp(1j * phase)
        return symbols


class OQPSKMapper(ModulationMapper):
    """Offset QPSK: I and Q channels offset by half a symbol period."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        if len(bit_array) % 2 != 0:
            bit_array = np.append(bit_array, 0.0)

        num_symbols = len(bit_array) // 2
        I = np.zeros(num_symbols, dtype=np.complex128)
        Q = np.zeros(num_symbols, dtype=np.complex128)

        for i in range(num_symbols):
            bits = bit_array[2 * i:2 * i + 2]
            bit_i = int(round(bits[0]))
            bit_q = int(round(bits[1]))

            I_val = 1.0 if bit_i == 0 else -1.0
            Q_val = 1.0 if bit_q == 0 else -1.0

            I[i] = (I_val + 0j) / np.sqrt(2)
            Q[i] = (Q_val + 0j) / np.sqrt(2)

        return (I, Q)

    @property
    def is_offset(self) -> bool:
        return True


class PSK8Mapper(ModulationMapper):
    """8-PSK: 3 bits per symbol, Gray coded."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        if len(bit_array) % 3 != 0:
            padding = 3 - (len(bit_array) % 3)
            bit_array = np.append(bit_array, np.zeros(padding))

        num_symbols = len(bit_array) // 3
        symbols = np.zeros(num_symbols, dtype=np.complex128)

        for i in range(num_symbols):
            bits = bit_array[3 * i:3 * i + 3]
            idx = _bits_to_int(bits)
            gray_idx = PSK8_GRAY_ORDER[idx]
            phase = 2 * np.pi * gray_idx / 8
            symbols[i] = np.exp(1j * phase)
        return symbols


class D8PSKMapper(ModulationMapper):
    """Differential 8-PSK: encodes as rotation from previous symbol."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        if len(bit_array) % 3 != 0:
            padding = 3 - (len(bit_array) % 3)
            bit_array = np.append(bit_array, np.zeros(padding))

        num_symbols = len(bit_array) // 3
        symbols = np.zeros(num_symbols, dtype=np.complex128)

        prev_phase = self.initial_phase
        for i in range(num_symbols):
            bits = bit_array[3 * i:3 * i + 3]
            idx = _bits_to_int(bits)
            gray_idx = PSK8_GRAY_ORDER[idx]
            rotation = 2 * np.pi * gray_idx / 8
            prev_phase = (prev_phase + rotation) % (2 * np.pi)
            symbols[i] = np.exp(1j * prev_phase)
        return symbols


class PI4_8PSKMapper(ModulationMapper):
    """Pi/4 8-PSK: rotates between two 8-PSK constellations."""

    def map_symbols(self, bit_array: np.ndarray) -> np.ndarray:
        if len(bit_array) % 3 != 0:
            padding = 3 - (len(bit_array) % 3)
            bit_array = np.append(bit_array, np.zeros(padding))

        num_symbols = len(bit_array) // 3
        symbols = np.zeros(num_symbols, dtype=np.complex128)

        for i in range(num_symbols):
            bits = bit_array[3 * i:3 * i + 3]
            idx = _bits_to_int(bits)
            gray_idx = PSK8_GRAY_ORDER[idx]

            if i % 2 == 0:
                phase = 2 * np.pi * gray_idx / 8
            else:
                phase = 2 * np.pi * gray_idx / 8 + np.pi / 8

            symbols[i] = np.exp(1j * phase)
        return symbols


MODULATION_REGISTRY = {
    "bpsk": BPSKMapper,
    "dbpsk": DBPSKMapper,
    "qpsk": QPSKMapper,
    "dqpsk": DQPSKMapper,
    "pi4_qpsk": PI4QPSKMapper,
    "oqpsk": OQPSKMapper,
    "8psk": PSK8Mapper,
    "d8psk": D8PSKMapper,
    "pi4_8psk": PI4_8PSKMapper,
}


class ConstellationFactory:
    """Factory for creating modulation mappers."""

    @staticmethod
    def create(modulation: str, bits_per_symbol: Optional[int] = None,
               gray_coding: bool = True, initial_phase: float = 0.0):
        mapper_class = MODULATION_REGISTRY.get(modulation)
        if mapper_class is None:
            raise ValueError(
                f"Unknown modulation '{modulation}'. "
                f"Valid: {sorted(MODULATION_REGISTRY.keys())}"
            )

        return mapper_class(
            bits_per_symbol=bits_per_symbol,
            gray_coding=gray_coding,
            initial_phase=initial_phase,
        )


def create_mapper(modulation: str, bits_per_symbol: Optional[int] = None,
                  gray_coding: bool = True, initial_phase: float = 0.0):
    """Convenience function to create a modulation mapper."""
    return ConstellationFactory.create(
        modulation=modulation,
        bits_per_symbol=bits_per_symbol,
        gray_coding=gray_coding,
        initial_phase=initial_phase,
    )

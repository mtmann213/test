"""IQ Signal Generator: orchestrates the full signal generation pipeline.

Pipeline:
1. Load config and validate interconnected parameters
2. Generate bitstream from data source
3. Pad bits to be divisible by bits_per_symbol if needed
4. Map bits to constellation symbols
5. Upsample to samples_per_symbol per symbol
6. Apply pulse shaping filter
7. Normalize to peak_power
8. Write output (cf32 or SigMF)
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from .config import SignalConfig, create_config
from .mappers import create_mapper, ModulationMapper
from .sources import RandomDataSource, FileDataSource, BitstringDataSource
from .filters import PulseShaper
from .writers import create_writer, Cf32Writer, SigMFWriter

logger = logging.getLogger(__name__)


class IQGenerator:
    """Orchestrates IQ signal generation from configuration."""

    def __init__(self, config: SignalConfig):
        self.config = config
        self._mapper: Optional[ModulationMapper] = None
        self._shaper: Optional[PulseShaper] = None
        self._data_source = None

    def _create_mapper(self) -> ModulationMapper:
        return create_mapper(
            modulation=self.config.modulation,
            bits_per_symbol=self.config.bits_per_symbol,
            gray_coding=self.config.gray_coding,
            initial_phase=self.config.initial_phase,
        )

    def _create_shaper(self) -> PulseShaper:
        return PulseShaper(
            filter_type=self.config.filter_type,
            num_taps=self.config.num_taps,
            span_symbols=self.config.span_symbols,
            roll_off=self.config.roll_off,
            bt_product=self.config.bt_product,
            samples_per_symbol=self.config.samples_per_symbol,
        )

    def _create_data_source(self):
        if self.config.source == "random":
            return RandomDataSource(seed=42)
        elif self.config.source == "file":
            return FileDataSource(
                file_path=self.config.input_file,
                bit_order=self.config.bit_order,
                payload_bytes=self.config.payload_bytes,
            )
        elif self.config.source == "bitstring":
            logger.warning(
                "bitstring source selected but no bitstring provided. "
                "Using random source instead."
            )
            return RandomDataSource(seed=42)
        elif self.config.source == "config":
            from .sources import ConfigDataSource
            return ConfigDataSource(seed=42)
        else:
            raise ValueError(f"Unknown data source: {self.config.source}")

    def _pad_bits(self, bits: np.ndarray) -> np.ndarray:
        """Pad bits to be divisible by bits_per_symbol."""
        remainder = len(bits) % self.config.bits_per_symbol
        if remainder != 0:
            pad_amount = self.config.bits_per_symbol - remainder
            bits = np.pad(bits, (0, pad_amount), mode="constant")
            logger.warning(
                f"Padded {pad_amount} bits to make length divisible by "
                f"bits_per_symbol={self.config.bits_per_symbol}. "
                f"Total bits: {len(bits)}"
            )
        return bits

    def _upsample(self, symbols: np.ndarray, sps: int) -> np.ndarray:
        """Upsample symbols to samples_per_symbol per symbol."""
        if sps == 1:
            return symbols.copy()
        return np.repeat(symbols, sps)

    def _apply_oqpsk_offset(self, upsampled: np.ndarray, sps: int) -> np.ndarray:
        """Apply OQPSK half-symbol offset to Q channel."""
        total_symbols = len(upsampled) // sps
        result = np.zeros(len(upsampled), dtype=np.complex128)

        I = upsampled[0::2] if total_symbols > 0 else np.array([])
        Q = upsampled[1::2] if total_symbols > 0 else np.array([])

        offset = sps // 2
        Q_delayed = np.zeros_like(Q)
        Q_delayed[offset:] = Q[:-offset] if len(Q) > offset else np.array([])

        result[0::2] = I
        result[1::2] = Q_delayed

        return result

    def _normalize(self, samples: np.ndarray) -> np.ndarray:
        """Normalize samples to peak_power."""
        peak = np.max(np.abs(samples))
        if peak > 0:
            samples = samples * (self.config.peak_power / peak)
        return samples

    def _combine_oqpsk(self, I: np.ndarray, Q: np.ndarray) -> np.ndarray:
        """Combine OQPSK I and Q channels."""
        num_sym = len(I)
        combined = np.zeros(2 * num_sym, dtype=np.complex128)
        combined[0::2] = I
        combined[1::2] = Q
        return combined

    def generate(self) -> np.ndarray:
        """Run the full signal generation pipeline."""
        self._mapper = self._create_mapper()
        self._shaper = self._create_shaper()
        self._data_source = self._create_data_source()

        num_bits = self.config.total_bits
        logger.info(f"Generating {num_bits} bits from '{self.config.source}' source")
        bits = self._data_source.generate(num_bits)

        if len(bits) == 0:
            logger.warning("Empty bitstream generated")
            return np.array([], dtype=np.complex64)

        bits = self._pad_bits(bits)

        logger.info(
            f"Mapping {len(bits)} bits to symbols ({self.config.modulation}, "
            f"{self.config.bits_per_symbol} bits/symbol)"
        )
        if self.config.modulation == "oqpsk":
            I, Q = self._mapper.map_symbols(bits)
            symbols = self._combine_oqpsk(I, Q)
        else:
            symbols = self._mapper.map_symbols(bits)

        num_symbols = len(symbols)
        logger.info(f"Generated {num_symbols} symbols")

        sps = self.config.samples_per_symbol
        logger.info(f"Upsampling: {num_symbols} symbols -> {num_symbols * sps} samples")
        upsampled = self._upsample(symbols, sps)

        if self.config.modulation == "oqpsk":
            upsampled = self._apply_oqpsk_offset(upsampled, sps)

        logger.info(
            f"Applying {self.config.filter_type} filter "
            f"({self.config.num_taps} taps)"
        )
        filtered = self._shaper.apply(upsampled)

        filtered = self._normalize(filtered)

        return filtered.astype(np.complex64)

    def generate_and_write(self) -> Tuple[str, Optional[str]]:
        """Generate signal and write to file."""
        logger.info(
            f"Starting signal generation: {self.config.name}, "
            f"{self.config.modulation}, {self.config.filter_type}"
        )

        samples = self.generate()

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        writer = create_writer(self.config.output_format)

        if self.config.output_format == "cf32":
            filename = self.config.get_output_filename()
            path = str(output_dir / filename)
            Cf32Writer().write(samples, path)
            return (path, None)

        elif self.config.output_format == "sigmf":
            filename_base = self.config.get_output_filename()
            data_path, meta_path = SigMFWriter().write(
                samples, str(output_dir), filename_base, self.config
            )
            return (data_path, meta_path)

        else:
            raise ValueError(f"Unsupported output format: {self.config.output_format}")

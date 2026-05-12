"""Signal configuration: YAML loading, validation, interconnected parameter resolution."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

VALID_MODULATIONS = {
    "bpsk", "dbpsk", "qpsk", "dqpsk", "pi4_qpsk", "oqpsk",
    "8psk", "d8psk", "pi4_8psk",
}

VALID_SOURCES = {"random", "file", "bitstring", "config"}

VALID_FILTERS = {"none", "root_raised_cosine", "raised_cosine", "gaussian", "rectangular"}

VALID_FORMATS = {"cf32", "sigmf"}

VALID_BIT_ORDERS = {"lsb_first", "msb_first"}

BPS_MAP = {
    "bpsk": 1,
    "dbpsk": 1,
    "qpsk": 2,
    "dqpsk": 2,
    "pi4_qpsk": 2,
    "oqpsk": 2,
    "8psk": 3,
    "d8psk": 3,
    "pi4_8psk": 3,
}


class FilterType(str, Enum):
    NONE = "none"
    ROOT_RAISED_COSINE = "root_raised_cosine"
    RAISED_COSINE = "raised_cosine"
    GAUSSIAN = "gaussian"
    RECTANGULAR = "rectangular"


@dataclass
class SignalConfig:
    """YAML-backed configuration for IQ signal generation.

    Resolves interconnected parameters:
    - symbol_rate = bitrate / bits_per_symbol
    - samples_per_symbol = sample_rate / symbol_rate (rounded to int)
    - num_taps = span_symbols * samples_per_symbol + 1
    """

    # Signal parameters
    name: str
    center_frequency_hz: float
    sample_rate: float
    peak_power: float = 1.0
    output_dir: str = "."
    add_timestamp: bool = True
    timestamp_format: str = "%Y%m%d_%H%M%S"

    # Data source
    source: str = "random"
    bit_count: int = 1000
    duration_sec: Optional[float] = None
    payload_bytes: int = 1024
    input_file: Optional[str] = None
    bit_order: str = "lsb_first"

    # Modulation
    modulation: str = "qpsk"
    gray_coding: bool = True
    initial_phase: float = 0.0

    # Rate parameters (interconnected)
    bitrate: Optional[float] = None
    symbol_rate_override: Optional[float] = None
    samples_per_symbol_override: Optional[int] = None

    # Pulse shaping
    filter_type: str = "none"
    span_symbols: int = 10
    roll_off: float = 0.35
    bt_product: float = 0.35
    num_taps_override: Optional[int] = None

    # Output format
    output_format: str = "cf32"

    # Resolved (computed) values
    _bits_per_symbol: int = field(init=False, default=1)
    _symbol_rate: float = field(init=False, default=1e6)
    _samples_per_symbol: int = field(init=False, default=1)
    _num_taps: int = field(init=False, default=11)
    _total_bits: int = field(init=False, default=1000)

    def __post_init__(self):
        self._bits_per_symbol = BPS_MAP.get(self.modulation, 1)
        self._resolve_rates()
        self._resolve_filter_taps()
        self._resolve_total_bits()

    def _resolve_rates(self):
        """Resolve interconnected rate parameters.

        Priority:
        1. If bitrate is set, compute symbol_rate and samples_per_symbol from it.
        2. If bitrate and samples_per_symbol are both set, compute symbol_rate.
        3. If bitrate and symbol_rate are both set, compute samples_per_symbol.
        4. If user overrides symbol_rate or samples_per_symbol, log warnings.
        """
        if not self.bitrate:
            raise ValueError("bitrate is required and must be a positive number")

        if self.bitrate <= 0:
            raise ValueError(f"bitrate must be positive, got {self.bitrate}")

        if self.sample_rate <= 0:
            raise ValueError(f"sample_rate must be positive, got {self.sample_rate}")

        if self.samples_per_symbol_override is not None:
            logger.warning(
                f"samples_per_symbol was provided ({self.samples_per_symbol_override}). "
                f"It will be overridden by computed value from sample_rate/bitrate."
            )

        if self.symbol_rate_override is not None:
            logger.warning(
                f"symbol_rate was provided ({self.symbol_rate_override}). "
                f"It will be overridden by computed value from bitrate/bps."
            )

        # Compute from bitrate
        self._symbol_rate = self.bitrate / self._bits_per_symbol

        # Compute samples_per_symbol
        raw_sps = self.sample_rate / self._symbol_rate
        rounded_sps = int(round(raw_sps))

        if rounded_sps <= 0:
            raise ValueError(
                f"Computed samples_per_symbol={rounded_sps} <= 0. "
                f"Check sample_rate ({self.sample_rate}), bitrate ({self.bitrate}), "
                f"and modulation ({self.modulation}) compatibility."
            )

        # Warn if rounding introduces significant error
        actual_sps = self.sample_rate / self._symbol_rate
        if abs(actual_sps - rounded_sps) > 0.01 * rounded_sps:
            logger.warning(
                f"samples_per_symbol rounded from {actual_sps:.4f} to {rounded_sps}. "
                f"Actual sample rate will be {rounded_sps * self._symbol_rate:.0f} Hz "
                f"instead of {self.sample_rate:.0f} Hz."
            )

        self._samples_per_symbol = rounded_sps

    def _resolve_filter_taps(self):
        """Resolve filter tap count from span_symbols and samples_per_symbol."""
        if self._samples_per_symbol is None:
            raise ValueError("samples_per_symbol must be resolved before filter taps")

        if self.num_taps_override is not None:
            logger.warning(
                f"num_taps was provided ({self.num_taps_override}). "
                f"It will be overridden by computed value."
            )
            self._num_taps = self.num_taps_override
        else:
            self._num_taps = self.span_symbols * self._samples_per_symbol + 1

    def _resolve_total_bits(self):
        """Resolve total number of bits to generate."""
        if self.duration_sec is not None:
            if self.duration_sec <= 0:
                raise ValueError(f"duration_sec must be positive, got {self.duration_sec}")
            self._total_bits = int(self.duration_sec * self.bitrate)
            if self._total_bits <= 0:
                raise ValueError(
                    f"Computed total_bits={self._total_bits} <= 0. "
                    f"Check duration_sec ({self.duration_sec}) and bitrate ({self.bitrate})"
                )
        else:
            self._total_bits = self.bit_count

    @property
    def bits_per_symbol(self) -> int:
        return self._bits_per_symbol

    @property
    def symbol_rate(self) -> float:
        return self._symbol_rate

    @property
    def samples_per_symbol(self) -> int:
        return self._samples_per_symbol

    @property
    def num_taps(self) -> int:
        return self._num_taps

    @property
    def total_bits(self) -> int:
        return self._total_bits

    def validate(self) -> None:
        """Validate configuration values."""
        if self.modulation not in VALID_MODULATIONS:
            raise ValueError(
                f"Unknown modulation '{self.modulation}'. "
                f"Valid: {sorted(VALID_MODULATIONS)}"
            )

        if self.source not in VALID_SOURCES:
            raise ValueError(
                f"Unknown source '{self.source}'. "
                f"Valid: {sorted(VALID_SOURCES)}"
            )

        if self.output_format not in VALID_FORMATS:
            raise ValueError(
                f"Unknown format '{self.output_format}'. "
                f"Valid: {sorted(VALID_FORMATS)}"
            )

        if self.filter_type not in VALID_FILTERS:
            raise ValueError(
                f"Unknown filter '{self.filter_type}'. "
                f"Valid: {sorted(VALID_FILTERS)}"
            )

        if self.bit_order not in VALID_BIT_ORDERS:
            raise ValueError(
                f"Unknown bit_order '{self.bit_order}'. "
                f"Valid: {sorted(VALID_BIT_ORDERS)}"
            )

        if self.source == "file" and not self.input_file:
            raise ValueError("input_file is required when source='file'")

        if self.source == "random" and self.bit_count <= 0:
            raise ValueError("bit_count must be positive for random source")

        if self.source == "file" and not Path(self.input_file).is_file():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        if self.peak_power <= 0:
            raise ValueError(f"peak_power must be positive, got {self.peak_power}")

        if self.span_symbols < 1:
            raise ValueError(f"span_symbols must be >= 1, got {self.span_symbols}")

        if self.roll_off < 0 or self.roll_off > 1:
            raise ValueError(f"roll_off must be in [0, 1], got {self.roll_off}")

        if self.bt_product <= 0:
            raise ValueError(f"bt_product must be positive, got {self.bt_product}")

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def get_output_filename(self, is_data: bool = False) -> str:
        """Generate output filename based on config parameters."""
        ts = ""
        if self.add_timestamp:
            from datetime import datetime
            ts = datetime.now().strftime(self.timestamp_format) + "_"

        fmt = self.output_format

        if fmt == "sigmf":
            base = f"{ts}{self.name}_{self.modulation}_{int(self.bitrate)}Hz_{int(self.sample_rate)}Hz"
            if is_data:
                return f"{base}.sigmf-data"
            else:
                return f"{base}.sigmf-meta"
        else:
            ext = "cf32" if self.output_format == "cf32" else self.output_format
            return f"{ts}{self.name}_{self.modulation}_{int(self.bitrate)}Hz_{int(self.sample_rate)}Hz.{ext}"


def create_config(yaml_path: str) -> SignalConfig:
    """Load and validate SignalConfig from a YAML file."""
    yaml_path = Path(yaml_path)
    if not yaml_path.is_file():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        raw = yaml.safe_load(f)

    if not raw or "iq_generator" not in raw:
        raise ValueError("Config must contain an 'iq_generator' section")

    cfg_raw = raw["iq_generator"]

    def _normalize(key: str) -> str:
        return key.replace("-", "_").replace(" ", "_")

    cfg_clean = {}
    for k, v in cfg_raw.items():
        cfg_clean[_normalize(k)] = v

    def _to_numeric(val, default=None):
        if val is None:
            return default
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            val = val.strip()
            try:
                if "." in val or "e" in val.lower():
                    return float(val)
                return int(val)
            except ValueError:
                return default
        return default

    def _get(name, default=None):
        val = cfg_clean.get(name, default)
        return val

    name = _get("name", "signal")
    center_freq = _to_numeric(_get("center_frequency_hz", 2.4e9))
    sample_rate = _to_numeric(_get("sample_rate", 1e6))
    peak_power = _to_numeric(_get("peak_power"), 1.0)
    output_dir = _get("output_dir", ".")
    add_timestamp = _get("timestamp", True)
    if isinstance(add_timestamp, str):
        add_timestamp = add_timestamp.lower() in ("true", "1", "yes")
    timestamp_format = _get("timestamp_format", "%Y%m%d_%H%M%S")

    source = _get("source", "random")
    bit_count = _to_numeric(_get("bit_count", 1000)) or 1000
    duration_sec = _to_numeric(_get("duration_sec"))
    payload_bytes = _to_numeric(_get("payload_bytes", 1024)) or 1024
    input_file = _get("input_file")
    bit_order = _get("bit_order", "lsb_first")

    modulation = _get("modulation", "qpsk")
    gray_coding = _get("gray_coding", True)
    if isinstance(gray_coding, str):
        gray_coding = gray_coding.lower() in ("true", "1", "yes")
    initial_phase = _to_numeric(_get("initial_phase", 0.0))

    bitrate = _to_numeric(_get("bitrate"))
    symbol_rate = _to_numeric(_get("symbol_rate"))
    samples_per_symbol = _to_numeric(_get("samples_per_symbol"))

    filter_type = _get("filter_type", "none")
    span_symbols = _to_numeric(_get("span_symbols", 10)) or 10
    roll_off = _to_numeric(_get("roll_off", 0.35))
    bt_product = _to_numeric(_get("bt_product", 0.35))
    num_taps = _to_numeric(_get("num_taps"))

    output_format = _get("output_format", "cf32")

    config = SignalConfig(
        name=name,
        center_frequency_hz=center_freq,
        sample_rate=sample_rate,
        peak_power=peak_power,
        output_dir=output_dir,
        add_timestamp=add_timestamp,
        timestamp_format=timestamp_format,
        source=source,
        bit_count=bit_count,
        duration_sec=duration_sec,
        payload_bytes=payload_bytes,
        input_file=input_file,
        bit_order=bit_order,
        modulation=modulation,
        gray_coding=gray_coding,
        initial_phase=initial_phase or 0.0,
        bitrate=bitrate,
        symbol_rate_override=symbol_rate,
        samples_per_symbol_override=samples_per_symbol,
        filter_type=filter_type,
        span_symbols=span_symbols,
        roll_off=roll_off,
        bt_product=bt_product,
        num_taps_override=num_taps,
        output_format=output_format,
    )

    config.validate()
    return config

"""Output writers: cf32 and SigMF format file generation."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class Cf32Writer:
    """Write IQ samples as complex32 binary (cf32) format."""

    @staticmethod
    def write(samples: np.ndarray, output_path: str) -> str:
        """Write samples to file in cf32 format."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cf32_array = samples.astype(np.complex64)
        cf32_array.tofile(output_path)

        file_size = Path(output_path).stat().st_size
        logger.info(f"Wrote {cf32_array.size} cf32 samples ({file_size} bytes) to {output_path}")
        return str(Path(output_path).resolve())


class SigMFWriter:
    """Write IQ samples in SigMF (Signal Metadata Format) standard."""

    def write(self, samples: np.ndarray, output_dir: str,
              filename_base: str, config) -> tuple:
        """Write SigMF data and metadata files."""
        data_path = Path(output_dir) / f"{filename_base}.sigmf-data"
        meta_path = Path(output_dir) / f"{filename_base}.sigmf-meta"

        cf32_array = samples.astype(np.complex64)
        cf32_array.tofile(str(data_path))
        logger.info(f"Wrote {cf32_array.size} complex32 samples to {data_path}")

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        global_info = {
            # SigMF standard global fields:
            "core:version": "1.0.0",
            "core:num_channels": 1,
            # core:datatype - cf32_le = complex float32 little-endian
            # Alternatives: ci32_le, cu8_cplxs8, cu16_cplxs16, cu32_f32le, ci64_le, cu64_le, cu8_le, ci8_le
            "core:datatype": "cf32_le",
            "core:sample_rate": config.sample_rate,
            "core:frequency": config.center_frequency_hz,
            "core:datetime": now,
            "core:hardware": "IQ Generator",
            "core:description": (
                f"{config.name} signal, {config.modulation} modulation, "
                f"{config.bitrate/1000:.1f} kbps, "
                f"{config.sample_rate/1e6:.1f} Msps, "
                f"{config.filter_type} pulse shaping"
            ),
            "core:author": "IQ Generator",
            "core:license": "MIT",
            # Optional SigMF fields for reference:
            # core:meta_doi, core:recording_doi, core:triggers, core:location,
            # core:geo_reference, core:metric, core:treble, core:bass,
            # core:balance, core:gain
        }

        captures = [
            {
                "core:sample_start": 0,
                "core:datetime": now,
                "core:frequency": config.center_frequency_hz,
                "core:sample_rate": config.sample_rate,
                "core:header_bytes": 0,
            }
        ]

        annotations = self._build_annotations(config, len(samples))

        meta = {
            "global": global_info,
            "captures": captures,
            "annotations": annotations,
        }

        with open(str(meta_path), "w") as f:
            json.dump(meta, f, indent=2)

        logger.info(f"Wrote SigMF metadata to {meta_path}")
        return str(data_path.resolve()), str(meta_path.resolve())

    def _build_annotations(self, config, total_samples: int) -> list:
        """Build SigMF annotation records with modulation details."""
        bps = config.bits_per_symbol
        num_symbols = config.total_bits // bps

        filter_desc = config.filter_type
        extra_fields = {}

        if config.filter_type in ("root_raised_cosine", "raised_cosine"):
            extra_fields["roll_off"] = config.roll_off
            filter_desc += f", roll_off={config.roll_off}"
        elif config.filter_type == "gaussian":
            extra_fields["bt_product"] = config.bt_product
            filter_desc += f", BT={config.bt_product}"

        annotation = {
            "core:sample_start": 0,
            "core:sample_count": total_samples,
            "core:frequency": config.center_frequency_hz,
            "core:label": f"{config.name}_{config.modulation}",
            "modulation": config.modulation,
            "bits_per_symbol": config.bits_per_symbol,
            "sample_rate": config.sample_rate,
            "bitrate": config.bitrate,
            "samples_per_symbol": config.samples_per_symbol,
            "pulse_shaping": config.filter_type,
            "description": filter_desc,
            "center_frequency_hz": config.center_frequency_hz,
            "peak_power": config.peak_power,
            "data_source": config.source,
            "total_bits": config.total_bits,
            "num_symbols": num_symbols,
            "total_duration_sec": total_samples / config.sample_rate,
        }
        annotation.update(extra_fields)
        return [annotation]


def create_writer(output_format: str) -> object:
    """Factory function to create the appropriate writer."""
    if output_format == "cf32":
        return Cf32Writer()
    elif output_format == "sigmf":
        return SigMFWriter()
    else:
        raise ValueError(f"Unknown output format: {output_format}")

"""Comprehensive tests for IQ signal generator module."""

import json
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from iqgen.config import SignalConfig, create_config
from iqgen.mappers import (
    BPSKMapper, DBPSKMapper, QPSKMapper, DQPSKMapper,
    PI4QPSKMapper, OQPSKMapper, PSK8Mapper, D8PSKMapper,
    PI4_8PSKMapper, ConstellationFactory, create_mapper,
    _int_to_bits,
)
from iqgen.sources import (
    RandomDataSource, FileDataSource, BitstringDataSource,
    ConfigDataSource, create_data_source,
)
from iqgen.filters import PulseShaper, FilterType, create_shaper
from iqgen.writers import Cf32Writer, SigMFWriter, create_writer
from iqgen.generator import IQGenerator


class TestBPSKMapper(unittest.TestCase):
    def test_constellation_values(self):
        mapper = BPSKMapper(bits_per_symbol=1)
        bits = np.array([1.0, 0.0, 1.0, 0.0])
        symbols = mapper.map_symbols(bits)
        self.assertAlmostEqual(symbols[0].real, 1.0, places=5)
        self.assertAlmostEqual(symbols[1].real, -1.0, places=5)

    def test_unit_amplitude(self):
        mapper = BPSKMapper(bits_per_symbol=1)
        bits = np.array([0.0, 1.0])
        symbols = mapper.map_symbols(bits)
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)

    def test_output_length(self):
        mapper = BPSKMapper(bits_per_symbol=1)
        bits = np.zeros(100, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        self.assertEqual(len(symbols), 100)

    def test_gray_coding(self):
        mapper = BPSKMapper(bits_per_symbol=1, gray_coding=True)
        # bit 1 -> +1 (phase 0), bit 0 -> -1 (phase pi)
        symbols = mapper.map_symbols(np.array([0.0, 1.0]))
        self.assertLess(symbols[0].real, 0)
        self.assertGreater(symbols[1].real, 0)


class TestDBPSKMapper(unittest.TestCase):
    def test_differential_encoding(self):
        mapper = DBPSKMapper(bits_per_symbol=1, initial_phase=0.0)
        bits = np.zeros(10, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        for i in range(1, len(symbols)):
            self.assertAlmostEqual(np.angle(symbols[i]) - np.angle(symbols[i-1]), 0, places=5)

    def test_bit_one_rotation(self):
        mapper = DBPSKMapper(bits_per_symbol=1, initial_phase=0.0)
        # bit 0 -> no rotation, bit 1 -> pi rotation
        bits = np.array([1.0, 0.0, 0.0])
        symbols = mapper.map_symbols(bits)
        # After bit 1 (rotate pi) then bit 0 (no rotation), symbols are the same
        self.assertAlmostEqual(abs(symbols[0] - symbols[1]), 0, places=5)


class TestQPSKMapper(unittest.TestCase):
    def test_constellation_points(self):
        mapper = QPSKMapper(bits_per_symbol=2)
        symbols = mapper.map_symbols(np.array([0.0, 0.0]))
        self.assertAlmostEqual(symbols[0].real, 1.0, places=5)
        self.assertAlmostEqual(symbols[0].imag, 0.0, places=5)

    def test_all_four_points(self):
        mapper = QPSKMapper(bits_per_symbol=2)
        bit_patterns = [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]]
        all_bits = np.array(bit_patterns, dtype=np.float64).flatten()
        symbols = mapper.map_symbols(all_bits)
        self.assertEqual(len(symbols), 4)
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)

    def test_output_length(self):
        mapper = QPSKMapper(bits_per_symbol=2)
        bits = np.zeros(200, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        self.assertEqual(len(symbols), 100)


class TestDQPSKMapper(unittest.TestCase):
    def test_differential_rotation(self):
        mapper = DQPSKMapper(bits_per_symbol=2, initial_phase=0.0)
        bits = np.zeros(4, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        self.assertAlmostEqual(np.angle(symbols[1]) - np.angle(symbols[0]), 0, places=5)

    def test_unit_amplitude(self):
        mapper = DQPSKMapper(bits_per_symbol=2, initial_phase=0.0)
        bits = np.random.randint(0, 2, 20).astype(np.float64)
        symbols = mapper.map_symbols(bits)
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)


class TestPI4QPSKMapper(unittest.TestCase):
    def test_alternating_sets(self):
        mapper = PI4QPSKMapper(bits_per_symbol=2)
        bits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        self.assertAlmostEqual(np.angle(symbols[0]), 0.0, places=5)
        self.assertAlmostEqual(np.angle(symbols[1]), np.pi / 4, places=5)

    def test_unit_amplitude(self):
        mapper = PI4QPSKMapper(bits_per_symbol=2)
        bits = np.random.randint(0, 2, 20).astype(np.float64)
        symbols = mapper.map_symbols(bits)
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)


class TestOQPSKMapper(unittest.TestCase):
    def test_returns_tuple(self):
        mapper = OQPSKMapper(bits_per_symbol=2)
        bits = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float64)
        I, Q = mapper.map_symbols(bits)
        self.assertIsInstance(I, np.ndarray)
        self.assertIsInstance(Q, np.ndarray)

    def test_iq_values(self):
        mapper = OQPSKMapper(bits_per_symbol=2)
        bits = np.array([0.0, 0.0], dtype=np.float64)
        I, Q = mapper.map_symbols(bits)
        # Both I and Q should be 1/sqrt(2) for bits 00
        self.assertAlmostEqual(abs(I[0]), 1/np.sqrt(2), places=5)
        self.assertAlmostEqual(abs(Q[0]), 1/np.sqrt(2), places=5)

    def test_is_offset(self):
        mapper = OQPSKMapper(bits_per_symbol=2)
        self.assertTrue(mapper.is_offset)

    def test_output_length(self):
        mapper = OQPSKMapper(bits_per_symbol=2)
        bits = np.zeros(200, dtype=np.float64)
        I, Q = mapper.map_symbols(bits)
        self.assertEqual(len(I), 100)
        self.assertEqual(len(Q), 100)


class TestPSK8Mapper(unittest.TestCase):
    def test_8_points(self):
        mapper = PSK8Mapper(bits_per_symbol=3)
        bits = np.zeros(24, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        self.assertEqual(len(symbols), 8)

    def test_unit_amplitude(self):
        mapper = PSK8Mapper(bits_per_symbol=3)
        bits = np.random.randint(0, 2, 24).astype(np.float64)
        symbols = mapper.map_symbols(bits)
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)

    def test_eight_phase_separation(self):
        mapper = PSK8Mapper(bits_per_symbol=3)
        bits_list = []
        for i in range(8):
            bits_list.extend(_int_to_bits(i, 3).tolist())
        bits = np.array(bits_list, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        # All symbols should be on unit circle at multiples of pi/4
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)
            phase = np.angle(s)
            # Phase should be a multiple of pi/4
            self.assertAlmostEqual(phase / (np.pi / 4), round(phase / (np.pi / 4)), places=5)


class TestD8PSKMapper(unittest.TestCase):
    def test_unit_amplitude(self):
        mapper = D8PSKMapper(bits_per_symbol=3, initial_phase=0.0)
        bits = np.random.randint(0, 2, 24).astype(np.float64)
        symbols = mapper.map_symbols(bits)
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)

    def test_differential(self):
        mapper = D8PSKMapper(bits_per_symbol=3, initial_phase=0.0)
        bits = np.zeros(6, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        self.assertAlmostEqual(np.angle(symbols[1]) - np.angle(symbols[0]), 0, places=5)


class TestPI4_8PSKMapper(unittest.TestCase):
    def test_alternating_sets(self):
        mapper = PI4_8PSKMapper(bits_per_symbol=3)
        bits = np.zeros(6, dtype=np.float64)
        symbols = mapper.map_symbols(bits)
        phase_diff = abs(np.angle(symbols[1]) - np.angle(symbols[0]))
        self.assertAlmostEqual(phase_diff, np.pi / 8, delta=np.pi / 8)

    def test_unit_amplitude(self):
        mapper = PI4_8PSKMapper(bits_per_symbol=3)
        bits = np.random.randint(0, 2, 24).astype(np.float64)
        symbols = mapper.map_symbols(bits)
        for s in symbols:
            self.assertAlmostEqual(abs(s), 1.0, places=5)


class TestConstellationFactory(unittest.TestCase):
    def test_create_bpsk(self):
        self.assertIsInstance(ConstellationFactory.create("bpsk"), BPSKMapper)

    def test_create_qpsk(self):
        self.assertIsInstance(ConstellationFactory.create("qpsk"), QPSKMapper)

    def test_create_8psk(self):
        self.assertIsInstance(ConstellationFactory.create("8psk"), PSK8Mapper)

    def test_create_oqpsk(self):
        self.assertIsInstance(ConstellationFactory.create("oqpsk"), OQPSKMapper)

    def test_invalid_modulation(self):
        with self.assertRaises(ValueError):
            ConstellationFactory.create("invalid_mod")


class TestRandomDataSource(unittest.TestCase):
    def test_generation(self):
        source = RandomDataSource(seed=42)
        bits = source.generate(100)
        self.assertEqual(len(bits), 100)
        self.assertTrue(np.all((bits == 0) | (bits == 1)))

    def test_reproducibility(self):
        s1 = RandomDataSource(seed=42)
        s2 = RandomDataSource(seed=42)
        np.testing.assert_array_equal(s1.generate(50), s2.generate(50))

    def test_zero_bits(self):
        source = RandomDataSource(seed=42)
        self.assertEqual(len(source.generate(0)), 0)


class TestFileDataSource(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
        self.test_data = bytes([0b10101010, 0b11001100, 0b11110000, 0b00001111])
        self.test_file.write(self.test_data)
        self.test_file.close()

    def tearDown(self):
        os.unlink(self.test_file.name)

    def test_lsb_first(self):
        source = FileDataSource(self.test_file.name, bit_order="lsb_first", payload_bytes=4)
        bits = source.generate(32)
        self.assertEqual(len(bits), 32)
        self.assertEqual(bits[0], 0.0)
        self.assertEqual(bits[1], 1.0)

    def test_msb_first(self):
        source = FileDataSource(self.test_file.name, bit_order="msb_first", payload_bytes=4)
        bits = source.generate(32)
        self.assertEqual(len(bits), 32)
        self.assertEqual(bits[0], 1.0)
        self.assertEqual(bits[1], 0.0)

    def test_payload_bytes_limit(self):
        source = FileDataSource(self.test_file.name, bit_order="lsb_first", payload_bytes=2)
        bits = source.generate(32)
        self.assertEqual(len(bits), 16)


class TestBitstringDataSource(unittest.TestCase):
    def test_basic(self):
        source = BitstringDataSource("10110101")
        bits = source.generate(8)
        np.testing.assert_array_equal(bits, [1, 0, 1, 1, 0, 1, 0, 1])

    def test_partial_read(self):
        source = BitstringDataSource("10110101")
        bits = source.generate(4)
        np.testing.assert_array_equal(bits, [1, 0, 1, 1])

    def test_all_zeros(self):
        source = BitstringDataSource("00000000")
        bits = source.generate(8)
        np.testing.assert_array_equal(bits, [0, 0, 0, 0, 0, 0, 0, 0])


class TestPulseShaper(unittest.TestCase):
    def test_none_filter(self):
        shaper = PulseShaper(filter_type="none", num_taps=1, samples_per_symbol=1)
        self.assertTrue(np.allclose(shaper.taps, 1.0))

    def test_rectangular_filter(self):
        shaper = PulseShaper(filter_type="rectangular", num_taps=11, samples_per_symbol=1)
        self.assertEqual(len(shaper.taps), 11)
        self.assertAlmostEqual(np.max(np.abs(shaper.taps)), 1.0, places=10)

    def test_rrc_filter(self):
        shaper = PulseShaper(filter_type="root_raised_cosine", num_taps=21, samples_per_symbol=1, roll_off=0.35)
        self.assertEqual(len(shaper.taps), 21)
        self.assertAlmostEqual(np.max(np.abs(shaper.taps)), 1.0, places=10)

    def test_rc_filter(self):
        shaper = PulseShaper(filter_type="raised_cosine", num_taps=21, samples_per_symbol=1, roll_off=0.35)
        self.assertEqual(len(shaper.taps), 21)

    def test_gaussian_filter(self):
        shaper = PulseShaper(filter_type="gaussian", num_taps=21, samples_per_symbol=1, bt_product=0.35)
        self.assertEqual(len(shaper.taps), 21)
        self.assertAlmostEqual(np.max(shaper.taps), 1.0, places=10)

    def test_apply_none(self):
        shaper = PulseShaper(filter_type="none", num_taps=1, samples_per_symbol=1)
        symbols = np.array([1+0j, -1+0j, 0+1j])
        np.testing.assert_array_equal(shaper.apply(symbols), symbols)

    def test_apply_filter(self):
        shaper = PulseShaper(filter_type="rectangular", num_taps=3, samples_per_symbol=1)
        symbols = np.array([1+0j, 0+0j, -1+0j])
        result = shaper.apply(symbols)
        self.assertEqual(len(result), 5)

    def test_has_filter(self):
        self.assertFalse(PulseShaper(filter_type="none", num_taps=1, samples_per_symbol=1).has_filter)
        self.assertTrue(PulseShaper(filter_type="root_raised_cosine", num_taps=11, samples_per_symbol=1).has_filter)

    def test_num_taps_calculation(self):
        shaper = PulseShaper(filter_type="root_raised_cosine", num_taps=201, span_symbols=10, samples_per_symbol=20)
        self.assertEqual(shaper.num_taps, 201)


class TestSignalConfig(unittest.TestCase):
    def test_basic_config(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5)
        self.assertEqual(cfg.bits_per_symbol, 2)
        self.assertEqual(cfg.symbol_rate, 50000.0)
        self.assertEqual(cfg.samples_per_symbol, 20)
        self.assertEqual(cfg.num_taps, 201)

    def test_bpsk_config(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="bpsk")
        self.assertEqual(cfg.bits_per_symbol, 1)
        self.assertEqual(cfg.symbol_rate, 100000.0)
        self.assertEqual(cfg.samples_per_symbol, 10)

    def test_8psk_config(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="8psk")
        self.assertEqual(cfg.bits_per_symbol, 3)
        self.assertGreater(cfg.samples_per_symbol, 0)

    def test_duration_overrides_bit_count(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, duration_sec=1.0, bit_count=999)
        self.assertEqual(cfg.total_bits, 100000)

    def test_missing_bitrate_raises(self):
        with self.assertRaises(ValueError):
            SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6)

    def test_invalid_modulation(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="invalid")
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_missing_input_file(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, source="file")
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_negative_sample_rate(self):
        with self.assertRaises(ValueError):
            SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=-1, bitrate=1e5)

    def test_output_filename_cf32(self):
        cfg = SignalConfig(name="mysignal", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, output_format="cf32", add_timestamp=False)
        filename = cfg.get_output_filename()
        self.assertIn("mysignal", filename)
        self.assertIn("qpsk", filename)  # default modulation is qpsk
        self.assertIn(".cf32", filename)

    def test_output_filename_sigmf(self):
        cfg = SignalConfig(name="mysignal", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, output_format="sigmf", add_timestamp=False)
        self.assertTrue(cfg.get_output_filename(is_data=True).endswith(".sigmf-data"))
        self.assertTrue(cfg.get_output_filename(is_data=False).endswith(".sigmf-meta"))

    def test_yaml_loading(self):
        yaml_content = """
iq_generator:
  name: "yaml_test"
  center_frequency_hz: "2.4e9"
  sample_rate: "1e6"
  bitrate: "100000"
  modulation: "bpsk"
  filter_type: "root_raised_cosine"
  output_format: "cf32"
  source: "random"
  bit_count: "500"
  output_dir: "./test_output"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            cfg = create_config(f.name)
            os.unlink(f.name)
        self.assertEqual(cfg.name, "yaml_test")
        self.assertEqual(cfg.modulation, "bpsk")
        self.assertEqual(cfg.output_format, "cf32")


class TestIQGenerator(unittest.TestCase):
    def _make_cfg(self, modulation="qpsk", filter_type="none", output_format="cf32"):
        return SignalConfig(
            name="gen_test", center_frequency_hz=2.4e9, sample_rate=1000000,
            bitrate=100000, modulation=modulation, filter_type=filter_type,
            output_format=output_format, source="random", bit_count=1000,
            output_dir=tempfile.mkdtemp(), add_timestamp=False, gray_coding=True,
        )

    def _generate_all_modulations(self):
        for mod in ["bpsk", "qpsk", "8psk", "dbpsk", "dqpsk", "pi4_qpsk", "oqpsk", "d8psk", "pi4_8psk"]:
            cfg = self._make_cfg(modulation=mod)
            gen = IQGenerator(cfg)
            samples = gen.generate()
            self.assertGreater(len(samples), 0)
            self.assertEqual(samples.dtype, np.complex64)

    def test_all_modulations(self):
        self._generate_all_modulations()

    def test_all_filters(self):
        for filt in ["none", "root_raised_cosine", "raised_cosine", "gaussian", "rectangular"]:
            cfg = self._make_cfg(filter_type=filt)
            gen = IQGenerator(cfg)
            samples = gen.generate()
            self.assertGreater(len(samples), 0)

    def test_power_normalization(self):
        cfg = self._make_cfg()
        cfg.peak_power = 0.5
        IQGenerator(cfg).generate()
        samples = IQGenerator(cfg).generate()
        peak = np.max(np.abs(samples))
        self.assertAlmostEqual(peak, 0.5, places=5)

    def test_power_normalization_high(self):
        cfg = self._make_cfg()
        cfg.peak_power = 2.0
        samples = IQGenerator(cfg).generate()
        peak = np.max(np.abs(samples))
        self.assertAlmostEqual(peak, 2.0, places=5)

    def test_sigmf_output(self):
        cfg = self._make_cfg(output_format="sigmf")
        gen = IQGenerator(cfg)
        data_path, meta_path = gen.generate_and_write()
        self.assertTrue(os.path.exists(data_path))
        self.assertTrue(os.path.exists(meta_path))
        with open(meta_path) as f:
            meta = json.load(f)
        self.assertEqual(meta["annotations"][0]["modulation"], "qpsk")

    def test_cf32_output(self):
        cfg = self._make_cfg(output_format="cf32")
        gen = IQGenerator(cfg)
        samples = gen.generate()
        data_path, _ = gen.generate_and_write()
        self.assertTrue(os.path.exists(data_path))
        self.assertEqual(len(samples), len(samples.astype(np.complex64)))
        self.assertEqual(os.path.getsize(data_path), len(samples) * 8)

    def test_file_source(self):
        test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
        test_file.write(bytes([0b10101010, 0b11001100]))
        test_file.close()
        cfg = SignalConfig(
            name="file_test", center_frequency_hz=2.4e9, sample_rate=1e6,
            bitrate=1e5, modulation="bpsk", filter_type="none", output_format="cf32",
            source="file", input_file=test_file.name, bit_order="msb_first",
            output_dir=tempfile.mkdtemp(), add_timestamp=False,
        )
        samples = IQGenerator(cfg).generate()
        self.assertGreater(len(samples), 0)
        os.unlink(test_file.name)


class TestSigMFMetadata(unittest.TestCase):
    def _make_sigmf_cfg(self):
        return SignalConfig(
            name="meta_test", center_frequency_hz=2.4e9, sample_rate=1e6,
            bitrate=100000, modulation="qpsk", filter_type="root_raised_cosine",
            roll_off=0.35, output_format="sigmf", source="random", bit_count=100,
            output_dir=tempfile.mkdtemp(), add_timestamp=False,
        )

    def test_global_fields(self):
        cfg = self._make_sigmf_cfg()
        _, meta_path = IQGenerator(cfg).generate_and_write()
        with open(meta_path) as f:
            meta = json.load(f)
        g = meta["global"]
        for key in ["core:version", "core:sample_rate", "core:frequency", "core:datetime",
                     "core:datatype", "core:num_channels", "core:hardware",
                     "core:description", "core:author", "core:license"]:
            self.assertIn(key, g)

    def test_capture_fields(self):
        cfg = self._make_sigmf_cfg()
        _, meta_path = IQGenerator(cfg).generate_and_write()
        with open(meta_path) as f:
            meta = json.load(f)
        c = meta["captures"][0]
        for key in ["core:sample_start", "core:frequency", "core:datetime", "core:sample_rate"]:
            self.assertIn(key, c)

    def test_annotation_fields(self):
        cfg = self._make_sigmf_cfg()
        _, meta_path = IQGenerator(cfg).generate_and_write()
        with open(meta_path) as f:
            meta = json.load(f)
        ann = meta["annotations"][0]
        self.assertEqual(ann["modulation"], "qpsk")
        self.assertEqual(ann["bits_per_symbol"], 2)
        for key in ["sample_rate", "bitrate", "samples_per_symbol", "pulse_shaping", "roll_off", "description"]:
            self.assertIn(key, ann)


class TestInterconnectedParameters(unittest.TestCase):
    def test_symbol_rate_calculation(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="qpsk")
        self.assertAlmostEqual(cfg.symbol_rate, 1e5 / 2)

    def test_samples_per_symbol_calculation(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=2e6, bitrate=1e5, modulation="qpsk")
        expected_sps = 2e6 / (1e5 / 2)
        self.assertEqual(cfg.samples_per_symbol, int(round(expected_sps)))

    def test_num_taps_calculation(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="qpsk", span_symbols=10)
        self.assertEqual(cfg.num_taps, 10 * cfg.samples_per_symbol + 1)

    def test_sps_override_warning(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="qpsk", samples_per_symbol_override=999)
        self.assertNotEqual(cfg.samples_per_symbol, 999)

    def test_symbol_rate_override_warning(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="qpsk", symbol_rate_override=12345)
        self.assertNotEqual(cfg.symbol_rate, 12345)


class TestCreateFunctions(unittest.TestCase):
    def test_create_config(self):
        yaml_content = """
iq_generator:
  name: "factory_test"
  center_frequency_hz: 2400000000
  sample_rate: 1000000
  bitrate: 100000
  modulation: "bpsk"
  output_format: "cf32"
  source: "random"
  bit_count: 100
  output_dir: "./test_output"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            cfg = create_config(f.name)
            os.unlink(f.name)
        self.assertEqual(cfg.name, "factory_test")

    def test_create_data_source(self):
        self.assertIsInstance(create_data_source("random", seed=42), RandomDataSource)

    def test_create_shaper(self):
        self.assertIsInstance(create_shaper("root_raised_cosine"), PulseShaper)

    def test_create_writer(self):
        self.assertIsInstance(create_writer("cf32"), Cf32Writer)
        self.assertIsInstance(create_writer("sigmf"), SigMFWriter)

    def test_create_mapper(self):
        self.assertIsInstance(create_mapper("qpsk"), QPSKMapper)

    def test_invalid_writer_format(self):
        with self.assertRaises(ValueError):
            create_writer("invalid")

    def test_invalid_source(self):
        with self.assertRaises(ValueError):
            create_data_source("invalid")


class TestEdgeCases(unittest.TestCase):
    def test_empty_bitstream(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, modulation="bpsk", filter_type="none", output_format="cf32", source="random", bit_count=0, output_dir=tempfile.mkdtemp(), add_timestamp=False)
        samples = IQGenerator(cfg).generate()
        self.assertEqual(len(samples), 0)

    def test_non_integer_sps_rounding(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1000001, bitrate=100000, modulation="qpsk", output_dir=tempfile.mkdtemp(), add_timestamp=False)
        self.assertGreater(cfg.samples_per_symbol, 0)

    def test_missing_config_file(self):
        with self.assertRaises(FileNotFoundError):
            create_config("/nonexistent/config.yaml")

    def test_missing_iq_generator_section(self):
        yaml_content = "other_section:\n  name: test\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            with self.assertRaises(ValueError):
                create_config(f.name)
            os.unlink(f.name)

    def test_power_zero(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, peak_power=0)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_negative_bitrate(self):
        with self.assertRaises(ValueError):
            SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=-1000)

    def test_invalid_filter_type(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, filter_type="invalid")
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_invalid_bit_order(self):
        cfg = SignalConfig(name="test", center_frequency_hz=2.4e9, sample_rate=1e6, bitrate=1e5, bit_order="invalid")
        with self.assertRaises(ValueError):
            cfg.validate()


class TestIntegration(unittest.TestCase):
    def _run_full(self, modulation, filter_type, output_format):
        cfg = SignalConfig(
            name=f"integration_{modulation}", center_frequency_hz=2.4e9,
            sample_rate=1000000, bitrate=100000, modulation=modulation,
            filter_type=filter_type, output_format=output_format,
            source="random", bit_count=1000, output_dir=tempfile.mkdtemp(),
            add_timestamp=False,
        )
        return cfg, IQGenerator(cfg).generate_and_write()

    def test_all_modulations_cf32(self):
        for mod in ["bpsk", "qpsk", "8psk", "dbpsk", "dqpsk", "pi4_qpsk", "oqpsk", "d8psk", "pi4_8psk"]:
            _, paths = self._run_full(mod, "none", "cf32")
            self.assertTrue(os.path.exists(paths[0]))

    def test_all_filters_sigmf(self):
        for filt in ["none", "root_raised_cosine", "raised_cosine", "gaussian", "rectangular"]:
            _, paths = self._run_full("qpsk", filt, "sigmf")
            self.assertTrue(os.path.exists(paths[0]))
            self.assertTrue(os.path.exists(paths[1]))

    def test_file_source_sigmf(self):
        test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
        test_file.write(b"Hello world! Test data for signal generation.")
        test_file.close()
        cfg = SignalConfig(
            name="file_integration", center_frequency_hz=2.4e9, sample_rate=1e6,
            bitrate=1e5, modulation="qpsk", filter_type="root_raised_cosine",
            output_format="sigmf", source="file", input_file=test_file.name,
            bit_order="msb_first", output_dir=tempfile.mkdtemp(), add_timestamp=False,
        )
        data_path, meta_path = IQGenerator(cfg).generate_and_write()
        self.assertTrue(os.path.exists(data_path))
        self.assertTrue(os.path.exists(meta_path))
        os.unlink(test_file.name)


if __name__ == "__main__":
    unittest.main()

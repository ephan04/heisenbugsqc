"""Tests of the kit.

  pip install pytest && python -m pytest test_kit.py
"""
import numpy as np
import pytest
import stim

from circuit import (
    GROSS_CIRCUITS,
    _merge_duplicates,
    dem_matrices,
    detector_ids,
    load_circuit,
    noise_strengths,
    rescale_noise,
    sample,
)
from decoders import bposd_decoder, per_cycle_rate, score
from make_circuit import CODES, memory_experiment

# code: (qubits, logical qubits)
SIZES = {"gross": (288, 12), "bb108": (216, 8), "bb90": (180, 8), "bb72": (144, 12)}
BASES = ["X", "Z"]


@pytest.mark.parametrize("basis", BASES)
def test_shipped_circuits_match_generator(basis):
    assert stim.Circuit.from_file(GROSS_CIRCUITS[basis]) == memory_experiment("gross", basis)


@pytest.mark.parametrize("basis", BASES)
@pytest.mark.parametrize("code", list(CODES))
def test_noiseless_circuit_is_silent(code, basis):
    circuit = memory_experiment(code, basis)
    qubits, logical_qubits = SIZES[code]
    assert (circuit.num_qubits, circuit.num_observables) == (qubits, logical_qubits)
    circuit.detector_error_model()   # raises if a detector or observable is not deterministic
    det, obs = sample(circuit.without_noise(), shots=10, seed=0)
    assert not det.any() and not obs.any()


@pytest.mark.parametrize("rounds", [1, 2, 3])
def test_short_experiments_build(rounds):
    circuit = memory_experiment("bb72", "Z", rounds)
    assert circuit.num_detectors == 36 * (2 * rounds)   # 36 X checks in rounds - 1 cycles, 36 Z checks in rounds + 1
    circuit.detector_error_model()


def test_rescale_noise_equals_generating_at_that_noise():
    rescaled = load_circuit(GROSS_CIRCUITS["X"], p=0.004)
    assert noise_strengths(rescaled) == {0.004}
    assert rescaled == memory_experiment("gross", "X", p=0.004)


def test_rescale_refuses_mixed_noise():
    mixed = stim.Circuit("X_ERROR(0.1) 0\nX_ERROR(0.2) 0\nM 0")
    with pytest.raises(ValueError):
        rescale_noise(mixed, 0.01)


def test_duplicate_mechanisms_are_merged():
    dem = stim.DetectorErrorModel("error(0.1) D0 L0\nerror(0.2) D0 L0\nerror(0.3) D1")
    merged = _merge_duplicates(dem, det_rows={0: 0, 1: 1})
    assert list(merged) == [((0,), (0,)), ((1,), ())]
    assert list(merged.values()) == pytest.approx([0.26, 0.3])   # 0.1 * 0.8 + 0.2 * 0.9 = 0.26


def test_mechanisms_outside_the_kept_detectors_are_dropped():
    dem = stim.DetectorErrorModel("error(0.1) D0\nerror(0.3) D1")
    assert _merge_duplicates(dem, det_rows={1: 0}) == {((0,), ()): 0.3}


@pytest.mark.parametrize("basis", BASES)
def test_detectors_of_the_gross_circuits(basis):
    circuit = load_circuit(GROSS_CIRCUITS[basis])
    other = "Z" if basis == "X" else "X"
    assert circuit.num_detectors == 1728
    assert len(detector_ids(circuit, basis)) == 936 and len(detector_ids(circuit, other)) == 792


@pytest.mark.parametrize("basis", BASES)
def test_matrices_of_the_gross_circuits(basis):
    H, L, priors = dem_matrices(load_circuit(GROSS_CIRCUITS[basis]), basis)
    assert H.shape == (936, 8784) and L.shape == (12, 8784) and priors.shape == (8784,)
    assert priors.min() > 0 and priors.max() < 0.5
    assert H.sum(axis=1).min() > 1   # at least two mechanisms flip every detector
    assert H.sum(axis=0).min() > 1   # every mechanism flips at least two detectors


def test_bposd_decodes_low_noise_shots():
    circuit = load_circuit(GROSS_CIRCUITS["X"], p=0.001)
    H, L, priors = dem_matrices(circuit, "X")
    det, obs = sample(circuit, shots=20, seed=0)
    failed, seconds = score(bposd_decoder(H, priors).decode, L, det[:, detector_ids(circuit, "X")], obs)
    assert not failed.any() and (seconds > 0).all()


def test_per_cycle_rate():
    half_failed = np.array([True, False, True, False])
    assert per_cycle_rate(half_failed, cycles=1)[0] == pytest.approx(0.5)
    assert per_cycle_rate(half_failed, cycles=2)[0] == pytest.approx(1 - 0.5 ** 0.5)
    rate, error = per_cycle_rate(np.zeros(10, bool), cycles=12)
    assert rate == 0 and error == 0

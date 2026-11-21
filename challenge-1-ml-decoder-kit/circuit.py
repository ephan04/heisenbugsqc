"""Load a Stim memory circuit and turn it into decoder inputs."""
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import stim

CHECK_COORDINATE = {"X": 0, "Z": 1}   # detector coordinate of a check type in the kit's circuits
# The X memory and the Z memory experiment of the Gross code, by memory basis.
GROSS_CIRCUITS = {basis: str(Path(__file__).parent / "circuits" / f"gross_{basis}_r12_p0.001.stim") for basis in "XZ"}


def load_circuit(path, p=None):
    """Read a Stim circuit. If p is given, set its noise strength to p."""
    circuit = stim.Circuit.from_file(path)
    return circuit if p is None else rescale_noise(circuit, p)


def noise_strengths(circuit):
    """All distinct noise probabilities in the circuit."""
    return {arg for instruction in circuit.flattened() for arg in _noise_args(instruction)}


def _noise_args(instruction):
    """Noise probabilities of one instruction. Gates, resets and annotations have none."""
    return instruction.gate_args_copy() if stim.gate_data(instruction.name).is_noisy_gate else []


def rescale_noise(circuit, p):
    """Replace the circuit's one noise strength by p. Mixed strengths are refused."""
    if len(noise_strengths(circuit)) != 1:
        raise ValueError("rescaling needs a circuit with exactly one noise strength")
    return _replace_noise(circuit, p)


def _replace_noise(circuit, p):
    """Copy the circuit and set every noise argument to p. Repeat blocks stay repeat blocks."""
    out = stim.Circuit()
    for instruction in circuit:
        if isinstance(instruction, stim.CircuitRepeatBlock):
            out.append(stim.CircuitRepeatBlock(instruction.repeat_count, _replace_noise(instruction.body_copy(), p)))
        elif _noise_args(instruction):
            out.append(instruction.name, instruction.targets_copy(), [p] * len(_noise_args(instruction)))
        else:
            out.append(instruction)
    return out


def detector_ids(circuit, basis=None):
    """Ids of the detectors on X checks (basis "X") or on Z checks (basis "Z"). None gives all.

    The kit's circuits mark X-check detectors with coordinate 0 and Z-check detectors with 1.
    """
    if basis is None:
        return np.arange(circuit.num_detectors)
    coordinates = circuit.get_detector_coordinates()
    wanted = [CHECK_COORDINATE[basis]]
    return np.array([d for d in range(circuit.num_detectors) if coordinates[d] == wanted])


def dem_matrices(circuit, basis=None):
    """Detector error model as H (detectors x mechanisms), L (observables x mechanisms), priors.

    Column k is one error mechanism. H[:, k] marks the detectors it flips, L[:, k] the
    observables it flips, and priors[k] is its probability. A decoder solves H e = syndrome.
    With basis "X" or "Z" only the detectors on checks of that type are kept, in the order
    of detector_ids(circuit, basis). The X memory circuit is decoded with basis "X".
    """
    det_ids = detector_ids(circuit, basis)
    # flattened() expands repeat blocks.
    dem = circuit.detector_error_model().flattened()
    errors = _merge_duplicates(dem, _row_numbers(det_ids))
    if not errors:
        raise ValueError("no error mechanism flips these detectors, so there is nothing to decode")
    detectors, observables = zip(*errors, strict=True)
    H = _incidence_matrix(detectors, len(det_ids))
    L = _incidence_matrix(observables, circuit.num_observables)
    return H, L.tocsr(), np.array(list(errors.values()))


def _row_numbers(det_ids):
    """{detector id: its row in H} for the kept detectors."""
    return {int(kept): row for row, kept in enumerate(det_ids)}


def _merge_duplicates(dem, det_rows):
    """{(detector rows, observables): probability}, one entry per distinct effect.

    Mechanisms with the same effect are merged. Mechanisms that flip no kept detector and
    no observable are dropped.
    """
    merged = {}
    for instruction in dem:
        if instruction.type != "error":
            continue
        effect, p = _effect(instruction, det_rows), instruction.args_copy()[0]
        if effect != ((), ()):
            merged[effect] = _exactly_one_fires(p, merged.get(effect, 0.0))
    return merged


def _effect(error, det_rows):
    """(kept detector rows, observables) that one error instruction flips."""
    targets = error.targets_copy()
    detectors = sorted(det_rows[t.val] for t in targets if t.is_relative_detector_id() and t.val in det_rows)
    observables = sorted(t.val for t in targets if t.is_logical_observable_id())
    return tuple(detectors), tuple(observables)


def _exactly_one_fires(p, q):
    """Probability that exactly one of two independent mechanisms fires."""
    return p * (1 - q) + q * (1 - p)


def _incidence_matrix(id_lists, n_rows):
    """Sparse 0/1 matrix (CSC). Row = detector or observable id, column = error mechanism."""
    rows = [i for ids in id_lists for i in ids]
    cols = [col for col, ids in enumerate(id_lists) for _ in ids]
    return sp.csc_matrix((np.ones(len(rows), np.uint8), (rows, cols)), shape=(n_rows, len(id_lists)))


def sample(circuit, shots, seed):
    """Detector flips and true observable flips as uint8 arrays, one row per shot."""
    sampler = circuit.compile_detector_sampler(seed=seed)
    det, obs = sampler.sample(shots, separate_observables=True)
    return det.astype(np.uint8), obs.astype(np.uint8)

"""Build the X or Z memory experiment of the Gross code.

  python make_circuit.py --code gross --basis X --out circuits/gross_X_r12_p0.001.stim

The syndrome cycle follows Bravyi et al., "High-threshold and low-overhead fault-tolerant
quantum memory", Nature 627, 778 (2024), and the authors' code at
https://github.com/sbravyi/BivariateBicycleCodes (Apache 2.0).
The experiment follows the relay-BP paper (arXiv:2506.01779) and its circuits at
https://github.com/trmue/relay.

Qubit order, as in the code of Bravyi et al.: X checks, left data, right data, Z checks.
Each of the four blocks has n2 = ell * m qubits.
"""
import argparse
from dataclasses import dataclass

import numpy as np
import stim

from circuit import CHECK_COORDINATE

# name: (ell, m, a, b, rounds).  A = x^a1 + y^a2 + y^a3,  B = y^b1 + x^b2 + x^b3
CODES = {
    "gross": (12, 6, (3, 1, 2), (3, 1, 2), 12),   # [[144,12,12]]
    "bb108": (9, 6, (3, 1, 2), (3, 1, 2), 10),    # [[108,8,10]]
    "bb90": (15, 3, (9, 1, 2), (0, 2, 7), 10),    # [[90,8,10]]
    "bb72": (6, 6, (3, 1, 2), (3, 1, 2), 6),      # [[72,12,6]]
}
# The neighbour each check meets in CX layers 0 to 6 (the paper's schedule).
# Neighbours 0-2 are A1, A2, A3 and 3-5 are B1, B2, B3.
IDLE = "idle"
S_X = [IDLE, 1, 4, 3, 5, 0, 2]
S_Z = [3, 5, 0, 1, 2, 4, IDLE]
RESET = {"X": "RX", "Z": "R"}
MEASURE = {"X": "MX", "Z": "M"}
FLIP = {"X": "Z_ERROR", "Z": "X_ERROR"}   # the error that flips a state of this basis


# ---------- the code ----------

def cyclic_shift(size, shift):
    """Permutation matrix of a cyclic shift."""
    return np.roll(np.eye(size, dtype=np.uint8), shift, axis=1)


def x_power(ell, m, power):
    """The matrix of x^power on the ell x m torus."""
    return np.kron(cyclic_shift(ell, power), np.eye(m, dtype=np.uint8))


def y_power(ell, m, power):
    """The matrix of y^power on the ell x m torus."""
    return np.kron(np.eye(ell, dtype=np.uint8), cyclic_shift(m, power))


def shift_matrices(ell, m, a, b):
    """The permutation matrices [A1, A2, A3] and [B1, B2, B3]."""
    As = [x_power(ell, m, a[0]), y_power(ell, m, a[1]), y_power(ell, m, a[2])]
    Bs = [y_power(ell, m, b[0]), x_power(ell, m, b[1]), x_power(ell, m, b[2])]
    return As, Bs


def check_matrices(As, Bs):
    """hx = [A | B] and hz = [B^T | A^T]. Columns are left data, then right data."""
    A, B = sum(As) % 2, sum(Bs) % 2
    return np.hstack([A, B]), np.hstack([B.T, A.T])


def neighbours(As, Bs):
    """(x_neighbours, z_neighbours). Entry [d][i] is the qubit that is neighbour d (0 to 5) of check i."""
    n2 = len(As[0])
    # argmax finds the single 1 in each row (axis 1) or column (axis 0) of a permutation matrix.
    x_neighbours = [n2 + M.argmax(axis=1) for M in As] + [2 * n2 + M.argmax(axis=1) for M in Bs]
    z_neighbours = [n2 + M.argmax(axis=0) for M in Bs] + [2 * n2 + M.argmax(axis=0) for M in As]
    return x_neighbours, z_neighbours


@dataclass(frozen=True)
class Layout:
    """One code: its check matrices and the neighbours of every check."""
    hx: np.ndarray        # X checks x data qubits
    hz: np.ndarray        # Z checks x data qubits
    x_neighbours: list    # x_neighbours[d][i]: the qubit that is neighbour d (0 to 5) of X check i
    z_neighbours: list    # the same for the Z checks

    @property
    def n2(self):
        """Number of checks of one type. The code has 2 * n2 data qubits."""
        return len(self.hx)

    @property
    def x_checks(self):
        """Qubit indices of the X checks."""
        return range(self.n2)

    @property
    def data(self):
        """Qubit indices of the data qubits: the left block, then the right block."""
        return range(self.n2, 3 * self.n2)

    @property
    def z_checks(self):
        """Qubit indices of the Z checks."""
        return range(3 * self.n2, 4 * self.n2)

    def checks(self, basis):
        """The check matrix of one Pauli type."""
        return self.hx if basis == "X" else self.hz


def code_layout(name):
    """The layout of one code of CODES."""
    ell, m, a, b, _ = CODES[name]
    As, Bs = shift_matrices(ell, m, a, b)
    return Layout(*check_matrices(As, Bs), *neighbours(As, Bs))


# ---------- linear algebra over GF(2) ----------

def gf2_row_reduce(M):
    """Row-reduce over GF(2). Returns the nonzero reduced rows and their pivot columns."""
    M, pivots = M.copy() % 2, []
    for col in range(M.shape[1]):
        row = len(pivots)
        hits = np.nonzero(M[row:, col])[0]
        if row == len(M) or len(hits) == 0:
            continue
        M[[row, row + hits[0]]] = M[[row + hits[0], row]]   # move a pivot into place
        others = np.nonzero(M[:, col])[0]
        M[others[others != row]] ^= M[row]                  # clear the rest of the column
        pivots.append(col)
    return M[: len(pivots)], pivots


def gf2_rank(M):
    """Rank over GF(2)."""
    return len(gf2_row_reduce(M)[1])


def gf2_kernel(M):
    """Basis of the vectors v with M v = 0 over GF(2)."""
    reduced, pivots = gf2_row_reduce(M)
    free = [col for col in range(M.shape[1]) if col not in pivots]
    basis = np.zeros((len(free), M.shape[1]), dtype=np.uint8)
    for k, col in enumerate(free):
        basis[k, col] = 1
        basis[k, pivots] = reduced[:, col]
    return basis


def logical_operators(h_same, h_other):
    """Logical operators of one Pauli type: they commute with h_other and are independent of h_same."""
    stack, rank, chosen = h_same, gf2_rank(h_same), []
    for candidate in gf2_kernel(h_other):
        trial = np.vstack([stack, candidate])
        if gf2_rank(trial) > rank:
            stack, rank = trial, rank + 1
            chosen.append(candidate)
    return np.array(chosen)


# ---------- the circuit ----------

def append_preparation(circuit, qubits, basis, p):
    """Reset qubits in a basis. A faulty reset flips the state."""
    circuit.append(RESET[basis], qubits)
    circuit.append(FLIP[basis], qubits, p)


def append_measurement(circuit, qubits, basis, p):
    """Measure qubits in a basis. A faulty measurement flips the outcome."""
    circuit.append(FLIP[basis], qubits, p)
    circuit.append(MEASURE[basis], qubits)


def x_check_gates(layout, layer):
    """Flat (control, target) list: every X check controls its neighbour of this layer."""
    if S_X[layer] == IDLE:
        return []
    partners = layout.x_neighbours[S_X[layer]]
    return [int(q) for check, partner in zip(layout.x_checks, partners, strict=True) for q in (check, partner)]


def z_check_gates(layout, layer):
    """Flat (control, target) list: every Z check is the target of its neighbour of this layer."""
    if S_Z[layer] == IDLE:
        return []
    partners = layout.z_neighbours[S_Z[layer]]
    return [int(q) for check, partner in zip(layout.z_checks, partners, strict=True) for q in (partner, check)]


def cx_gates(layout, layer):
    """Flat (control, target) list of all CX gates of one layer."""
    return x_check_gates(layout, layer) + z_check_gates(layout, layer)


def idle_data(layout, layer):
    """The data qubits without a gate in this CX layer."""
    return sorted(set(layout.data) - set(cx_gates(layout, layer)))


def append_cx_layer(circuit, layout, layer, p, idle_noise=True):
    """Append one CX layer: the gates, their noise, noise on idle data qubits, and a TICK."""
    gates, idle = cx_gates(layout, layer), idle_data(layout, layer)
    circuit.append("CX", gates)
    circuit.append("DEPOLARIZE2", gates, p)
    if idle and idle_noise:
        circuit.append("DEPOLARIZE1", idle, p)
    circuit.append("TICK")


def syndrome_cycle(layout, p, first=False):
    """One syndrome cycle: 7 CX layers and a measure/reset layer, each closed by a TICK.

    The cycle records the Z-check outcomes (layer 6) and then the X-check outcomes (layer 7).
    Layer 7 prepares the Z checks for the next cycle. In the first cycle the data qubits
    get no idle noise in layer 0.
    """
    circuit = stim.Circuit()
    append_preparation(circuit, layout.x_checks, "X", p)
    append_cx_layer(circuit, layout, 0, p, idle_noise=not first)
    for layer in range(1, 6):
        append_cx_layer(circuit, layout, layer, p)
    append_measurement(circuit, layout.z_checks, "Z", p)
    append_cx_layer(circuit, layout, 6, p)
    circuit.append("DEPOLARIZE1", layout.data, p)   # layer 7: data qubits idle
    append_measurement(circuit, layout.x_checks, "X", p)
    append_preparation(circuit, layout.z_checks, "Z", p)
    circuit.append("TICK")
    return circuit


def last_syndrome_cycle(layout, p, first=False):
    """The last cycle. It records the Z checks and then the X checks, like every cycle.

    Both check types are measured after layer 6, and the data readout follows at once.
    The idle noise is placed as in the relay-BP authors' circuits: the Z checks and the
    data qubits that idle in layer 6 get it before layer 5.
    """
    circuit = stim.Circuit()
    append_preparation(circuit, layout.x_checks, "X", p)
    append_cx_layer(circuit, layout, 0, p, idle_noise=not first)
    for layer in range(1, 5):
        append_cx_layer(circuit, layout, layer, p)
    circuit.append("DEPOLARIZE1", [*layout.z_checks, *idle_data(layout, 6)], p)
    append_cx_layer(circuit, layout, 5, p)
    append_cx_layer(circuit, layout, 6, p, idle_noise=False)
    append_measurement(circuit, layout.z_checks, "Z", p)
    append_measurement(circuit, layout.x_checks, "X", p)
    circuit.append("TICK")
    return circuit


def initial_preparation(layout, basis, p):
    """Prepare the data qubits in the memory basis and the Z-check qubits, with noise."""
    circuit = stim.Circuit()
    append_preparation(circuit, layout.data, basis, p)
    append_preparation(circuit, layout.z_checks, "Z", p)
    circuit.append("TICK")
    return circuit


def cycle_detectors(layout, basis, first=False):
    """Compare every check with its value one cycle earlier.

    The detector coordinate is 0 for an X check and 1 for a Z check. In the first cycle
    only the checks of the memory basis have a known value, and it is 0.
    """
    circuit, n2 = stim.Circuit(), layout.n2
    for record in range(-2 * n2, 0):
        check_basis = "Z" if record < -n2 else "X"   # a cycle records the Z checks first
        if first and check_basis != basis:
            continue
        earlier = [] if first else [stim.target_rec(record - 2 * n2)]
        circuit.append("DETECTOR", [stim.target_rec(record), *earlier], [CHECK_COORDINATE[check_basis]])
    return circuit


def noisy_cycles(layout, basis, rounds, p):
    """All noisy syndrome cycles with their detectors."""
    first, later = cycle_detectors(layout, basis, first=True), cycle_detectors(layout, basis)
    if rounds == 1:
        return last_syndrome_cycle(layout, p, first=True) + first
    circuit = syndrome_cycle(layout, p, first=True) + first
    circuit += (syndrome_cycle(layout, p) + later) * (rounds - 2)
    return circuit + last_syndrome_cycle(layout, p) + later


def data_records(support):
    """Measurement records of the data qubits in a 0/1 support vector, right after the data readout."""
    return [stim.target_rec(int(qubit) - len(support)) for qubit in np.nonzero(support)[0]]


def final_detectors(layout, basis):
    """Compare every check of the memory basis with the data readout."""
    circuit, n2 = stim.Circuit(), layout.n2
    # Before the data readout, the last cycle recorded the Z checks and then the X checks.
    last_value = -3 * n2 if basis == "X" else -4 * n2
    for check, support in enumerate(layout.checks(basis)):
        targets = [*data_records(support), stim.target_rec(last_value + check)]
        circuit.append("DETECTOR", targets, [CHECK_COORDINATE[basis]])
    return circuit


def logical_observables(layout, basis):
    """The logical operators of the memory basis, read from the data readout."""
    other = "Z" if basis == "X" else "X"
    circuit = stim.Circuit()
    for index, support in enumerate(logical_operators(layout.checks(basis), layout.checks(other))):
        circuit.append("OBSERVABLE_INCLUDE", data_records(support), index)
    return circuit


def data_readout(layout, basis):
    """Measure all data qubits in the memory basis, without noise, and evaluate the result."""
    circuit = stim.Circuit()
    circuit.append(MEASURE[basis], layout.data)
    return circuit + final_detectors(layout, basis) + logical_observables(layout, basis)


def memory_experiment(code="gross", basis="X", rounds=None, p=0.001):
    """The X or Z memory experiment of the relay-BP paper for one code of CODES.

    The data qubits are prepared in the memory basis with noise. `rounds` noisy syndrome
    cycles follow. A noiseless measurement of all data qubits ends the experiment.
    The observables are the logical operators of the memory basis.
    """
    rounds = CODES[code][-1] if rounds is None else rounds
    if rounds < 1:
        raise ValueError("the experiment needs at least one round")
    layout = code_layout(code)
    return initial_preparation(layout, basis, p) + noisy_cycles(layout, basis, rounds, p) + data_readout(layout, basis)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--code", choices=list(CODES), default="gross")
    parser.add_argument("--basis", choices=["X", "Z"], default="X", help="memory basis")
    parser.add_argument("--rounds", type=int, default=None, help="noisy cycles, default: the code distance")
    parser.add_argument("--p", type=float, default=0.001)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    circuit = memory_experiment(args.code, args.basis, args.rounds, args.p)
    circuit.to_file(args.out)
    print(args.out, f"{circuit.num_qubits} qubits, {circuit.num_detectors} detectors, "
                    f"{circuit.num_observables} observables")


if __name__ == "__main__":
    main()

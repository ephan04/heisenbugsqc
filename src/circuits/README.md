# Gross code circuits

`gross_X_r12_p0.001.stim` and `gross_Z_r12_p0.001.stim` are the X and Z memory experiments
of the [[144,12,12]] Gross code: the bivariate bicycle code with A = x^3 + y + y^2 and
B = y^3 + x + x^2 on a 12 x 6 torus.

`load_circuit(path, p)` in `circuit.py` sets the noise strength.
`make_circuit.py` regenerates the files.

## Schedule

The syndrome cycle of Bravyi et al., Nature 627, 778 (2024).

- 288 qubits: 72 X checks, 72 left data, 72 right data, 72 Z checks.
- A cycle has 8 layers. Layers 0 to 6 are CX layers. Each check meets its six data
  neighbours in the order `sX = [idle, 1, 4, 3, 5, 0, 2]` for X checks and
  `sZ = [3, 5, 0, 1, 2, 4, idle]` for Z checks. Neighbours 0-2 are A1, A2, A3 and 3-5 are
  B1, B2, B3.
- X checks are prepared in layer 0 and measured in layer 7. Z checks are measured in layer 6
  and prepared in layer 7.
- A `TICK` closes every layer.

## Experiment

The memory experiment of the relay-BP paper (arXiv:2506.01779). X memory:

1. All data qubits are prepared in |+>, with noise.
2. 12 noisy syndrome cycles follow.
3. All data qubits are measured in the X basis, without noise.

The 12 observables are the X logical operators. Z memory uses |0>, Z measurements and the
Z logical operators.

- **Detectors.** A detector compares a check with its value one cycle earlier. Coordinate 0
  marks an X check and 1 a Z check. Each circuit has 1728 detectors.
- **Memory basis.** X memory has 936 detectors on X checks (13 x 72) and 792 on Z checks
  (11 x 72).
- **Decoding.** The baselines decode X memory from the 936 X-check detectors.
  `detector_ids(circuit, basis)` in `circuit.py` gives their columns.

## Noise

One strength p for every operation: two-qubit depolarizing noise after each CX, a flip
after each preparation and before each check measurement, and single-qubit depolarizing
noise on idle data qubits (layers 0, 6 and 7).

As in the relay-BP authors' circuits:

- Data qubits do not idle in layer 0 of the first cycle.
- In the last cycle both check types are measured after layer 6. The Z checks and the data
  qubits that idle in layer 6 get their idle noise before layer 5.

## Provenance

- `make_circuit.py` generates the files.
- The syndrome cycle is that of https://github.com/sbravyi/BivariateBicycleCodes (Apache 2.0).
- The error model equals that of `bicycle_bivariate_144_12_12_memory_X` and `memory_Z` at
  https://github.com/trmue/relay (`tests/testdata`): the same detectors, the same 67,824 and
  67,752 error mechanisms with equal probabilities, and the same logical operators. The
  qubit numbering differs.
- The decoding matrix of each memory basis has 936 rows and 8784 columns.

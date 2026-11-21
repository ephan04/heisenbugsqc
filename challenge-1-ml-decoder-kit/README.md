# Midwest Quantum Hackathon Infleqtion: ML-assisted decoding of the [[144,12,12]] Gross code

| file | what it does |
|------|--------------|
| `circuits/` | the X and Z memory circuits of the Gross code and their schedule |
| `baseline.py` | step 1: run BP-OSD and relay-BP |
| `make_dataset.py` | step 2: save training and test data |
| `circuit.py`, `decoders.py` | the functions behind the two steps |
| `make_circuit.py` | generate the circuits, other codes and round counts |
| `test_kit.py` | tests |

## Setup

Tested with Python 3.12.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`relay-bp` builds from source and needs a Rust toolchain (https://rustup.rs). Without Rust,
remove its line from `requirements.txt`. `baseline.py` then skips relay-BP.

## The experiment

The kit follows the relay-BP paper (arXiv:2506.01779), which decodes the syndrome circuit
of the Gross code paper (Bravyi et al., Nature 627, 778). `circuits/README.md` has the
details.

- **X memory.** The data qubits start in |+>. 12 noisy syndrome cycles follow, and a
  noiseless X measurement of the data qubits ends the experiment. The 12 observables are
  the X logical operators.
- **Z memory.** The same with |0>, Z measurements and the Z logical operators.
- **Decoding.** A shot of X memory gives 1728 detector bits. The baselines decode the 936
  bits on X checks. This problem has 8784 error mechanisms. Z memory is decoded from its
  936 bits on Z checks.
- **Failure.** A shot fails when the decoder predicts any logical operator wrong. Shot k of
  X memory is paired with shot k of Z memory, and the pair fails when either fails.
- **Rate.** With failure fraction P over the pairs, the logical error rate per cycle is
  1 - (1 - P)^(1/12).

## Step 1: reproduce the baselines

```bash
python baseline.py --p 0.004 --shots 10000
```

```
10000 shots at p=0.004, 12 cycles, failures listed as [X Z]
bposd      failures [253 269] of 10000  per cycle 4.37e-03 +- 1.9e-04  mean 326.2 ms  p99 1165 ms
relay-bp   failures [45 60] of 10000  per cycle 8.71e-04 +- 8.5e-05  mean 378.7 ms  p99 5954 ms
```

Run it at p = 0.003, 0.004 and 0.005. The shots are spread over worker processes
(`--workers`, default: half the cores). The time covers one X shot and one Z shot.

The circuits and the decoder settings are those of the relay-BP authors' published results
(https://github.com/trmue/relay, `examples/data`). The settings are at the top of
`decoders.py`. Reference results with 10,000 shots per basis, next to the authors' counts:

| p | decoder | failures X, Z | rate per cycle | authors' failures X, Z (shots) | authors' rate | mean time | run time, 8 cores |
|---|---------|---------------|----------------|--------------------------------|---------------|-----------|-------------------|
| 0.003 | BP-OSD | 26, 30 | 4.7e-4 +- 0.6e-4 | 282, 316 (100,000) | 5.0e-4 | 0.14 s | 6 min |
| 0.003 | relay-BP | 3, 2 | 4.2e-5 +- 1.9e-5 | 32, 40 (100,000) | 6.0e-5 | 0.10 s | |
| 0.004 | BP-OSD | 253, 269 | 4.4e-3 +- 0.2e-3 | 244, 265 (10,000) | 4.3e-3 | 0.33 s | 17 min |
| 0.004 | relay-BP | 45, 60 | 8.7e-4 +- 0.9e-4 | 53, 44 (10,000) | 8.1e-4 | 0.38 s | |
| 0.005 | BP-OSD | 1302, 1286 | 2.3e-2 +- 0.05e-2 | 660, 651 (5,000) | 2.3e-2 | 0.59 s | 58 min |
| 0.005 | relay-BP | 411, 414 | 6.9e-3 +- 0.2e-3 | 216, 205 (5,000) | 7.1e-3 | 1.7 s | |

- Your counts will differ from ours within the statistical error.
- Relay-BP at p = 0.003 fails on a handful of shots in 10,000. Our run with 100,000 shots
  per basis gave 43 and 54 failures, a rate of 8.0e-5 +- 0.8e-5.

## Step 2: make training and test data

```bash
python make_dataset.py --basis X --p 0.004 --shots 20000 --seed 1 --out train_X.npz
python make_dataset.py --basis X --p 0.004 --shots 10000 --seed 2 --out test_X.npz
```

Each file holds `detectors` (1728 bits per shot) and `observables` (the label, 12 bits per
shot). `basis_detectors` lists the 936 columns that the baselines decode. Your decoder may
use all 1728. Use different seeds for training and test data.

## Scoring your own decoder

`decoders.score(decode, L, det, obs)` scores any function that maps one syndrome to an error
vector over the columns of `H`. `dem_matrices(circuit, "X")` gives `H`, `L` and the priors
of X memory, and `baseline.py` shows the full loop over both experiments. If your model
predicts the observable bits directly, compare them with `observables`.

Compare decoders on the same shots. Quote the rate per cycle with `decoders.per_cycle_rate`.

`dem_matrices(circuit)` gives the problem with all 1728 detectors and about 68,000 error
mechanisms. It keeps the correlations between X and Z errors.

## Rules of thumb

- **Noise.** Work at p = 0.003, 0.004 and 0.005.
- **Shots.** 10,000 shots per basis are enough at p = 0.004 and 0.005. Relay-BP fails on
  one pair in 12 at p = 0.005, one in 100 at p = 0.004 and one in 1000 at p = 0.003.
- **Slow shots.** At p = 0.004 a typical pair takes 0.1 s with relay-BP and 0.3 s with
  BP-OSD. One pair in 100 takes more than 1 s with BP-OSD and more than 5 s with relay-BP.

## Other circuits

```bash
python make_circuit.py --code bb72 --basis X --out bb72_X.stim
python make_circuit.py --code bb72 --basis Z --out bb72_Z.stim
python baseline.py --circuits bb72_X.stim bb72_Z.stim --cycles 6 --p 0.004
```

`make_circuit.py` builds the same experiment for the other codes of the Gross code paper
(`bb72`, `bb90`, `bb108`) and for any number of rounds. Pass the number of noisy cycles to
`baseline.py` with `--cycles`.

The scripts expect the kit's convention: detector coordinate 0 for X checks and 1 for
Z checks.

## Tests

```bash
pip install pytest && python -m pytest test_kit.py
```

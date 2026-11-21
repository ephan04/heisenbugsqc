"""Step 1: run the baseline decoders and report logical error rate and decode time.

  python baseline.py --p 0.004 --shots 10000

The X memory and the Z memory experiment are sampled and decoded separately, as in the
relay-BP paper. Shot k of one is paired with shot k of the other. The pair fails when either
fails. The logical error rate is quoted per syndrome cycle.
The shots are spread over worker processes.
"""
import argparse
import os
from multiprocessing import Pool
from typing import NamedTuple

import numpy as np
import scipy.sparse as sp

from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample
from decoders import bposd_decoder, print_score, relay_decoder, score

BASELINES = {"bposd": bposd_decoder, "relay-bp": relay_decoder}


class Experiment(NamedTuple):
    """One memory experiment as a decoding problem, with sampled shots."""
    H: sp.csc_matrix      # detectors x error mechanisms
    L: sp.csr_matrix      # observables x error mechanisms
    priors: np.ndarray    # probability of every mechanism
    det: np.ndarray       # detector flips, one row per shot
    obs: np.ndarray       # observable flips, one row per shot


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--circuits", nargs=2, default=[GROSS_CIRCUITS["X"], GROSS_CIRCUITS["Z"]],
                        metavar=("X_CIRCUIT", "Z_CIRCUIT"), help="the X memory and the Z memory circuit")
    parser.add_argument("--cycles", type=int, default=12, help="noisy syndrome cycles in the circuit")
    parser.add_argument("--p", type=float, default=0.004, help="physical noise strength")
    parser.add_argument("--shots", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--workers", type=int, default=max(1, os.cpu_count() // 2))
    return parser.parse_args()


def memory_experiments(paths, p, shots, seed):
    """The X memory and the Z memory experiment, each with its own shots.

    A decoder of the X memory experiment sees the detectors on X checks only.
    """
    experiments = []
    for k, (basis, path) in enumerate(zip("XZ", paths, strict=True)):
        circuit = load_circuit(path, p)
        det, obs = sample(circuit, shots, seed + k)
        experiments.append(Experiment(*dem_matrices(circuit, basis), det[:, detector_ids(circuit, basis)], obs))
    return experiments


def every_nth_shot(experiment, first, step):
    """The experiment with shots first, first + step, first + 2 * step and so on."""
    return experiment._replace(det=experiment.det[first::step], obs=experiment.obs[first::step])


def split_shots(experiments, pieces):
    """Deal the shots of both experiments into `pieces` slices, one per worker."""
    return [[every_nth_shot(experiment, k, pieces) for experiment in experiments] for k in range(pieces)]


def score_experiment(name, experiment):
    """(failed, seconds) of one baseline on the shots of one experiment."""
    decoder = BASELINES[name](experiment.H, experiment.priors)
    return score(decoder.decode, experiment.L, experiment.det, experiment.obs)


def score_slice(job):
    """Decode both experiments of one slice. Returns failed and seconds, one column per experiment."""
    name, experiments = job
    results = [score_experiment(name, experiment) for experiment in experiments]
    failed, seconds = zip(*results, strict=True)
    return np.column_stack(failed), np.column_stack(seconds)


def print_baseline(name, slices, pool, cycles):
    """Score one baseline. It is skipped when its package is missing."""
    try:
        results = pool.map(score_slice, [(name, experiments) for experiments in slices])
    except ImportError:
        print(f"{name:10s} not installed, skipped")
        return
    failed, seconds = zip(*results, strict=True)
    print_score(name, np.concatenate(failed), np.concatenate(seconds), cycles)


def main():
    args = parse_args()
    slices = split_shots(memory_experiments(args.circuits, args.p, args.shots, args.seed), args.workers)
    print(f"{args.shots} shots at p={args.p}, {args.cycles} cycles, failures listed as [X Z]")
    with Pool(args.workers) as pool:
        for name in BASELINES:
            print_baseline(name, slices, pool, args.cycles)


if __name__ == "__main__":
    main()

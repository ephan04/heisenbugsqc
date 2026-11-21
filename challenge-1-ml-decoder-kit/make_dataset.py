"""Step 2: save a labelled dataset for training or testing a learned decoder.

  python make_dataset.py --basis X --p 0.004 --shots 20000 --seed 1 --out train_X.npz
  python make_dataset.py --basis X --p 0.004 --shots 10000 --seed 2 --out test_X.npz

Arrays in the file:
  detectors        all detector bits, one row per shot
  observables      the label, one row per shot: which logical operators the errors flipped
  basis_detectors  columns of `detectors` on checks of the memory basis, the input of the baselines
"""
import argparse

import numpy as np

from circuit import GROSS_CIRCUITS, detector_ids, load_circuit, sample


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--basis", choices=["X", "Z"], default="X", help="memory basis")
    parser.add_argument("--circuit", help="default: the Gross code circuit of this basis")
    parser.add_argument("--p", type=float, default=0.004, help="physical noise strength")
    parser.add_argument("--shots", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=1, help="use different seeds for train and test")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    circuit = load_circuit(args.circuit or GROSS_CIRCUITS[args.basis], args.p)
    det, obs = sample(circuit, args.shots, args.seed)
    np.savez_compressed(args.out, p=args.p, seed=args.seed, basis=args.basis, detectors=det, observables=obs,
                        basis_detectors=detector_ids(circuit, args.basis))
    print(args.out, f"detectors {det.shape}, observables {obs.shape}")


if __name__ == "__main__":
    main()

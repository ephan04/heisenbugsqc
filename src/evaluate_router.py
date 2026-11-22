"""Run the routed decoder live on fresh shots, next to relay-BP and BP-OSD, for X and Z memory.
Prints results in the same format as baseline.py.

  python evaluate_router.py --p 0.004 --shots 1000 --t 0.7 \
      --models route_X_p0.004_safe_logistic.joblib route_Z_p0.004_safe_logistic.joblib
"""
import argparse

import joblib
import numpy as np

from circuit import GROSS_CIRCUITS, dem_matrices, detector_ids, load_circuit, sample
from decoders import bposd_decoder, print_score, relay_decoder, score
from fast_bp import fast_decoder, features


class RoutedDecoder:
    """Fast BP -> (if not converged) ML router -> BP-OSD or relay-BP."""

    def __init__(self, H, priors, model, threshold):
        self.bp = fast_decoder(H, priors)
        self.relay = relay_decoder(H, priors)
        self.bposd = bposd_decoder(H, priors)
        self.model, self.threshold = model, threshold
        self.counts = {"bp": 0, "relay": 0, "bposd": 0}

    def decode(self, syndrome):
        error = self.bp.decode(syndrome)
        if self.bp.converge:                                  # stage 1: BP solved it
            self.counts["bp"] += 1
            return error
        clues = features(syndrome, self.bp, error)            # stage 2: ask the router
        if self.model.predict_proba([clues])[0, 1] >= self.threshold:
            self.counts["bposd"] += 1
            return self.bposd.decode(syndrome)
        self.counts["relay"] += 1
        return self.relay.decode(syndrome)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=float, default=0.004)
    parser.add_argument("--shots", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=1000, help="different from the training seeds")
    parser.add_argument("--t", type=float, default=0.7, help="router threshold")
    parser.add_argument("--models", nargs=2, required=True, metavar=("X_MODEL", "Z_MODEL"))
    args = parser.parse_args()

    results = {"relay-bp": [], "bposd": [], "router": []}
    for k, (basis, model_path) in enumerate(zip("XZ", args.models)):
        circuit = load_circuit(GROSS_CIRCUITS[basis], args.p)
        H, L, priors = dem_matrices(circuit, basis)
        det, obs = sample(circuit, args.shots, args.seed + k)
        det = det[:, detector_ids(circuit, basis)]

        routed = RoutedDecoder(H, priors, joblib.load(model_path), args.t)
        decoders = {"relay-bp": relay_decoder(H, priors), "bposd": bposd_decoder(H, priors), "router": routed}
        for name, decoder in decoders.items():
            print(f"[{basis}] decoding {args.shots} shots with {name} ...", flush=True)
            results[name].append(score(decoder.decode, L, det, obs))
        print(f"[{basis}] router sent shots to: {routed.counts}")

    print(f"\n{args.shots} shots at p={args.p}, 12 cycles, router t={args.t}, failures listed as [X Z]")
    for name, per_basis in results.items():
        failed = np.column_stack([f for f, _ in per_basis])
        seconds = np.column_stack([s for _, s in per_basis])
        print_score(name, failed, seconds, cycles=12)


if __name__ == "__main__":
    main()

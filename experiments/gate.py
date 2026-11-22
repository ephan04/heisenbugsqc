"""The agreement gate as a real decoder, with settings chosen per noise level.

    gate = AgreementGate(H, L, priors, K=10, referee="R2")
    error = gate.decode(syndrome)          # same interface as the kit's decoders

Path per shot: seed 0 (fast Relay-BP, at most K restarts) -> accept if solved in the deterministic
first leg; referee if no solution; otherwise seed 1 and accept when both give the same logical
answer, else referee. No learned components: the noise level picks K and the referee from a table.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
from decoders import relay_decoder  # noqa: E402

FIRST_LEG = 80
REFEREES = {"R5": dict(), "R2": dict(stop_nconv=2), "R1": dict(stop_nconv=1, num_sets=300)}
PATHS = ["first_leg", "agreed", "no_solution", "disagreed"]


class AgreementGate:
    def __init__(self, H, L, priors, K=50, referee="R5"):
        self.L = L
        self.fast = [relay_decoder(H, priors, stop_nconv=1, num_sets=K, seed=s) for s in (0, 1)]
        self.referee = relay_decoder(H, priors, **REFEREES[referee])
        self.last_path = None

    def _logical(self, error):
        return (self.L @ np.asarray(error, np.uint8)) % 2

    def decode(self, syndrome):
        r0 = self.fast[0].decode_detailed(syndrome)
        if not r0.success:
            self.last_path = "no_solution"
            return self.referee.decode(syndrome)
        if r0.iterations <= FIRST_LEG:
            self.last_path = "first_leg"
            return r0.decoding
        r1 = self.fast[1].decode_detailed(syndrome)
        if r1.success and np.array_equal(self._logical(r0.decoding), self._logical(r1.decoding)):
            self.last_path = "agreed"
            return r0.decoding
        self.last_path = "disagreed"
        return self.referee.decode(syndrome)


def settings_for(p, table="results/adaptive_selected.json"):
    """Frozen settings for the nearest tabulated noise level."""
    selected = json.loads(Path(table).read_text())
    nearest = min(selected, key=lambda q: abs(float(q) - p))
    return selected[nearest]["K"], selected[nearest]["referee"]

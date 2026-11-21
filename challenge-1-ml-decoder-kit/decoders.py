"""Baseline decoders (BP-OSD and relay-BP) at the relay-BP authors' settings, and a shared scoring loop.

The settings are those of the authors' published results for the Gross code:
https://github.com/trmue/relay, examples/data/bicycle_bivariate_144_12_12_fine_ler_sweep.csv
"""
import time

import numpy as np
from ldpc import BpOsdDecoder

# BP-OSD: 80 min-sum iterations, then a combination sweep of order 10.
BPOSD_SETTINGS = {"max_iter": 80, "bp_method": "minimum_sum", "ms_scaling_factor": 1.0,
                  "osd_method": "OSD_CS", "osd_order": 10}
# Relay-BP: plain min-sum, a first leg of 80 iterations with memory strength 0.15, up to 300
# more legs of 60 iterations with memory strengths drawn from the interval, stop after 5 solutions.
RELAY_SETTINGS = {"alpha": 1.0, "gamma0": 0.15, "pre_iter": 80, "num_sets": 300, "set_max_iter": 60,
                  "gamma_dist_interval": (-0.22628432386414646, 0.6216020925981884), "stop_nconv": 5}


def bposd_decoder(H, priors, **changes):
    """BP-OSD at the authors' settings. Keyword arguments replace single settings."""
    return BpOsdDecoder(H, error_channel=list(priors), **(BPOSD_SETTINGS | changes))


def relay_decoder(H, priors, **changes):
    """Relay-BP at the authors' settings. Keyword arguments replace single settings."""
    import relay_bp  # optional: needs a Rust build
    return relay_bp.RelayDecoderF64(H.tocsr(), error_priors=priors, **(RELAY_SETTINGS | changes))


def score(decode, L, det, obs, before_shot=None):
    """Decode every shot. Returns (failed, seconds) with one entry per shot.

    decode maps one syndrome to an error vector over the columns of H.
    A shot fails when any predicted observable is wrong.
    before_shot(k) runs before shot k and is not timed.
    """
    failed, seconds = np.zeros(len(det), bool), np.zeros(len(det))
    for k, (syndrome, truth) in enumerate(zip(det, obs, strict=True)):
        if before_shot:
            before_shot(k)
        error, seconds[k] = _timed(decode, syndrome)
        predicted = (L @ error) % 2   # uint8 sums wrap at 256, which preserves the parity
        failed[k] = (predicted != truth).any()
    return failed, seconds


def _timed(decode, syndrome):
    """(error vector, seconds) of one decode call."""
    start = time.perf_counter()
    error = decode(syndrome)
    return np.asarray(error, np.uint8), time.perf_counter() - start


def per_cycle_rate(failed, cycles):
    """(rate, standard error) of the logical error rate per syndrome cycle.

    failed marks the shots that failed. With failure fraction P the rate is
    1 - (1 - P)^(1/cycles).
    """
    total = failed.mean()
    sigma = np.sqrt(total * (1 - total) / len(failed))
    rate = 1 - (1 - total) ** (1 / cycles)
    rate_plus_sigma = 1 - (1 - min(total + sigma, 1.0)) ** (1 / cycles)
    return rate, rate_plus_sigma - rate


def print_score(name, failed, seconds, cycles):
    """One line: failures per basis, logical error rate per cycle, decode time per shot.

    failed and seconds have one row per shot and one column per memory basis.
    A row fails when any of its bases fails. Its decode time is the sum over the bases.
    """
    rate, error = per_cycle_rate(failed.any(axis=1), cycles)
    ms = seconds.sum(axis=1) * 1e3
    print(f"{name:10s} failures {failed.sum(axis=0)} of {len(failed)}  per cycle {rate:.2e} +- {error:.1e}  "
          f"mean {ms.mean():.1f} ms  p99 {np.percentile(ms, 99):.0f} ms")

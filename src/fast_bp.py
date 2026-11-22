"""The fast first-stage decoder (plain BP) and the clues the router looks at."""
import numpy as np
from ldpc import BpDecoder

# Plain min-sum BP: few iterations, no OSD. Fast but sometimes wrong.
FAST_SETTINGS = {"max_iter": 30, "bp_method": "minimum_sum", "ms_scaling_factor": 1.0}

FEATURE_NAMES = ["detectors fired", "BP converged", "errors blamed",
                 "weakest-20 confidence", "weakest confidence", "unsure count"]


def fast_decoder(H, priors):
    """Build a plain BP decoder for the decoding problem H with error probabilities priors."""
    return BpDecoder(H, error_channel=list(priors), **FAST_SETTINGS)


def features(syndrome, bp, error):
    """Six numbers describing how hard this shot was for BP (call right after bp.decode)."""
    llr = np.abs(np.asarray(bp.log_prob_ratios))   # BP's confidence per error; small = unsure
    weakest = np.partition(llr, 20)[:20]           # the 20 errors BP was least sure about
    return [syndrome.sum(),        # how many detectors fired
            int(bp.converge),      # 1 if BP's answer explains every alarm
            error.sum(),           # how many errors BP blamed
            weakest.mean(),
            weakest.min(),
            (llr < 2.0).sum()]     # how many errors BP was unsure about


def is_correct(L, error, truth):
    """True if the error guess predicts all 12 logical bits correctly."""
    return not ((L @ np.asarray(error, np.uint8)) % 2 != truth).any()


def fast_features(bp, L, det, obs):
    """Run BP on every shot. Returns (features per shot, whether BP was right per shot)."""
    feats, correct = [], []
    for syndrome, truth in zip(det, obs):
        error = bp.decode(syndrome)
        feats.append(features(syndrome, bp, error))
        correct.append(is_correct(L, error, truth))
    return np.array(feats), np.array(correct)

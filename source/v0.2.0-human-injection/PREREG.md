# PREREG — membrane-nervous-system v0.2.0

Written BEFORE the v0.2.0 demo run. Bars are fixed here and are
not moved after seeing results. If a bar fails, the failure is
reported, not tuned away.

## What is added, in one line

1. A human-frequency layer (`human.py`): the membrane's gate
   becomes frequency-sensitive, centred on a CHOSEN sensitive
   frequency.
2. A Crystallize injection (`injection.py`): on a rejection,
   commit a probability, sample fresh variants, revise, score —
   without ever moving the gate or storing a new pattern.

## The sensitive frequency — chosen, not measured

Bands reused exactly from `bentov-kuramoto/chain.py` NATURAL_HZ,
which that package already labels illustrative, not measurements:

- breath 0.25 Hz, heart 1.2 Hz, aorta 7.0 Hz, brain 10.0 Hz
  (alpha mid-band).

SENSITIVE_HZ = 7.0 Hz. This is Bentov's alignment frequency:
in the bentov-kuramoto chain, meditation ON forces all four
nodes toward ~7 Hz and the heart-brain spread falls to 0.000.
Choosing 7.0 Hz here reuses that toy alignment; it is NOT a
measurement of any person, NOT a medical finding, and NOT
evidence that 7 Hz does anything in a real body.

Sensitivity curve, imposed by design, not discovered:

    s(f) = exp(-0.5 * ((f - 7.0) / 1.5) ** 2)

Width 1.5 Hz is a chosen parameter, stated here. The experiment
tests that the imposed curve works as designed, nothing more.

## Pre-registered bars (seed 42 system, gate calibrated exactly
## as in demo.py: 100 in-probes sigma 0.15, 100 random, rng 11)

- F1 (analytic): s(7.0) = 1.0, s(0.25) < 0.01, s(10.0) < 0.20.
- F2 (frequency gate): clean pain probe at f = 7.0 Hz is
  accepted; the same probe at f = 0.25 Hz is refused; at
  f = 10.0 Hz is refused.
- I1 (fail-closed): after any injection run, tau is unchanged
  and the number of stored patterns is still 4.
- I2 (rescue, sigma = 0.30, 40 noisy stored probes, f = 7.0):
  injected accept rate > stock accept rate on the same probes.
- I3 (not accept-everything, sigma = 0.30, f = 7.0): injected
  accept rate on 40 random fields < injected accept rate on
  the 40 noisy stored probes.
- I4 (no cost when accepted): a clean pain probe at f = 7.0
  that the stock gate accepts needs 0 injection attempts.

No bar is set on the net calibration score. Brier and net
(-Brier - 0.01 * n) are reported as measured, including if
sampling does not pay for itself — as in microtubule-crystallize
Exp 6, where it did not.

## Fixed injection parameters (not tuned on test data)

- Commit p0 = 0.75 (the membrane-arena injection default).
- Samples n = 20, cost c = 0.01 per sample, revise alpha = 2.0
  (the microtubule-crystallize calibration rule).
- A dedicated RNG stream, separate from the probe stream.
  CORRECTION (after the first test run, bars unchanged): the
  first draft sampled fresh noisy copies of the rejected probe
  and failed bar I2 (19/40 stock, 19/40 injected) — re-noising
  an already noisy probe only degrades it. The corrected method
  follows the arena analogy: a variant is a fresh PARAMETER
  set, width uniform [8, 20] (stock 12) and period uniform
  [30, 50] (stock 40), geometry and seed unchanged, patterns
  recomputed from cached Dijkstra delays. The probe is unchanged;
  variant patterns are never stored in the system.
- Decision uses only the best sampled variant's overlap vs the
  FROZEN tau. Truth (stored vs random) is used only for scoring
  in the demo, never for the decision.

## What this package still does NOT have

- No sensor, no person, no recording, no EEG/ECG, no dataset.
- No claim that any frequency is therapeutic, resonant in a
  real body, or a validation of Bentov.
- No learning: rescued probes are not stored.

# DESIGN.md — membrane-nervous-system v0.1.0

## Why a nervous system, and why it is not the brain package

membrane-brain already holds wave patterns on a two-lobed
layout. A nervous system is a different question: a signal that
enters at the periphery, passes through a relay, and leaves at
a motor stage — with a short route that skips the central stage
and a long route that goes through it. That is what this package
measures. It does not reuse the brain's hemispheres, and it does
not claim the brain package was a nervous system.

## Decisions

- Four stages, 128 neurons total, matching the brain package's
  scale so the two toys are comparable, not because 128 is a
  biological number (it is not).
- Central as a cap on top (centre y = 38), not between spinal
  and motor. This is what makes the reflex route geometrically
  shorter than the central route (53.52 vs 90.65) without adding
  an arbitrary "processing penalty" at central nodes. The
  geometry is the assumption, stated here, not a discovery.
- Sensory modalities are labels on node ids, not separate
  position zones. A touch node and a pain node sit in the same
  sensory ellipse; what differs is which stored wave they seed.
  Claiming spatial modality maps would be inventing anatomy.
- Motor flexor/extensor are labels only. No muscle is modelled;
  membrane-muscle is the separate muscle toy.
- Gate J = 0.990, not 1.000 as in membrane-brain. One in-probe
  or out-probe overlaps the other side of the frozen tau in
  calibration; the demo reports 0.990 honestly rather than
  rounding it to a perfect score.

## Falsified / not built

- A single "nerve impulse" travelling as a spike train: not
  built. The package stores wave snapshots, as the whole
  membrane family does; it does not simulate action potentials.
- Learning in any biological sense: not built. Patterns are
  stored by outer product in one shot; nothing is learned from
  experience in this package.
- A central route that is faster than the reflex route: not
  claimed. In this geometry it is longer, by construction.

## Limits carried from the family

- Delays are distance units from Dijkstra on a seeded graph.
- Recognition at sigma = 0.15 is 40/40, as in the brain package;
  that is a property of enveloped waves on this graph, not a
  property of real sensation.
- The lesion toy removes graph edges. It says nothing about
  real spinal injury, recovery, or treatment.

## v0.2.0 additions

- Frequency does not change which response wins: scaling a
  field scales every overlap equally, so project() ratios are
  unchanged. Only the gate (max overlap vs tau) moves. That
  separation is deliberate and test-pinned.
- The 7.0 Hz centre is a reuse of the bentov-kuramoto toy
  alignment, not a fitted parameter. There is no human data
  here to fit anything to, and the README says so.
- Injection variants vary the membrane (width, period), not
  the probe. This matches the arena injection, where variants
  vary dt and mirror strength. Varying the probe by re-noising
  it was tried first and falsified by its own bar.
- Injection rescues 2 of 21 rejected probes at sigma 0.30.
  That small effect is the honest size of the mechanism on
  this toy; a larger rescue would have meant the gate was
  not doing its job on random fields (it is: 0/40).
- Net score is negative (-0.276 mean). Injection is a
  rescue ledger, not a free calibration win.

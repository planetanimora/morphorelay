# MorphoRelay: a scalar actuator for performance transfer across anatomies

**Planet Animora · Technical note · 27 September 2026**

**Developed at Innowaft for Planet Animora.** Proof-of-concept authors: [Nelli James](https://id.innowaft.com/e006) and [SugamOviyam](https://id.innowaft.com/e019), working at Innowaft.

## 1. Motivation and research question

Creature performance authoring requires choices about correspondence. Human mouth opening can correspond to a hinge, an annulus, several mandibles, or a membrane. A target may have no meaningful vertex or skeletal correspondence to the performer. MorphoRelay investigates a control interface in which the performance is represented by target-independent quantities and a target rig interprets them.

The present implementation is deliberately narrow: a jaw-opening curve controls an annular opening. It asks whether a scalar control can produce a stable, legible response on a different anatomy. It establishes a working test case for a larger research program; it does not establish general expression transfer or semantic equivalence across species.

### Creature-family vocabulary

M1–M6 are Planet Animora's identifiers for creature anatomy families. Each family is intended to have its own adapter that translates shared performance signals into suitable rig controls. The numbering identifies families; it does not indicate development stages or maturity.

| Family | Anatomy | Status in this repository |
|---|---|---|
| M1 | Reserved; anatomy to be defined | No implementation |
| M2 | Reserved; anatomy to be defined | No implementation |
| M3 | Tentacle mouth | Proposed spread, curl, compression, and mouth-gap controls |
| M4 | Radial / circular mouth | Implemented aperture actuator and live jaw input |
| M5 | Beak | Proposed opening, closure strength, and upper/lower beak controls |
| M6 | Feline / cat / lion-like mouth | Proposed jaw, muzzle, lip-corner, and snarl controls |

M4 is the first experiment because a radial mouth exposes a clear, compact actuator: aperture. The other families describe the research roadmap; their rigs and transfer behavior are still to be developed.

## 2. Implemented system

The phone runs Live Link Face in MetaHuman Animator mode with Realtime Animation enabled. Unreal's Live Link Face source publishes a Basic-role subject. `AM4RadialMouthPOCActor` evaluates that subject on Tick and looks up the configured aperture curve. A successful finite value reaches `ApplyAperture`; an unavailable frame or curve leaves the previous pose in place and updates the diagnostic status.

The default curve is `jawOpen`. If it is absent, the adapter searches for a property whose name ends in `jawOpen`, supporting a namespace prefix. Explicitly configured alternative names require an exact lookup. This fallback was introduced during integration debugging; the development record does not identify which name the successful phone session ultimately matched.

Let $a=\min(1,\max(0,j))$. For a rest bone position $b_i$, mouth center $c$, and twelve evenly spaced radial bones,

$$b_i(a)=c+(0.65+0.70a)(b_i-c).$$

Each update derives positions from the reference skeleton, avoiding accumulated pose offsets. Bone transforms are explicitly refreshed after the update. The rig has fourteen bones: root, center, and twelve radial controls. It uses bone translation and linear skinning rather than a simulated tissue model.

## 3. Procedural weights

The imported mouth faces the X axis. For a vertex in the YZ plane, define $r=\sqrt{y^2+z^2}$ and $u=(r-r_{min})/(r_{max}-r_{min})$. The radial influence is

$$w_r=1-\mathrm{smoothstep}(0.15,1,u).$$

The angle $\mathrm{atan2}(y,z)$ determines two adjacent radial bones. Linear interpolation within the angular sector splits $w_r$ between those bones; the center receives $1-w_r$. Each vertex has at most three influences. This makes the inner region follow the radial controls and gradually anchors the outer region.

The radial rest position is $r_{min}+0.28(r_{max}-r_{min})$. These constants are hand-selected for this mesh. Their suitability for another shape must be evaluated.

## 4. Initial observations

The original validation used 1,536 vertices. The stored weights included 1,380 vertices with multiple influences and 156 with a single influence. Bone radii were checked at aperture values 0, 0.25, 0.5, 0.75, and 1; opposite controls agreed within the test tolerance. A synthetic `jawOpen=0.8` reached the bones, and an unrelated curve was rejected.

| Aperture | Mean inner-band radius (cm) | Mean outer-band displacement (cm) | Minimum radius (cm) |
|---|---:|---:|---:|
| 0.0 | 0.968119 | 0.000293 | 0.914141 |
| 0.5 | 2.118307 | 0.000000 | 2.089293 |
| 1.0 | 3.268498 | 0.000293 | 3.224404 |

These values are analytical reconstructions from rest positions and stored weights, not measurements of a live phone sequence or GPU vertices. Inner and outer bands each cover 3% of the source radius span. Endpoint screenshots provide a separate visual check. The operator subsequently reported successful jaw-driven movement in Play, and supplied a demonstration video. No synchronized input/output recording, participant study, or latency benchmark was collected.

## 5. Interpretation

The demonstration shows that a selected human facial signal can control a geometrically different actuator in an Unreal scene. The target rig supplies the geometric interpretation; the capture system supplies the control signal. This separation gives artists a concrete place to change sensitivity, motion constraints, and anatomy-specific behavior.

A scalar mapping necessarily loses information. Lip closure, jaw direction, emotion, speech articulation, and asymmetric motion are not modeled. A visually responsive aperture does not by itself prove perceptual preservation of a performance. The next useful result is a measured comparison, rather than an increased number of untested mappings.

## 6. Evaluation plan

| Question | Experiment | Measurements |
|---|---|---|
| Is the actuator controllable? | Ask performers to reach and hold five target apertures | Absolute target error, settling time, variance during holds |
| Does calibration help? | Compare raw mapping with per-user neutral/open calibration | Range used, saturation rate, task error |
| What does smoothing cost? | Replay the same captured curve with several filter settings | Output jitter and added delay |
| How robust is the stream? | Introduce dropouts and reconnect | Stale-pose duration, recovery time, visible discontinuity |
| Does the interface generalize? | Implement radial, hinged, and segmented targets | Authoring time, required parameters, deformation failures |
| Is intended action recognizable? | Blinded viewer assessment of target performances | Action identification, agreement, preference |

Record device and app versions, frame rates, network conditions, calibration procedure, and engine revision. Report per-session data, uncertainty, and failure cases. Any latency claim needs a synchronized capture protocol; editor frame rate alone is insufficient.

## 7. From the first actuator to expressive creatures

### Original intent

MorphoRelay began with the idea of applying MetaHuman's solved performance signals to custom creature meshes. The aim is to reuse the timing and expressive detail of a human performance while giving each creature a rig suited to its own anatomy. A jaw opening, a moment of compression, or a left–right imbalance could become a radial contraction, a beak movement, or coordinated tentacle articulation through an authored mapping.

We view the M4 prototype as a stepping stone toward that broader system. It demonstrates the smallest complete path: a solved jaw-opening signal reaches a custom skeletal mesh and controls its aperture in real time. This gives the project a working input-to-actuator connection on which more expressive mappings can be built.

### A shared performance source, several anatomies

The proposed next architecture introduces an intermediate representation of opening, closure, compression, roundness, asymmetry, and intensity. Each creature-family adapter would translate those quantities into its own controls. M5 could map opening and closure to a beak; M3 could distribute opening, compression, and asymmetry across tentacle spread, curl, and coordination. M6 could retain more jaw, muzzle, and lip-corner articulation. These examples are research hypotheses that need implementation and evaluation on the intended meshes.

For prerecorded work, we intend to derive this representation from the solved animation curves associated with a MetaHuman Performance Asset, then store or replay the resulting creature-control animation. The ambition is to solve a performance once and reinterpret it across several creature families. The current repository implements the Live Link input path; an offline Performance Asset adapter and the shared intermediate representation remain future work.

### Expressive motion and emotional readability

A further goal is to explore whether performance-derived motion can communicate expressive intent through unusual anatomy. For example, the timing and intensity of a performed expression might inform tentacle contraction, spreading, or coordinated secondary motion. Such mappings would need artistic direction and viewer studies to establish whether the intended expression remains readable. The current aperture signal does not infer emotion, and a facial control value alone does not establish an emotional label.

### Present limits and the next proof

Current behavior is validated on one source mesh and one operator's setup. The adapter clamps values, holds the last pose on missing data, and has no calibration, smoothing, stale-frame timeout, or recovery interpolation. It assumes an annular mesh centered on the origin with a useful radial profile. Self-intersection, volume preservation, and expressive quality have not been quantified. Packaged-game support and other platforms have not been established.

The next architectural test is to drive M4 and a second family—M5 beak or M3 tentacle mouth—from the same performance representation. That experiment would test how much of the mapping is reusable, how much must be authored for a specific anatomy, and which aspects of the performance survive the transfer. The evaluation plan above provides the measurements needed to examine those questions.

The existing literature includes skeletal retargeting, correspondence-based deformation transfer, and facial retargeting. MorphoRelay's present contribution is its runnable actuator example, procedural construction, and documented integration. The broader research proposition is a reusable performance interface with anatomy-specific interpretation. Establishing that proposition as a general method requires further experiments and comparisons with prior work.

## References

1. Michael Gleicher. 1998. [Retargetting Motion to New Characters](https://graphics.cs.wisc.edu/Papers/1998/Gle98/retarget-preprint.pdf). SIGGRAPH.
2. Robert W. Sumner and Jovan Popović. 2004. [Deformation Transfer for Triangle Meshes](https://people.csail.mit.edu/sumner/research/deftransfer/). ACM Transactions on Graphics.
3. Epic Games. [Using a Live Link Face Source](https://dev.epicgames.com/documentation/en-us/metahuman/using-a-live-link-face-source). Documentation accessed 27 September 2026.

# EP01 — Máy xúc nghiêng dốc: dầu mất thật hay mức đo sai?

Status: CONCEPT / TECHNICAL CLAIMS PENDING REVIEW. Two distinct versions; do not conflate them.

## Audience promise
By the end, viewers can answer: '**Why can a fuel level sensor change when a machine tilts even without a matching decrease in actual fuel volume?**' and '**why a suspicious fuel-level drop is not automatic evidence of theft?**'

## Technical guardrails
- Distinguish sensor *measured level* from actual *liquid volume* and consumed fuel over time. Reading depends on tank geometry, sensor position, machine orientation, slosh and filtering.
- On a tilt, a liquid free surface tends to remain approximately perpendicular to gravity when relatively static; its height relative to a sensor may change with tank attitude. Actual sensor response depends on technology and mount.
- Real engine fuel use is independent of sensor reading artifact and must be considered; no definitive fault diagnosis from one signal.
- Mitigation examples: synchronized timestamps, IMU orientation, operation state, calibrated volume mapping and temporal filtering are **candidate methods**, not proof of FuelGuard performance.
- Never claim theft detection accuracy or validation without independently approved evidence.
- Illustrative scenes are not a PC200-8 as-built schematic.

## TikTok: ~2:00 / portrait 9:16 (story-driven)
| Time | Beat | Image/action |
|---|---|---|
| 0:00–0:10 | Capy screams 'Trộm dầu?!' | studio capy bounces, warning icon |
| 0:10–0:25 | Mechanic/narrator challenges assumption | excavator turns up slope |
| 0:25–0:45 | tank level demonstration | transparent tank, liquid/gravity, illustrated sensor marker |
| 0:45–1:05 | actual volume vs reading | contrasting two side-by-side panels |
| 1:05–1:25 | why vibration + filtering matter | mini chart noisy samples vs smoothed |
| 1:25–1:45 | research workflow, no unproven claims | block diagram: sensor + IMU + machine state + algorithm |
| 1:45–2:00 | Capy realizes and teases CAN episode | happy bounce, logo and gentle CTA |

## YouTube: ~10:00 / landscape 16:9 (educational long form)
| Time | Chapter | Educational value |
|---|---|---|
| 0:00–0:40 | Cold open: tilt + apparent fuel loss | engaging problem, distinguish reading vs loss |
| 0:40–1:40 | What a fuel level sensor actually measures | sensor types, uncertainty |
| 1:40–3:10 | Tank orientation and free-surface geometry | physical demonstration, diagram, intuitive volume/level distinction |
| 3:10–4:25 | Why fuel slosh and vibration corrupt readings | temporal dynamics, examples of sampling |
| 4:25–5:40 | Why filtering alone cannot fix all problems | lag, slope vs short oscillations, time sync |
| 5:40–7:10 | Combining sensor + IMU + context | architecture; clearly label hypotheses |
| 7:10–8:30 | A synthetic example walkthrough | toy data / visual graph; no private telemetry |
| 8:30–9:30 | Designing a verification experiment | controlled tilt, refill, repeated observations, ground truth |
| 9:30–10:00 | Recap + tease CAN/ECU | concise three-part takeaway |

## Scene production
- Capy in studio is an anchor but should not be a static talking head for 10 minutes.
- Cutaways: excavator slope, transparent tank, float/sensor, IMU vector, sample time-series plots, algorithm block and controlled experiment.
- Separate wide and vertical compositions and prioritize readable engineering figures.
- First milestone: 15–25s voiced proof of style with Capy + excavator + one diagram, not full-length production.

## Release gate
Scientific reviewer approval, animated mascot continuity, audio narration complete, rights cleared for logos/music/media, all platform versions played through and inspected before upload.

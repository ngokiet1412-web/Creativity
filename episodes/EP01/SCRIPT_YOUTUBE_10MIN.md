# CAPY BK EP01 — YouTube ~10-minute long-form treatment (DRAFT)

**Title option:** Máy xúc nghiêng dốc: Bình dầu bị mất thật hay cảm biến đang đánh lừa mình?
**Format:** 16:9, 1920x1080 30fps, target 9:30–10:30, split host/B-roll roughly 25%/75%. Audience: new learners and automotive/mechanical engineering students; avoid making it a FuelGuard advertisement.

## Timed outline and voice beats (to be expanded / read aloud for timing)
| Time | Scene | Voice concept + visual |
|---|---|---|
| 00:00–00:35 | Cold open | Capy sees sudden displayed 'fuel drop' after hill; play comic accusation, engineer says stop: indication is not proof; quick visual of excavator going uphill |
| 00:35–01:20 | Introduce problem | What actually gets measured? Distinguish quantity in tank, liquid height at sensor, instrument display, and fuel consumption; show four labeled boxes |
| 01:20–02:25 | Gravity & tank angle | Free surface roughly horizontal in gravity frame during quasi-static tilt; container tilts around it; tank geometry/sensor position determine apparent level. Demonstrate two identical-volume tilted tanks |
| 02:25–03:20 | Sloshing | Vibration/acceleration, time lag, filtering. Animated tank on uneven terrain; distinguish true change vs measurement noise |
| 03:20–04:15 | Sensor types | Generic level measurement (e.g. float/other sensor) and calibration; not all machines use identical instruments; do NOT claim a specific PC200-8 model has this exact sensor without verified manual/field survey |
| 04:15–05:15 | Common mistakes | 'Fuel reading down' not equal 'stolen'. Could be slope, consumption, filtering, sampling, calibration or actual loss. Graphic checklist: evidence vs competing explanations |
| 05:15–06:30 | Systems engineering | Practical signal stack: fuel level + IMU orientation + engine operating state, timestamps, filtering, plausible geometry; why sensor fusion is hard |
| 06:30–07:35 | AI role | Feature examples: rate of change, slope correction, duration, engine-off state. AI can rank anomalies; can't prove motive or theft. Explain false positives/false negatives with Capy gag |
| 07:35–08:40 | Validation | Safe simulated experiment: tank incline at fixed fuel volume, repeat at multiple angles, log time/angle/level. Compare with known volume. Do not claim these tests already occurred or fabricate results |
| 08:40–09:30 | Engineering takeaway | Four takeaways: quantity vs level, motion, calibration, evidence. Capy summarizes in friendly way |
| 09:30–10:00 | Teaser / CTA | Next: can excavator computers 'talk'? Introduction of CAN/ECU in episode 02 |

## Long-form scripted anchors
**00:00 CAPY:** 'Ê! Máy xúc vừa leo dốc xong, đồng hồ dầu tụt một đoạn! Ai lấy dầu của tui?'
**00:08 NARRATOR:** 'Khoan kết luận. Có ít nhất hai chuyện khác nhau: nhiên liệu thật sự giảm, hoặc con số hiển thị thay đổi dù lượng dầu chưa giảm tương ứng.'
**01:20 NARRATOR:** 'Hãy tưởng tượng một chiếc hộp chứa nước. Ta không rút giọt nào, chỉ nghiêng hộp thôi. Mặt thoáng chất lỏng chịu tác dụng của trọng lực, trong khi thành bình xoay theo máy. Điểm mà cảm biến quan sát có thể đọc một độ cao khác.'
**03:20 CAPY:** 'Vậy mọi máy xúc đều đo bằng một cái phao hả?'
**03:24 NARRATOR:** 'Không. Cấu tạo khác nhau theo máy và hệ thống. Bản vẽ này chỉ là một ví dụ mô phỏng để hiểu nguyên lý, không phải sơ đồ của một mẫu máy cụ thể.'
**06:30 CAPY:** 'Có AI là biết ngay tên kẻ trộm dầu hả?'
**06:35 NARRATOR:** 'Không. AI có thể hỗ trợ tìm bất thường trong dữ liệu. Muốn kết luận điều gì đã xảy ra, vẫn cần ngữ cảnh, phép đo được kiểm chứng và bằng chứng thực tế.'
**09:30 CAPY:** 'Vậy muốn làm kỹ sư giỏi, trước tiên phải ngừng đổ oan cho... cái cảm biến!'
**09:42 NARRATOR:** 'Tập sau mình sẽ tìm hiểu các bộ điều khiển trên xe trao đổi thông tin bằng cách nào.'

## Research checklist before recording
- Cite authoritative sources for fluid free-surface behavior, float sensor calibration, general telemetry/IMU basics.
- If PC200-8, CAN or proprietary fuel system details appear, require verified model-serial specific evidence; otherwise omit them.
- Discuss uncertainties honestly: moving machinery acceleration makes real liquid motion more complex than the quasi-static illustration.
- Owner to verify every physical diagram and narration. No fictional test statistics or customer machine footage.

## Scene production note
This is a **10-minute narrative treatment with timed voice beats**, not a fully word-for-word 10-minute recording transcript. Expand individual scenes into owner-reviewed read-aloud paragraphs, record real speaking rate and retime. Preserve audience-friendly pacing and 3D animated diagrams.

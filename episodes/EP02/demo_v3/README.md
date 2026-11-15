# CAPY BK EP02 V3 · Demo thủy lực nâng cần PC200-8 (DRAFT)

**42 giây · 1920 × 1080 · 30 fps.** Đây là bản demo sửa theo `../ANIMATION_QUALITY_V3_BRIEF.md` và Issue #8, đi theo chuỗi Động cơ → Bơm → Van → Xi lanh cần → Cần chuyển động. Bản này thay cho demo V2 ở `../demo/` (PR #9). Đang chờ owner duyệt, chưa dựng tập dài hoặc bản TikTok.

- Storyboard: [STORYBOARD.md](STORYBOARD.md)
- Phân vai và mốc thoại: [audio_timing.csv](audio_timing.csv)
- Phụ đề riêng: [EP02_V3_demo_vi.srt](EP02_V3_demo_vi.srt)
- Báo cáo kỹ thuật, nguồn và QA: [TECHNICAL_QA_V3.md](TECHNICAL_QA_V3.md)
- Manifest tài nguyên: [ASSET_MANIFEST.md](ASSET_MANIFEST.md)

## Cấu trúc project Godot

```
godot/
  main.tscn        Cảnh chính + AnimationPlayer "sequence" (17 track keyframe)
  director.gd      Đọc track, đặt camera, tính trạng thái thủy lực theo thời gian, chế độ --qa
  rig.gd           Rig máy đào: khâu cứng quay quanh chốt, xi lanh giải theo 2 chốt, cơ cấu 4 khâu gầu
  hydraulics.gd    Nhìn xuyên khoang máy: động cơ, bơm, đĩa nghiêng, van, joystick, LS, ống dầu
  env.gd           Phông, bóng, đống đất bị múc, đất rơi, khói xả
  crew.gd          Capy + anh kỹ sư sau rào (lớp cục bộ)
  hud.gd           Nhãn bộ phận, chú giải màu, chuỗi năng lượng, lớp chẩn đoán --pins
  intro.gd         Mở kênh 0–4 s
  art/             Lớp máy cắt từ atlas đã commit, rig.json, parts.json, motion_plan.json
  local/           (không commit) cel studio EP01, lớp nhân vật, SIGNATURE.wav
tools/
  prepare_layers.py   Cắt lớp máy và lớp nhân vật, đo chốt
  kinematics.py       FK/IK dùng chung với rig.gd
  build_scene.py      Lập quỹ đạo đào bằng IK và ghi main.tscn
  make_foley_v3.py    Tạo tiếng máy từ telemetry.csv
```

## Mở và chỉnh

1. Chép thư mục `local/` trong gói bàn giao vào `godot/local/` (cel studio, lớp nhân vật, SIGNATURE.wav).
2. Mở `godot/project.godot` bằng Godot 4.5.1. Các script có `@tool`, nên khi kéo thanh thời gian của `AnimationPlayer → sequence` trong editor, máy, dầu và camera cùng cập nhật.
3. Sửa khớp: track `boom_deg`, `arm_rel`, `bucket_rel` (độ). Đoạn đào 4–9,1 s được nướng từ IK, 15 key/giây. Muốn đổi quỹ đạo thì sửa `WAYPOINTS` trong `tools/build_scene.py` rồi chạy `python3 tools/build_scene.py`. Các track khác (camera, joystick, spool, xray, cutaway, nhãn, chuỗi, đầu Capy) sửa thẳng trong editor.
4. Hình học chốt và xi lanh nằm trong `godot/art/rig.json`.

## Kiểm thử và xuất

```bash
# QA hình học 1.260 khung -> qa_geometry.txt, telemetry.csv
godot --path godot --fixed-fps 30 --quit-after 1260 res://main.tscn -- --qa
# ảnh chẩn đoán chốt tại một thời điểm
godot --path godot --write-movie pins.png --fixed-fps 30 --quit-after 2 res://main.tscn -- --pins --start=27.6
# render
godot --path godot --resolution 1920x1080 --write-movie EP02_V3.avi --fixed-fps 30 --quit-after 1260 res://main.tscn
ffmpeg -i EP02_V3.avi -map 0:v -c:v libx264 -crf 17 -pix_fmt yuv420p picture.mp4
python3 tools/make_foley_v3.py telemetry.csv godot/local/audio/SIGNATURE.wav out/
```

Trên Windows dùng `Godot_v4.5.1-stable_win64_console.exe` thay cho `godot`. Movie Maker cần phiên có đồ họa. Bản render trong gói bàn giao được dựng bằng Godot 4.5.1 Linux (đã đối chiếu SHA-512 với bản phát hành) dưới Xvfb, ra đúng 1920 × 1080, không phải co giãn.

## Nhập vào CapCut Pro

1. Tạo project 16:9, 1920 × 1080, 30 fps. Đặt `CAPY-BK-EP02-V3-picture.mp4` (hình không tiếng) ở 00:00 trên track video.
2. Tạo 4 track tiếng: `SIGNATURE`, `CAPY`, `ENGINEER`, `MACHINE`. Đặt `SIGNATURE.wav` ở 00:00.480 và `MACHINE.wav` ở 00:00.000. Đặt WAV CAPY/ENGINEER theo cột `start` trong `audio_timing.csv` khi có bản thu. Giảm `MACHINE` khoảng −8 dB dưới giọng.
3. Nhập `EP02_V3_demo_vi.srt` làm phụ đề. Chữ không nằm trong hình nền nên có thể đổi kiểu chữ trong CapCut.
4. Nếu câu thoại thật dài hoặc ngắn hơn ô thời gian, sửa keyframe trong Godot (dời cả cụm key của cảnh đó), render lại rồi thay clip. Không tua nhanh giọng để khớp hình.
5. Xuất H.264/AAC 1080p30 cho owner duyệt. Không đăng YouTube/TikTok.

`CAPY-BK-EP02-V3-PC200-8-demo.mp4` là bản xem nhanh, đã trộn sẵn tag và tiếng máy, chưa có giọng EP02.

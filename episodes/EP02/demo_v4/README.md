# CAPY BK EP02 V4 · Bản mẫu 16 giây: cần nâng và dầu vào xi lanh (DRAFT)

**16 giây · 1920 × 1080 · 30 fps · 480 khung.** Đây là bản V3 được nâng cấp theo `../CLAUDE_V3_VS_ARGON_REVIEW_20261112.md` (mục “Acceptance test 12–18 seconds”) và `../ANIMATION_QUALITY_V3_BRIEF.md`. V4 giữ nguyên rig, hình máy, bố cục cận cảnh và cách chuyển từ toàn máy vào bên trong của V3, rồi sửa chuyển động, phần thủy lực và phong cách hình. V3 vẫn để nguyên ở `../demo_v3/` để so sánh. Chưa dựng tập 10–12 phút.

- Storyboard và nhịp: [STORYBOARD_V4.md](STORYBOARD_V4.md)
- Báo cáo kỹ thuật, các điểm chưa xác minh và QA: [TECHNICAL_QA_V4.md](TECHNICAL_QA_V4.md)
- Bảng so sánh trước/sau với V3: [BEFORE_AFTER_V3_V4.md](BEFORE_AFTER_V3_V4.md)
- Phân vai và mốc thoại: [audio_timing.csv](audio_timing.csv) · phụ đề: [EP02_V4_proof_vi.srt](EP02_V4_proof_vi.srt)
- Manifest: [ASSET_MANIFEST.md](ASSET_MANIFEST.md)

## Thay đổi so với V3

| Phần | V4 |
|---|---|
| Phong cách | Shader `godot/ink.gdshader` cho mọi lớp máy: viền mực ấm, chia tông mềm, giảm vân ảnh. Chỉ đổi màu, không đổi hình học. Máy chuyển từ “ảnh render” sang minh họa kỹ thuật 2.5D, hợp với Capy 2D. |
| Chuyển động cần | Ty xi lanh đi theo hồ sơ tốc độ min-jerk: khởi động, tăng tốc, đi đều (lưu lượng không đổi thì ty đi đều), giảm tốc, dừng. Góc cần được giải ngược từ chiều dài ty qua hình học chốt. |
| Chịu tải | Van mở thì áp tăng trước, cần võng 0,12° khi tải chuyển sang dầu, sau đó mới đi lên. Khi dừng, cần nhún tắt dần 0,28° (dầu bị nén dưới tải). |
| Phản ứng máy | Cả máy nghiêng cứng tối đa 0,14° quanh bánh dẫn trước theo gia tốc góc cần. Thân rung ≤ 0,45 px tỷ lệ với tải bơm. Đều là phép biến đổi cứng, không biến dạng. |
| Gầu | Xi lanh gầu duỗi qua cơ cấu 4 khâu, gầu cuộn 38° → 64° và vượt nhẹ 0,8° rồi về. Đất rơi khỏi mép gầu theo trọng lực, có bụi khi chạm đất. |
| Bóng | Bóng gầu và bóng tay gầu trên nền, đổi cỡ và độ đậm theo độ cao. Có thêm bóng tiếp xúc của máy. |
| Thủy lực | Camera đi liền một mạch: động cơ → bơm → van → theo ống A xuống xi lanh → mặt cắt piston. Vạch dầu chạy theo thể tích ty đẩy. Mỗi nhãn ghi rõ **K1 ✓** (đã đối chiếu brochure Komatsu) hoặc **NGUYÊN LÝ** (minh họa giản lược). |
| Capy | Mở bằng studio EP01 có ly BK. Capy và anh kỹ sư đứng sau rào nhìn máy: đầu nghiêng theo cần, chớp mắt, gật “À há” khi gầu cuộn. |
| Lỗi V3 đã sửa | Bộ ghi scene của V3 ghi số nguyên (`1` thay vì `1.0`), nên Godot nội suy theo bậc. Ở V3 việc mờ dần x-ray, joystick, con trượt và độ nghiêng đầu Capy thực ra bị nhảy bậc. V4 ghi số thực nên các chuyển động này mượt. |

## Mở, chỉnh, kiểm thử

1. Giải nén `local/` trong gói bàn giao vào `godot/local/`, rồi mở `godot/project.godot` bằng Godot 4.5.1. Scene chính là `main.tscn` (V4).
2. Các key cần/tay gầu/gầu được nướng sẵn từ `tools/build_scene.py`: `boom_profile()` (hồ sơ tốc độ ty) và `bucket_profile()`. Sửa ở đó rồi chạy `python3 tools/build_scene.py`. Camera, x-ray, mặt cắt, nhãn và đầu Capy là track thường, sửa thẳng trong AnimationPlayer.
3. Tham số phản ứng máy nằm trên node `Main`: `tremor_px`, `pitch_gain`, `crumb_bursts`, `capy_blinks`.

```bash
godot --path godot --fixed-fps 30 --quit-after 480 res://main.tscn -- --qa      # QA -> qa_geometry.txt, telemetry.csv
python3 tools/plot_pins.py telemetry.csv godot/art/rig.json pins.png               # đồ thị chốt/xi lanh
godot --path godot --write-movie pins.png --fixed-fps 30 --quit-after 2 res://main.tscn -- --pins --start=10.5
godot --path godot --resolution 1920x1080 --write-movie V4.avi --fixed-fps 30 --quit-after 480 res://main.tscn
godot --path godot --resolution 1920x1080 --write-movie layer.png --fixed-fps 30 --quit-after 480 res://main.tscn -- --pass=machine
python3 tools/make_foley_v4.py telemetry.csv godot/local/audio/SIGNATURE.wav out/ 0.12
```

`--pass` gồm `bg`, `machine` (máy + đất), `hydraulics` (x-ray, dòng dầu, nhãn), `crew`, `intro`. Các pass xuất PNG có kênh alpha.

## Layer chuyển động cho CapCut Pro

Gói bàn giao có:
- `layers/EP02_V4_layer_bg.mp4`: phông công trường, bóng, lớp làm tối khi nhìn xuyên.
- `layers/EP02_V4_layer_machine.webm`, `layers/EP02_V4_layer_hydraulics.webm`, `layers/EP02_V4_layer_crew.webm`, `layers/EP02_V4_layer_intro.webm`: VP9 có kênh alpha.

Xếp từ dưới lên: bg → machine → hydraulics → crew → intro, tất cả đặt ở 00:00. Nếu CapCut không đọc được alpha của WebM, chạy lệnh `--pass` ở trên để xuất PNG, rồi chuyển sang ProRes 4444: `ffmpeg -i layer%08d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le layer.mov`. Lưu ý file ProRes khá nặng, khoảng 1–2 GB mỗi layer.

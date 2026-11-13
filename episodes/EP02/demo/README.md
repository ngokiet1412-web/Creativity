# CAPY BK EP02 · Demo Hệ Thống Thủy Lực Komatsu PC200-8 (V3)

**Bản nghiệm thu Giai đoạn 2 & 3 · 42 giây (`sequence`) + Clip QA Proof 16 giây (`proof_16s`) · 1920 × 1080 · 30 FPS.**
Dự án Godot 4.5.1 minh họa toàn bộ chuỗi truyền lực thủy lực trên máy đào **Komatsu PC200-8**:
`Động cơ SAA6D107E-1 (110 kW) → Cụm bơm piston đĩa nghiêng (439 L/phút) → Tay trang PPC & Van phân phối CLSS / Bù áp → Xi lanh cần, tay gầu, gầu xúc đất → Nâng cần, giữ tải & Hồi dầu qua két làm mát, lọc về thùng`.

---

## 1. Mở và chỉnh sửa Project Godot 4.5.1

1. Mở `episodes/EP02/demo/godot/project.godot` trong **Godot 4.5.1**, sau đó mở scene `res://demo.tscn` và nhấn **F6** để chạy trực tiếp.
2. Cấu trúc các nút tách lớp trong `demo.tscn`:
   - `Field` (`Node2D`): Vẽ nền phòng studio (cảnh `D01`) và công trường có mây trôi, bóng đổ mặt đất theo độ cao gầu.
   - `Machine` (`Node2D`, script `res://machine.gd`): Mô hình máy đào PC200-8 tách lớp cứng (`Track`, `Upper`, `BoomRamFar`, `Boom/Stick/Bucket`, `BoomRamNear`). Cả 3 khâu `Boom`, `Stick`, `Bucket` quay quanh đúng tâm chốt (`BOOM_PIN`, `ELBOW`, `WRIST`) với `scale == Vector2.ONE`, dẫn động bởi cặp xi lanh cần, xi lanh tay gầu và xi lanh gầu + cơ cấu 4 khâu, kèm mô đất biến dạng và hạt đất rơi theo trọng trường $g$.
   - `DiagramLayer` (`Node2D`): Vẽ các mặt cắt kỹ thuật động hóa (động cơ 6 xi lanh `SAA6D107E-1`, bơm piston đĩa nghiêng, tay trang PPC & van trượt CLSS, xi lanh nâng cần tác động kép, mạch hồi qua két làm mát & lọc về thùng).
   - `Characters` (`Node2D`, script `res://characters.gd`): Rig nhân vật 2D tách lớp cho **Anh kỹ sư** (`Engineer/{ArmR,Torso,Head/{Brows,Eyelids,Mouth},ArmL}`) và **Capy BK** (`Capy/{Torso,PawLWave,Head/{Brows,Eyelids,Mouth,Hat},PawLRail,PawRRail}`) đứng sau hàng rào an toàn `SafetyRail`.
   - `AnimationPlayer`: Chứa animation `sequence` (42,0 giây) và `proof_16s` (16,0 giây) điều khiển các thuộc tính `lift_amount`, `stick_amount`, `bucket_amount` và `pilot_amount`.

---

## 2. Chạy kiểm thử tự động (`--qa`) và xuất video bằng Movie Maker

Từ thư mục `episodes/EP02/demo`, chạy bằng Godot 4.5.1 Console và FFmpeg:

```powershell
# 1. Kiểm thử tự động toàn bộ 1.260 frame (42s) + 480 frame (16s proof)
godot --headless --path godot -- --qa

# 2. Ghi file AVI bằng Movie Maker (bản 42s và bản 16s V3 proof)
godot --path godot --write-movie out/EP02-V3-Godot.avi --fixed-fps 30 --quit-after 1260
godot --path godot --write-movie out/EP02-V3-Proof16s.avi --fixed-fps 30 --quit-after 480 -- --proof16

# 3. Nén ra MP4 H.264 + AAC 1920x1080 @ 30fps giữ nguyên tỷ lệ khung hình 16:9
ffmpeg -y -i out/EP02-V3-Godot.avi -i out/MACHINE.wav -i out/SIGNATURE.wav `
  -filter_complex "[0:v]scale=1920:1080:flags=lanczos:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#142c36,setsar=1:1[vout];[2:a]adelay=480|480[sig];[1:a][sig]amix=inputs=2:duration=first:dropout_transition=0,volume=1.6[aout]" `
  -map "[vout]" -map "[aout]" -c:v libx264 -crf 17 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k out/CAPY-BK-EP02-PC200-8-demo.mp4
```

Xem chi tiết tại [Storyboard](STORYBOARD.md), [Bảng phân vai & timing âm thanh](audio_timing.csv), [Phụ đề SRT](EP02_demo_vi.srt), [Asset Manifest](ASSET_MANIFEST.md) và [Báo cáo Kỹ thuật & Animation QA](TECHNICAL_QA.md).

---

## 3. Hướng dẫn nhập và dựng trong CapCut Pro

1. **Khởi tạo Project:** Mở CapCut Pro, tạo project ngang **16:9, `1920 × 1080`, `30 FPS`**.
2. **Đặt Video Track:** Kéo file `build/EP02_pc200_8_demo_v3/CAPY-BK-EP02-PC200-8-demo.mp4` vào track `V1` tại mốc `00:00:00.000`. (Nếu muốn cân chỉnh âm lượng từng stem riêng, có thể tắt tiếng track video gốc và dùng các file WAV rời trong thư mục `audio/`).
3. **Đặt 4 Track Âm thanh riêng biệt:**
   - **Track `A1 (SIGNATURE)`:** Đặt `audio/SIGNATURE.wav` tại mốc **`00:00:00.480`** (khớp câu chào *“Kĩ Sư Ơiiii!”* của Capy trong cảnh `D01`).
   - **Track `A2 (CAPY)`:** Dành riêng cho các file WAV giọng ElevenLabs đã duyệt của Capy (`CAPY_D02.wav` tại `00:00:04.350`, `CAPY_D06.wav` tại `00:00:36.000`).
   - **Track `A3 (ENGINEER)`:** Dành riêng cho các file WAV giọng ElevenLabs đã duyệt của Anh kỹ sư (`ENGINEER_D02.wav` tại `00:00:07.200`, `ENGINEER_D03.wav` tại `00:00:10.300`, `ENGINEER_D04.wav` tại `00:00:17.500`, `ENGINEER_D05.wav` tại `00:00:24.300`, `ENGINEER_D06.wav` tại `00:00:38.900`).
   - **Track `A4 (FOLEY / MACHINE)`:** Đặt `audio/MACHINE.wav` tại mốc `00:00:00.000` (mức âm lượng gợi ý `-8 dB` đến `-6 dB` dưới giọng đọc).
4. **Nhập Phụ đề rời (`SRT`):** Vào **Text → Local Captions → Import**, chọn file `episodes/EP02/demo/EP02_demo_vi.srt`. Phụ đề hoàn toàn tách rời khỏi nền video, dễ dàng chỉnh font, viền chữ và căn lề dưới.
5. **Điều chỉnh theo giọng đọc thực tế:** Khi có bản thu ElevenLabs chính thức cho EP02, chỉ cần kéo vị trí keyframe trong `AnimationPlayer` của `demo.tscn` theo độ dài câu thoại thực tế (không ép nhanh lời thoại), rồi chạy lại lệnh Movie Maker ở mục 2.

# Asset manifest · EP02 V4 (DRAFT)

Kiểm kê ngày 2026-11-12, kế thừa V3. Repo công khai chỉ chứa lớp máy cắt từ atlas đã commit, phông công trường đã commit, mã nguồn và số liệu. Hình nhân vật EP01, cel studio và tag tiếng nằm trong `godot/local/` của gói bàn giao. Logo BK cần đối chiếu quyền sử dụng trước khi phát hành.

| Tài nguyên | Nguồn và cách tạo | Cảnh | Trạng thái |
|---|---|---|---|
| `godot/art/upper.png`, `undercarriage.png`, `boom.png`, `arm.png`, `bucket.png` | Cắt theo thành phần alpha từ `godot/art/source/pc200-parts.png` (atlas ImageGen do Codex tạo cho V2, kèm `source/PROVENANCE_codex_v2.md`) bằng `tools/prepare_layers.py`. Chốt đo bằng HoughCircles, ghi ở `parts.json`. `bucket.png` lật gương ngang. | D02–D06 | DRAFT, hình do dự án tạo |
| `godot/art/worksite.png` | Bản sao phông công trường của demo V2 (ImageGen) | D02–D06 | DRAFT |
| `godot/ink.gdshader` | Shader V4: viền mực, chia tông, giảm vân ảnh; chỉ đổi màu, giữ nguyên hình học và UV | D02–D07 | DRAFT |
| `godot/art/rig.json` | Hình học minh họa; thêm `mound_bite_baked` (vết múc đất lấy từ V3): chiều dài cần/tay gầu 5,70/2,925 m, hành trình xi lanh theo brochure K1, tọa độ chốt minh họa | Toàn bộ | Chờ reviewer |
| Xi lanh, ty, chốt, tai treo, thanh dẫn, thanh chữ H, mũi khung | Vẽ thủ tục trong `rig.gd` | D02–D06 | DRAFT |
| Động cơ, bơm, đĩa nghiêng, van, joystick, thùng, lọc, áp kế, ống dầu | Vẽ thủ tục trong `hydraulics.gd`, sơ đồ giản lược | D03–D06a | DRAFT |
| Đống đất, đất rơi, khói xả, bóng | Vẽ thủ tục trong `env.gd` | D02–D06 | DRAFT |
| `local/crew_base.png`, `capy_head.png`, `capy_collar.png`, `crew.json` | Cắt từ ảnh EP01 V7 `field-reply.png` (bản EP02 V2 cục bộ) bằng GrabCut; tách đầu Capy để xoay quanh cổ; mí mắt vẽ màu lông | D02, D05b, D06b | EP01 continuity, **thiếu lớp miệng/tay** |
| `local/studio-cels.png` | Cel studio EP01 (42 cel, 10 fps) từ bàn giao V2 | D01 | EP01 continuity |
| `local/audio/SIGNATURE.wav` | Đoạn tag từ `Capy_Ki_Su_Oiii_v2_Nhe_Tu_Nhien.mp3` của owner (bản trích của V2) | D01 | Owner đã dùng ở EP01 |
| Layer `bg/machine/hydraulics/crew/intro` | Render từng pass Godot (`-- --pass=`), alpha VP9 WebM; bg là H.264 | Toàn bộ | DRAFT |
| `MACHINE.wav` | Tổng hợp bằng `tools/make_foley_v4.py` từ `telemetry.csv`, không dùng mẫu thu | D02–D06 | DRAFT |
| CAPY / ENGINEER | Chưa có bản thu EP02 | D02–D06 | **Chờ WAV ElevenLabs owner chọn** |

Công cụ dựng: Godot 4.5.1-stable Linux x86_64 (SHA-512 `5bccbed6…85b0b9` khớp `SHA512-SUMS.txt` của bản phát hành), ffmpeg, Python 3 với OpenCV/NumPy/SciPy. Không dùng tài nguyên FuelGuard hay dữ liệu máy thật.

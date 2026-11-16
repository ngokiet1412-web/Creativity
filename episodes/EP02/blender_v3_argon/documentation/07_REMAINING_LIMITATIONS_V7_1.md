# Danh sách Những Điểm Chưa Đạt, Giả định & Giới hạn — EP02 V7.1

**Phạm vi:** EP02 V7.1 Cinematic Quality Upgrade (`build_ep02_v7_1_cinematic.py`, `materials_v7_1.py`)

---

## 1. Giới hạn Nguồn Hình học CAD & Môi trường

1. **Chưa có phần thân máy (upper structure), cabin, đối trọng và cụm di chuyển bánh xích OEM:**
   - Nguồn NX V2 chỉ cung cấp cụm công tác (`boom`, `stick`, `bucket`, `4 cylinders`, `4-bar linkage`, `13 pins`) cùng khớp gá tham chiếu `carrier_mount_reference`.
   - Trong V7.1, chân đế được nâng cấp thành **bệ thử tải dầm chữ I có gân tăng cứng và 8 bulông neo** (`Plinth_IBeam_*`, `AnchorBolt_*`) để mang tính công nghiệp thuyết phục hơn, nhưng đây **không phải** khung gầm/cabin thật của Komatsu PC200-8. Không được trình bày là xe đào nguyên chiếc.
2. **Môi trường nền studio công nghiệp thay vì công trường khai thác đầy đủ:**
   - Do giới hạn 6 GB VRAM (trong đó ~3,5 GB đang bị phần mềm nền chiếm dụng) và để giữ sự tập trung vào chuyển động cơ cấu thủy lực 18 giây, cảnh sử dụng sàn bê tông thử tải có kết cấu bump/roughness + ray đổ bóng thay cho địa hình hố đào ngoài trời nhiều cây cối/tài nguyên nặng.

## 2. Chi tiết Giả định & Minh họa Nguyên lý (Không phải Bản vẽ Shop Manual OEM)

1. **Kích thước clevis, chiều dài đóng xi lanh và bán kính chốt:** Được giữ nguyên từ hệ tham số khái niệm V2 (`geometry_v2_argon.py`), kết hợp với các kích thước chính thức công khai từ brochure Komatsu CEN00049-08 (`5700 mm`, `2925 mm`, hành trình `1334 / 1490 / 1120 mm`).
2. **Chi tiết cơ khí bổ sung trong V7.1:**
   - Gân tăng cứng hông cần, hộp chia dầu, 4 ống thép cần + 5 kẹp ống, 2 ống thép tay gầu + 3 kẹp, 6 ống mềm catenary, vòng bulông nắp chốt & cổ bít được dựng hợp lý theo nguyên lý cơ khí thủy lực nhằm nâng độ chân thực bề mặt — **không tuyên bố là vị trí part-number OEM theo số sê-ri cụ thể**.
3. **Mặt cắt xi lanh & Thông số Telemetry HUD (`8–14s`):**
   - Kết cấu bên trong mặt cắt (hai đai đồng dẫn hướng, phớt PTFE ở giữa, đai ốc hãm piston, xung sóng dầu cấp màu đỏ và dầu hồi màu xanh, cửa dầu SAE) mang tính **minh họa nguyên lý truyền động thủy lực**.
   - Trị số `Áp suất minh họa (~bar)` và vận tốc trên bảng HUD là hàm minh họa tỷ lệ từ dữ liệu quỹ đạo MATLAB `motion_trace_v3.csv`, không phải kết quả mô phỏng mạch thủy lực CLSS thực hoặc số đo cảm biến áp suất trên máy thật.

## 3. Hạng mục Chưa Thực hiện trong V7.1 (Chờ Gate Duyệt Tiếp theo)

1. **Sự khác biệt nhỏ giữa EEVEE Video và Cycles Stills:** Video 540 frame dùng `BLENDER_EEVEE` (Raytracing + AO + DOF) nên không tính `ShaderNodeNewGeometry -> Pointiness` (vốn chỉ chạy ở Cycles), do đó độ sờn cạnh sơn ở video 18s chủ yếu thể hiện qua `ShaderNodeAmbientOcclusion` + Noise hai tầng thay vì vết mòn góc nhọn như ảnh Cycles `SHOT_01..04`.
2. **Chưa có Motion Blur thật trong video:** Không bật motion blur camera để tránh làm nhòe số đọc telemetry và giữ biên khớp cơ khí sắc nét khi kiểm chứng kỹ thuật.
3. **Chưa ghép âm thanh, lồng tiếng & dựng bản EP02 đầy đủ:** Các file MP4 hiện tại là cảnh câm 18,0 giây (`1080p @ 30fps`) dành riêng cho khâu kiểm duyệt V7.1; chưa dựng toàn bộ tập EP02 và chưa merge PR #15 theo đúng lệnh Owner.
4. **Phạm vi đồng bộ GitHub (Theo yêu cầu bổ sung của Owner):** Toàn bộ mã nguồn, báo cáo, log tiến trình (`blender_v71_anim_render.log`, `gpu_vram_thermal_report_v7_1.json`), 53 file STL + 3 STEP AP214, `.blend` (`V3` & `V7_1`), 3 video `.mp4`, 4 ảnh V7.0 baseline, 4 ảnh V7.1, 4 ảnh so sánh `COMPARE_SHOT_*`, và 2 storyboard timeline đã được đẩy đầy đủ lên nhánh `argon/ep02-v7-nx-blender-cinematic` (PR #15) để các agent khác kiểm tra độc lập. Chỉ loại trừ file backup `.blend1`, `__pycache__` và 540 khung PNG thô `frames_v7_1/`.

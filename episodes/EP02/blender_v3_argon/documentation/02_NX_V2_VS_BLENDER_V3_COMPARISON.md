# Báo cáo So sánh Siemens NX V2 với Blender Cinematic V3

**Dự án:** KĨ SƯ ƠIII! / CAPY BK — EP02 V7  
**Ngày lập:** 2026-11-16

---

## 1. Bảng Đối chiếu Kỹ thuật & Mỹ thuật (NX V2 vs Blender V3)

| Tiêu chí | Siemens NX V2 (`NX_NATIVE_V2_ARGON_20261116`) | Blender Cinematic V3 (`EP02_V7_ARGON_BLENDER`) |
|---|---|---|
| **Vai trò chính** | Dựng CAD tham số gốc `.prt`, ràng buộc lắp ráp, xuất STEP AP214 & STL | Tiếp nhận trọn bộ hình học STL từ NX V2 (`0.08 mm`), nâng cấp chi tiết ngoại vi, PBR, ánh sáng & animation liên tục |
| **Phân cấp chi tiết** | 27 component instances, 11 constraints, 13 chốt `PIN_*`, 181 solid bodies | Nhập 53 file STL tách riêng theo vật liệu/chức năng vào 8 Collection độc lập; giữ nguyên toàn bộ 13 chốt & pivot gốc |
| **Độ chính xác khớp (3 tư thế tĩnh)** | `max_datum_error_mm <= 6.72e-7 mm` trên `LOW / REACH / HIGH` | Đối chiếu MATLAB: `abs_diff <= 3.935e-7 mm`; trong Blender qua 1079 trạng thái (540 khung + 539 nửa khung): `max_pin_dev_mm = 0.001066 mm`, `max_cyl_axis_err_mm = 0.000674 mm` |
| **Quỹ đạo chuyển động** | 3 tư thế rời rạc (`LOW`, `REACH`, `HIGH`) | Quỹ đạo spline C2 liên tục **18,0 giây (540 khung @ 30 fps)** qua `LOW -> REACH -> HIGH`, kiểm chứng 2161 mẫu 120 Hz (`maxFourBarErr = 9.095e-13 mm`, `zero_metal_scaling_verified = True`) |
| **Chi tiết cơ khí nâng cấp** | Có vách ngăn hộp, bạc lót, cổng SAE, ống dọc vỏ xi lanh, răng gầu, dao cắt bên | Kế thừa nguyên 100% hình học NX V2, vát mép 2 mm, tách riêng 5 răng gầu & dao cắt, bổ sung ống thép thủy lực dọc lưng cần + 4 kẹp ống, 4 ống mềm động lực nối bằng Hook, đất trong gầu, bệ thử tải & cụm **mặt cắt dọc xi lanh có piston đai đồng + 2 buồng dầu** |
| **Vật liệu & Ánh sáng** | Màu chỉ số CAD NX chuẩn | 13 vật liệu PBR thủ tục (sơn vàng có độ nhám & xước cạnh, thép tiện, ty chrome gương, gầu mòn công trường, cao su ống dầu, dầu cấp/hồi bán trong suốt), AgX + ánh sáng 3 điểm |
| **Đầu ra hình ảnh & Video** | 4 ảnh wireframe/shaded kỹ thuật viewport | 4 ảnh Cycles OPTIX `1920 × 1080` (`SHOT_01`..`SHOT_04`, ~12.5s/ảnh) + video EEVEE 540 khung `1920 × 1080 @ 30 fps` (`EP02_V7_ARGON_CINEMATIC_DEMO_18s.mp4`, `18.00s`, `11.87 MB`, `DECODE_EXIT=0`) |

---

## 2. Đối chiếu Ba Tư thế NX V2 vs MATLAB / Blender V3

| Tư thế | Cụm xi lanh | NX V2 `pose_check.csv` (mm) | MATLAB R2026b (mm) | Chênh lệch (mm) | Khoảng hở nền (mm) |
|---|---|---|---|---|---|
| `low` (22.5°, 101.0°, 56.0°) | Boom (×2) | 2772.054280 | 2772.054280 | 2.74e-07 | 83.38 |
| `low` | Arm | 2279.415532 | 2279.415532 | 1.66e-08 | 83.38 |
| `low` | Bucket | 2598.148869 | 2598.148869 | 2.89e-07 | 83.38 |
| `reach` (29.0°, 86.0°, 62.0°) | Boom (×2) | 2872.759733 | 2872.759733 | 2.58e-07 | 1006.33 |
| `reach` | Arm | 2123.675885 | 2123.675885 | 3.93e-07 | 1006.33 |
| `reach` | Bucket | 2625.563213 | 2625.563213 | 7.19e-08 | 1006.33 |
| `high` (42.0°, 105.0°, 76.0°) | Boom (×2) | 3059.807578 | 3059.807578 | 1.81e-07 | 2008.69 |
| `high` | Arm | 2321.213934 | 2321.213934 | 1.91e-07 | 2008.69 |
| `high` | Bucket | 2681.656580 | 2681.656580 | 9.11e-09 | 2008.69 |

---

## 3. Lý giải Hiện tượng Thấy trong `ARGON_V2_EXPLODED_VIEW.prt`

- File `ARGON_V2_EXPLODED_VIEW.prt` được tạo với chế độ phân rã `explode=True` dọc trục Y (`±550..1250 mm`) để trình bày rời từng xi lanh và chốt, vì vậy trông rời rạc so với mô hình lắp ráp.
- Khi lắp ráp đúng khớp trong `PC2008_WORK_EQUIPMENT_CONCEPT_ASSY.prt` (hoặc `ARGON_V2_FULL_EXCAVATOR_REACH.prt`), và khi đưa toàn bộ sub-STL sang Blender V3 (`build_ep02_v3_cinematic.py`), mọi chốt và tai liên kết khớp khít trong sai số **≤ 0,001066 mm** suốt 540 khung hình.

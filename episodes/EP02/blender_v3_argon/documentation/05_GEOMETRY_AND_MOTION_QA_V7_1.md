# Báo cáo Kiểm tra Hình học, Xi lanh & Chuyển động — EP02 V7.1

**Dự án:** KĨ SƯ ƠIII! / CAPY BK — EP02 V7.1  
**Baseline kế thừa:** PR #15 (NX V2 `NX_NATIVE_V2_ARGON_20261116` -> MATLAB R2026b `motion_trace_v3.csv` -> Blender 5.3.0)  
**Script xây dựng & kiểm tra:** `blender_project/build_ep02_v7_1_cinematic.py`  
**Kết quả JSON xác thực:** `qa/blender_vs_nx_v2_verification_v7_1.json` (`BLENDER_V71_KINEMATICS_QA_PASS`)

---

## 1. Bảo toàn Nguyên trạng Nguồn CAD NX V2 & Quỹ đạo MATLAB R2026b

- **Không sửa đổi hoặc thay thế hình học gốc:** Toàn bộ 53 file STL Binary exported từ Siemens NX 12 (`cad_exchange/stl/*.stl`, dung sai chordal `0.08 mm`) và 540 hàng quỹ đạo spline bậc 3 liên tục `C2` (`animation/motion_trace_v3.csv`) được giữ nguyên vẹn tuyệt đối.
- **Tất cả chi tiết nâng cấp cơ khí V7.1 chỉ bổ sung ngoại vi hoặc nội bộ mặt cắt minh họa**, không cắt xén hoặc biến dạng các tai gá, chốt `PIN_*`, cần Boom, tay gầu Stick, gầu Bucket, 4 xi lanh hay cơ cấu 4 khâu gốc.

## 2. Kết quả Kiểm tra 1.079 Trạng thái Liên tục trong Blender 5.3.0

Hàm `animate_secondary_effects_and_verify()` trong `build_ep02_v7_1_cinematic.py` đã giải nghiệm đồ thị phụ thuộc (`evaluated_depsgraph_get`) trên **1.079 trạng thái** gồm 540 khung hình nguyên (`1..540`, bước `1/30 s`) và 539 trạng thái giữa khung (`subframe = 0.5`):

| Chỉ tiêu Kiểm tra | Giá trị Đo thực tế (V7.1) | Ngưỡng Giới hạn (`GEOM_TOL_M`) | Kết luận |
|---|---|---|---|
| Tổng số trạng thái kiểm tra | **1.079** (540 + 539 nửa khung) | Toàn bộ 18,0 giây (`0–540`) | PASS |
| Sai lệch vị trí các chốt (`max_pin_dev_mm`) | **`0.001066 mm`** | `0.250 mm` | PASS |
| Sai lệch chiều dài các khâu (`max_link_len_err_mm`) | **`0.003477 mm`** | `0.250 mm` | PASS |
| Sai lệch đồng trục vỏ – ty 4 xi lanh (`max_cyl_axis_err_mm`) | **`0.000674 mm`** | `0.250 mm` | PASS |
| Khoảng hở gầu – sàn tối thiểu (`min_bucket_ground_clearance_mm`) | **`83.3801 mm`** | `> 0.0 mm` | PASS |
| Tỷ lệ các chi tiết kim loại (`zero_metal_scaling_verified`) | **`1.000000` (`True`)** | Không kéo giãn lưới (`1:1:1`) | PASS |

- Hành trình cả 4 xi lanh tuân thủ đúng giới hạn brochure CEN00049-08:
  - Xi lanh cần (`2 × Ø120`): `572.05 – 859.81 mm` / tối đa `1334 mm`.
  - Xi lanh tay gầu (`Ø135`): `273.68 – 471.21 mm` / tối đa `1490 mm`.
  - Xi lanh gầu (`Ø115`): `873.68 – 981.66 mm` / tối đa `1120 mm`.

## 3. Kiểm tra Các Hạng mục Cơ khí & Chuyển động Thứ cấp Mới trong V7.1

1. **Bốn đường ống thép trên cần & 2 đường ống trên tay gầu:** Gắn vào cùng node pivot `Boom_PV` / `Stick_PV`, kèm kẹp ống bu-lông và khối chia dầu `Boom_Hydraulic_JunctionBox` (`BEVEL` 2 đoạn, không xuyên lấn mặt thép).
2. **Vòng bu-lông M20/M36:**
   - Gắn trên mặt bích cổ bít (`Gland`) của 4 xi lanh (`boom_l`, `boom_r`, `arm`, `bucket`), trên nắp giữ 4 chốt chính (`PIN_BOOM_BASE`, `PIN_BOOM_TIP`, `PIN_STICK_TIP`, `PIN_ARM_CYL_A`), trên cổ bít `Exploded_05_Gland_Seal_Collar` (`SHOT_03`), và 8 bulông neo M36 trên tấm đế `Plinth_SolePlate`.
3. **Sáu ống mềm thủy lực 3D (`create_catenary_hose`):**
   - Trong bản V7.1 chính thức, đã loại bỏ `HookModifier` (vốn gây nhân đôi ma trận làm đầu ống lệch trong bản thử nghiệm đầu tiên) và thay bằng **keyframe trực tiếp 3 điểm Bezier + vector tiếp tuyến theo ma trận world thực (`evaluated_get(depsgraph).matrix_world`) qua toàn bộ 540 khung hình**.
   - Hai đầu ống luôn bám chính xác **`0.00 mm`** vào các đầu bấm kim loại (`Ferrule_Start`, `Ferrule_End`), điểm giữa võng catenary dao động quán tính có tắt dần theo vận tốc cần `boom_vel_mms / 22.0`.
4. **Hiệu ứng đất rời thứ cấp (`Falling_Soil_Clod_01..14`):**
   - 14 viên đất đá nhả tuần tự khỏi mép gầu từ `0.35 s` đến `3.3 s`, rơi theo phương trình đạn đạo trọng trường (`g = 9.81 m/s²`) và dừng tiếp xúc đúng tại cao độ mặt sàn `GROUND_Z_M + 0.028 m`.
5. **Mặt cắt xi lanh & Telemetry động (`8–14s`, Khung `240–420`):**
   - Vỏ xi lanh phải chuyển mượt sang mặt cắt để lộ hai buồng dầu đỏ/xanh có xung sóng `ShaderNodeTexWave` đồng bộ trực tiếp theo độ dãn ty (`delta_ext_m * 10.5`), hai vòng đai dẫn hướng bằng đồng + phớt PTFE + đai ốc hãm piston.
   - Xác minh trực quan tại các khung `ep02_v71_0260.png` (`A-B: 2,934 mm | Ty đi ra: 734 / 1,334 mm | 21.4 mm/s | ~210 bar`) và `ep02_v71_0380.png` (`A-B: 3,015 mm | Ty đi ra: 815 / 1,334 mm | 17.7 mm/s | ~203 bar`): thông số HUD và thanh tiến trình thay đổi chính xác theo từng khung hình.

# Bản ghi Quy trình Chuyển đổi Siemens NX 12 (V2) sang Blender 5.3.0 (V3)

**Dự án:** KĨ SƯ ƠIII! / CAPY BK — EP02 V7  
**Đối tượng:** Cơ cấu công tác máy đào kiểu Komatsu PC200-8  
**Ngày thực hiện:** 2026-11-16

---

## 1. Kiểm kê & Bảo toàn Nguồn NX V2 (`source_nx_v2/`)

- **Nguồn V2:** `D:\Creativity_CAPY_BK_EP01_Assets_For_Codex\CAPY_BK_EP02_NX_CODEX_PILOT\NX_NATIVE_V2_ARGON_20261116\` (và bản nén `NX_NATIVE_V2_ARGON_20261116.zip` hiện diện cạnh thư mục gốc).
- **Script kiểm kê:** `source_nx_v2/inventory_nx_v2.py` -> xuất `source_nx_v2/nx_v2_inventory.json`.
- **Thành phần kiểm kê (không chỉnh sửa bất kỳ file gốc V2 nào):**
  - 32 file `.prt` native chuẩn (bao gồm 4 Component Assembly `PC2008_WORK_EQUIPMENT_CONCEPT_ASSY*.prt`, 4 multibody placed-solids/exploded `.prt`, 13 part riêng và 11 chốt cơ khí `pin_R*_L*.prt`).
  - 8 file bản sao tách tên `ARGON_V2_*.prt` để mở song song trong NX GUI mà không trùng `Leaf`.
  - 3 file STEP AP214 (`PC2008_LOW_AP214.step`, `PC2008_REACH_AP214.step`, `PC2008_HIGH_AP214.step`).
  - 4 bảng CSV thông số & tọa độ chốt (`assembly_params.csv`, `joint_map.csv`, `pose_check.csv`, `pin_verification_v2.csv`).
  - 6 file audit/log (`feature_tree_audit_v2_argon.json`, `native_reopen_v2_argon.log`, `nx_run_v2_argon.log`, v.v.).

---

## 2. Quy trình Tách Lưới Trung gian từ Siemens NX 12 (`cad_exchange/`)

Do Blender 5.3.0 không hỗ trợ nhập trực tiếp file `.prt` hoặc `.step` mặc định nếu không dùng addon ngoài chưa audit, pipeline sử dụng trực tiếp API **NXOpen `DexManager.CreateStlCreator()`** thông qua `C:\Program Files\Siemens\NX 12.0\NXBIN\run_journal.exe`.

- **Script tái chạy:** `cad_exchange/export_nx_v2_parts_for_blender.py`
- **Thông số tessellation:** Binary STL, đơn vị `mm`, `ChordalTol = 0.08 mm`, `AdjacencyTol = 0.025 mm`, `AutoNormalGen = True`.
- **Chiến lược tách sub-mesh trực tiếp từ cây Feature NX 12 (`feature.GetBodies()`):**
  - Kiểm tra phân hoạch 1-1 toàn bộ solid bodies (tổng số body xuất ra bằng đúng số `IsSolidBody` trong từng `.prt`, không sót hay trùng body).
  - Tổng cộng **53 file Binary STL** (`52.746` tam giác sub-mesh), tách riêng:
    - `carrier_mount_reference.stl` (7 bodies, 2.680 tam giác)
    - `boom_structure.stl` (8 bodies) & `boom_bosses.stl` (8 bodies)
    - `stick_structure.stl` & `stick_bosses.stl` (14 bodies)
    - `bucket_shell.stl`, `bucket_wear_edges.stl`, `bucket_teeth.stl` (21 bodies tách riêng 5 răng gầu rèn)
    - 3 cụm vỏ xi lanh tách riêng `*_body.stl`, `*_gland.stl`, `*_ports.stl`
    - 3 cụm ty piston tách riêng `*_chrome.stl`, `*_piston.stl`, `*_eye.stl`
    - `side_link_body/bosses.stl`, `h_link_body/bosses.stl`, và đủ 11 file chốt `pin_*.stl` + `pivot_pin.stl`.
- **Manifest kiểm chứng:** `cad_exchange/cad_exchange_manifest.json`.

---

## 3. Tính toán & Kiểm chứng Quỹ đạo MATLAB R2026b (`animation/`)

- **Script:** `animation/solve_ep02_v3_motion.m` (chạy trên MATLAB R2026b `26.2.0.3386108`, license Trial).
- **Đối chiếu 3 tư thế tĩnh NX V2 (`LOW`, `REACH`, `HIGH`):**
  - `nx_v2_max_pin_distance_diff_mm = 3.935e-7 mm`
  - `nx_v2_max_joint_coord_diff_mm = 6.717e-7 mm`
- **Quỹ đạo liên tục 18.0 giây (540 khung @ 30 fps + kiểm chéo 2161 mẫu @ 120 Hz):**
  - Dùng nội suy đường cong spline bậc 3 giữ đạo hàm bậc 1 bằng 0 tại đầu/cuối (`spline` C2 clamped) đi qua `LOW (0s)` → `REACH (5.8s)` → `HIGH (16.8–18.0s)`.
  - Dải hành trình: Boom `572.05–859.81 mm` (giới hạn `1334`), Arm `273.68–471.21 mm` (giới hạn `1490`), Bucket `873.68–981.66 mm` (giới hạn `1120`).
  - Sai số khép vòng 4 khâu lớn nhất: `9.095e-13 mm`. Khoảng hở gầu–nền tối thiểu: `83.38 mm`.

---

## 4. Nhập lưới, Quy đổi Tỷ lệ & Rigging trong Blender 5.3.0 (`blender_project/`)

- **Script tổng hợp:** `blender_project/build_ep02_v3_cinematic.py`
- **Xử lý đơn vị & bình pháp tuyến:**
  - Áp ma trận co giãn `Matrix.Scale(0.001, 4)` **trực tiếp lên đỉnh mesh** (`1 mm = 0.001 m`) thay vì giữ `obj.scale = (0.001, 0.001, 0.001)`, giúp `obj.scale = (1, 1, 1)` chuẩn xác và modifier `BEVEL (width = 0.002 m)` tạo vát cạnh `2 mm` đúng kích thước thật.
  - Xóa đỉnh trùng ở ngưỡng `1e-5 m`, đánh dấu cạnh sắc ở góc nhị diện `> 32°`, bật `EDGE_SPLIT` theo cạnh sắc để giữ khối trụ mạ chrome trơn mịn không loang bóng.
- **Hệ tọa độ & Quy ước góc quay:**
  - NX và Blender dùng chung hệ trục phải `+X` tiến về gầu, `+Y` sang trái máy, `+Z` hướng lên, gốc `(0, 0, 0)` tại tâm chốt chân cần (`BOOM_BASE`).
  - Phép quay `rotate((x, z), deg)` trong `geometry_v2_argon.py` tương ứng góc quay Euler quanh `+Y` của Blender là `-radians(deg)`.
  - Bốn xi lanh và hai thanh liên kết gầu sử dụng ràng buộc `LOCKED_TRACK` (`track_axis='TRACK_X'`, `lock_axis='LOCK_Y'`) giúp ty piston và vỏ xi lanh luôn trượt đồng trục trong mặt phẳng XZ, không xoắn trục hay kéo giãn lưới kim loại.

---

## 5. Kết quả Render Nghiệm thu (4 Ảnh Tĩnh + Video Demo 18s)

- **4 Ảnh tĩnh 1920 × 1080 (Cycles OPTIX 64 samples + Denoising trên RTX A3000 GPU):**
  - `renders/SHOT_01_HERO_MECHANICAL_ASSEMBLY.png` (`12.15 s`)
  - `renders/SHOT_02_HYDRAULIC_CYLINDER_CLOSEUP.png` (`13.68 s`)
  - `renders/SHOT_03_EXPLODED_ENGINEERING_VIEW.png` (`10.62 s`)
  - `renders/SHOT_04_CUTAWAY_XRAY.png` (`13.77 s`)
- **Video Demo 540 khung 1920 × 1080 @ 30 fps (Blender EEVEE 24 samples + Raytracing):**
  - Render 540 khung hình `ep02_v3_0001.png`..`ep02_v3_0540.png` hoàn tất trong `505.13 s`.
  - Đóng gói FFmpeg (`libx264 -crf 16 -pix_fmt yuv420p`) thành `renders/EP02_V7_ARGON_CINEMATIC_DEMO_18s.mp4`:
    - Thời lượng: `00:00:18.00`, `1920x1080`, `30 fps`, bitrate `5272 kb/s`, dung lượng `11.869.604 bytes`.
    - Kiểm tra giải mã toàn bộ 540 khung (`ffmpeg -v error -i ... -f null -`): `exit code = 0`.


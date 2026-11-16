# Báo cáo GPU, VRAM, Nhiệt độ & Thời gian Render — EP02 V7.1

**Thiết bị thử nghiệm:** Dell Precision 7560 — **NVIDIA RTX A3000 Laptop GPU (6.144 MiB VRAM)** / 32 GB RAM  
**Phiên bản Blender:** 5.3.0  
**Dữ liệu log đầy đủ:** `qa/gpu_vram_thermal_report_v7_1.json` (lấy mẫu `nvidia-smi` mỗi 2,0 giây trong toàn bộ 540 khung hình)

---

## 1. Giải đáp Câu hỏi của Owner về Mức Sử dụng GPU Giữa Bước Thử nghiệm & Render Thật

Trong phiên trước khi chạy `build_ep02_v7_1_cinematic.py --mode stills`, hệ thống **mới chỉ**:
1. Chạy bài toán kiểm tra động học 1.079 trạng thái trên CPU.
2. Biên dịch nhân shader OptiX mới trên CPU (khi bật `ShaderNodeAmbientOcclusion` + `Compositor`).
3. Render **4 ảnh tĩnh đơn lẻ (`SHOT_01..04_V7_1.png`)** mất 11–16 giây/ảnh rồi kết thúc tiến trình Blender.

Vì vậy tải GPU ở bước đó chỉ xuất hiện thoáng qua vài chục giây và nhìn có vẻ "ít tốn tài nguyên" hơn lúc render cả 540 frame video V7.0. Bản V7.1 thực chất **nặng và chi tiết hơn V7.0** (bổ sung `ShaderNodeAmbientOcclusion` + `Pointiness`, Depth of Field, `CompositorNodeGlare`, 48 bulông, bệ dầm I-beam, 6 ống mềm catenary 540 frame, 14 viên đất rơi, và xung sóng dầu 3D).

---

## 2. Kết quả Đo Đạc Thực tế 4 Ảnh Tĩnh Cycles OPTIX GPU (`1920 × 1080`, 72 Samples + Denoise)

*Đo sau khi sửa 4 lỗi thị giác V7.1 (`task-660`, bộ nhớ đệm OptiX đã ấm):*

| Ảnh Nghiệm thu | Engine & Cài đặt | Thời gian Render (giây) | Khung hình |
|---|---|---|---|
| `SHOT_01_V7_1.png` (Hero 3/4 Assembly) | Cycles GPU OPTIX · 72 spp + Adaptive `0.015` | **13.65 s** | Khung `175` |
| `SHOT_02_V7_1.png` (Cylinder & Chrome Close-Up) | Cycles GPU OPTIX · 72 spp + Adaptive `0.015` | **15.98 s** | Khung `175` |
| `SHOT_03_V7_1.png` (Exploded Engineering View) | Cycles GPU OPTIX · 72 spp + Adaptive `0.015` | **11.90 s** | Khung `175` |
| `SHOT_04_V7_1.png` (Cutaway X-Ray Principle) | Cycles GPU OPTIX · 72 spp + Adaptive `0.015` | **14.79 s** | Khung `331` |

- Tổng thời gian dựng cảnh + kiểm tra 1.079 trạng thái + lưu `.blend` + render 4 ảnh: **`~67 giây`**.

---

## 3. Kết quả Đo Telemetry GPU Liên tục cho Toàn bộ 540 Khung Hình Video (`task-698`)

- **Engine Animation:** `BLENDER_EEVEE` (Raytracing ON, `ShaderNodeAmbientOcclusion`, `taa_render_samples = 32`, Depth of Field, `CompositorNodeGlare Fog Glow`)
- **Độ phân giải & Tốc độ:** `1920 × 1080 @ 30 fps` (**540 / 540 khung hình hoàn tất**, exit code `0`)
- **Tổng thời gian Wall Time (dựng + QA + render 540 PNG):** **`808.52 giây`** (`~13 phút 28,5 giây`, trung bình `~1.50 s/khung`)
- **Số lần lấy mẫu `nvidia-smi`:** `393` mẫu tổng cộng (`386` mẫu trong pha render tích cực)

| Chỉ số Phần cứng (`NVIDIA RTX A3000 Laptop GPU`) | Idle nền (trước render) | Tối thiểu (khi render) | Trung bình (khi render) | Tối đa (khi render) | Sau render |
|---|---|---|---|---|---|
| **GPU Utilization (%)** | `0.0%` | `0.0%` | **`78.98%`** | **`99.0%`** | `0.0%` |
| **VRAM Used (MiB / 6144 MiB)** | `3,583 MiB` *(có sẵn NX + Blender GUI của Owner)* | `3,850 MiB` | **`4,990.59 MiB`** | **`5,618.0 MiB`** *(còn dư `526 MiB`)* | `3,509 MiB` |
| **Nhiệt độ GPU (°C)** | `61.0°C` | `68.0°C` | **`75.04°C`** | **`77.0°C`** | `71.0°C` |
| **Công suất (W)** | `31.93 W` | `65.36 W` | **`78.79 W`** | **`89.86 W`** | `38.96 W` |
| **Xung nhịp SM (MHz)** | `1,560 MHz` | `1,425 MHz` | **`1,578.11 MHz`** | **`1,740.0 MHz`** | `1,740 MHz` |

### Nhận xét Tối ưu Phần cứng:
- Vì máy đang mở song song Siemens NX và Blender GUI của Owner chiếm sẵn ~3,5 GB VRAM nền, cấu hình V7.1 chọn `BLENDER_EEVEE` Raytracing 32 TAA samples cho chuỗi 540 frame giúp giữ đỉnh VRAM ở **`5,618 / 6,144 MiB`** (tránh tràn VRAM xuống RAM hệ thống hoặc lỗi driver), nhiệt độ ổn định **`75–77°C`**, trong khi ảnh tĩnh hero vẫn khai thác tối đa **Cycles OPTIX** ở chất lượng 72 mẫu.
- Nếu cần render toàn bộ 540 frame bằng Cycles OPTIX trực tiếp ở các bước sản xuất cuối sau này, nên đóng các ứng dụng 3D nặng chạy nền để giải phóng ~2–3 GB VRAM trước khi chạy.

---

## 4. Thông số Đóng gói Video FFmpeg 7.1

1. **`renders/EP02_V7_1_CINEMATIC_DEMO_18s.mp4`**:
   - Codec: `H.264 High`, `yuv420p`, `CRF 15`, `+faststart`, `1920 × 1080`, `30 fps`, `18.00 s`
   - Bitrate: `6,449 kb/s` · Dung lượng: **`14,518,261 bytes` (`~13.85 MiB`)** · Kiểm tra `ffmpeg -v error`: exit `0`.
2. **`renders/EP02_V7_0_VS_V7_1_COMPARISON_18s.mp4`**:
   - Video so sánh đồng bộ từng khung hình (`hstack` `V7.0` bên trái vs `V7.1` bên phải), `1920 × 1080`, `30 fps`, `18.00 s`
   - Bitrate: `3,068 kb/s` · Dung lượng: **`6,911,396 bytes` (`~6.59 MiB`)** · Kiểm tra `ffmpeg -v error`: exit `0`.

# Danh mục Nguồn Tài liệu, Phần mềm & Giấy phép (EP02 V7 Blender V3)

**Dự án:** KĨ SƯ ƠIII! / CAPY BK — EP02 V7  
**Cam kết IP & Bảo mật:** Không tải model CAD thương mại trả phí, không cài addon/MCP bên thứ ba, không đưa dữ liệu FuelGuard hoặc CAD có ràng buộc bản quyền lên GitHub công khai.

---

## 1. Tài liệu & Thông số Kỹ thuật

| Hạng mục | Nguồn / Đường dẫn | Trạng thái / Phạm vi sử dụng |
|---|---|---|
| Thông số công bố họ Komatsu PC200-8 / PC200LC-8 (`S01 CEN00049-08`) | Tài liệu công khai `PC200-8_PC200LC-8.pdf` (tham chiếu trong `CAD_SOURCE_REGISTER_PC2008.md` và `V7_ENGINEERING_CINEMATIC_MASTERPLAN.md`) | Dùng cho chiều dài cần (`5700 mm`), tay gầu (`2925 mm`), đường kính xi lanh (`Ø120/135/115`), đường kính ty (`Ø85/95/80`), hành trình xi lanh (`1334/1490/1120 mm`). |
| Nguồn CAD Concept V2 (`NX_NATIVE_V2_ARGON_20261116`) | Do Argon kế thừa và hoàn thiện từ Codex V1 trên workspace cục bộ | Lưu cục bộ; file `.prt`, `.step`, `.blend`, `.stl` không đưa lên repo công khai nếu có quy định lưu trữ riêng. |

---

## 2. Công cụ Phần mềm Đã Dùng (Toàn bộ có sẵn trên máy Owner)

| Phần mềm | Phiên bản kiểm thực tế | Vai trò & Ghi chú License |
|---|---|---|
| **Siemens NX** | `v12.0.0.27` (`C:\Program Files\Siemens\NX 12.0\NXBIN\run_journal.exe`) | Đọc file `.prt` V2 bằng NXOpen Python API và tessellate thành 53 Binary STL (chỉ giữ kết xuất cục bộ). |
| **MATLAB** | `R2026b (26.2.0.3386108)` (`matlab.exe -batch`) | Chạy giải quỹ đạo spline 18s (540 khung @ 30fps, kiểm 2161 mẫu @ 120Hz) và xuất biểu đồ QA. Máy báo `Trial License -- for use to evaluate programs...`. |
| **Blender** | `5.3.0` (`hash 02f0899d78e3`, GPU `NVIDIA RTX A3000 Laptop GPU 6 GB`) | Giấy phép **GNU GPL v3+**. Toàn bộ vật liệu PBR, ống dầu, mặt cắt, đèn và animation được tạo hoàn toàn bằng **Python API + Shader Nodes tích hợp sẵn**, không dùng addon hay asset trả phí bên ngoài. |
| **FFmpeg** | `ffmpeg-win-x86_64-v7.1.exe` (từ `D:\Creativity_CAPY_BK_EP01_Assets_For_Codex\.capy-tools`) | Đóng gói chuỗi ảnh PNG 1080p thành video `MP4 H.264` và kiểm tra giải mã không lỗi. |

---

## 3. Tài sản 3D / Vật liệu Bổ sung (Tự tạo bằng Mã nguồn mở)

- Toàn bộ 13 vật liệu PBR (sơn vàng công nghiệp đa lớp, thép kết cấu, ty mạ chrome, thép chốt tiện bóng, gầu mòn công trường, cao su ống thủy lực, mặt cắt sơn cam kỹ thuật, dầu cấp/hồi bán trong suốt, đất công trường, sàn bãi thử) được sinh **100% thủ tục (procedural Shader Nodes)** trong `textures_materials/materials_v3.py`, không sử dụng bất kỳ texture map hay mô hình 3D tải từ nguồn bên ngoài nào.
- Chữ chú thích trong cảnh mặt cắt sử dụng font hệ thống mặc định của Blender (`Bfont`) với nhãn tiếng Việt thuần kỹ thuật.

# Danh sách Lỗi Đã Khắc phục, Điểm Giả định & Phần Chưa Hoàn thành

**Dự án:** KĨ SƯ ƠIII! / CAPY BK — EP02 V7  
**Phạm vi kiểm tra:** Giai đoạn chuyển đổi NX V2 → MATLAB R2026b → Blender 5.3.0 (V3)

---

## 1. Giải thích hiện tượng "Assembly rời rạc" trên ảnh NX GUI (`ARGON_V2_EXPLODED_VIEW.prt`)

- Trong phiên trước, khi mở file **`ARGON_V2_EXPLODED_VIEW.prt`** trong Siemens NX 12 GUI, người dùng nhìn thấy các xi lanh và chốt bị đẩy tách ra xung quanh cần và tay gầu.
- **Nguyên nhân:** File `ARGON_V2_EXPLODED_VIEW.prt` (sao chép từ `PC2008_REACH_EXPLODED_VIEW.prt`) là **bản vẽ phân rã minh họa (Exploded View)**, được sinh ra với `explode=True` (tách các xi lanh nâng cần ra `±1250 mm`, xi lanh tay gầu/gầu ra `750 mm`, thanh liên kết `±550 mm` và 13 chốt ra `±900 mm` dọc theo trục Y để nhìn rõ từng chi tiết không bị che khuất).
- **Bản lắp ráp liền khối đúng vị trí khớp:** Để xem bộ máy lắp ráp khớp khít tại đúng 13 chốt trong NX 12, mở **`ARGON_V2_FULL_EXCAVATOR_REACH.prt`** hoặc assembly **`PC2008_WORK_EQUIPMENT_CONCEPT_ASSY.prt`** (đồng thời tránh mở đè khi tab V1 cùng tên đang mở trong bộ nhớ NX, hoặc chạy `nx_ui_preview_v2_argon.py` đã sửa lỗi `CloseAll`).

---

## 2. Những điểm còn giả định / minh họa nguyên lý (KHÔNG phải bản vẽ OEM PC200-8)

Tuân thủ quy tắc trung thực kỹ thuật của dự án, các hạng mục sau **KHÔNG được tuyên bố là thông số OEM chính hãng của máy đào Komatsu PC200-8 cụ thể**:

1. **Kích thước brochure đã xác minh công khai (CEN00049-08):**
   - Chiều dài cần `5700 mm`, tay gầu `2925 mm`, số lượng & hành trình xi lanh cần (`2 × Ø120 × 1334 mm`, ty `Ø85`), tay gầu (`1 × Ø135 × 1490 mm`, ty `Ø95`), gầu (`1 × Ø115 × 1120 mm`, ty `Ø80`).
2. **Thông số giả định khái niệm (`ASSUMED-PARAM / CONCEPT`):**
   - Tọa độ X-Z các tai gá xi lanh trên thân, cần, tay gầu và gầu (`JOINTS` trong `geometry_v2_argon.py`), kích thước bốn khâu `650 mm / 750 mm`, chiều dài đóng của các xi lanh (`2200 / 1850 / 1700 mm`), đường kính và chiều dài chốt (`pin_verification_v2.csv`).
   - Kết cấu bên trong mặt cắt xi lanh (`SHOT_04` và `8–14s` của video): độ dày đai đồng dẫn hướng piston, vị trí phớt Viton, cổng dầu SAE trên vỏ xi lanh và đường ống mềm nối về khối phân phối là **minh họa nguyên lý làm việc thủy lực**, không phải bản vẽ kết cấu nội bộ hoặc sơ đồ thủy lực CLSS theo số serial cụ thể của Komatsu.
   - Đường áp suất `p_boom_illustrative_bar` trong `motion_trace_v3.csv` là hàm minh họa tỷ lệ thuận với cánh tay đòn và tốc độ nâng cần, không phải số liệu đo đạc thực địa hay mô phỏng mạch bơm van thực. Lưu lượng `Q = A · v` được tính lý tưởng hóa từ tiết diện hình học xi lanh nhân tốc độ trượt ty (`m³/s → L/min`).
3. **Phần thân máy & hệ di chuyển chưa có CAD:**
   - Dữ liệu NX V2 chỉ dựng **cụm công tác (cần – tay gầu – gầu – xi lanh – cơ cấu 4 khâu – 13 chốt)** và khung gá chữ A (`carrier_mount_reference`).
   - Để không tự bịa thân máy hay xích di chuyển thô sơ rồi nhận là PC200-8 hoàn chỉnh, scene Blender V3 gắn cụm công tác lên **bệ thử tải kết cấu công nghiệp (`Test_Plinth_*`)** đặt trên mặt sàn bãi thử tại đúng cao độ `GROUND_Z = -1584.9 mm`.

---

## 3. Công việc còn lại cho các bước sau (MATLAB / ANSYS / Production EP02)

1. **Tích hợp âm thanh, giọng đọc & Capy 2D (Gate G5/G6):** Bản Blender demo 18s hiện ở dạng video im tiếng 1080p @ 30fps, cần ghép với WAV giọng đọc kỹ sư/Capy đã duyệt, SFX thủy lực và phụ đề SRT trong CapCut Pro.
2. **ANSYS FEA (Gate G3 — tùy chọn):** Nếu owner muốn kiểm tra ứng suất cục bộ một chốt hoặc tai gầu, cần bổ sung mác thép chính thức, tải trọng thiết kế và điều kiện biên thực.
3. **Bản quyền & kiểm tra thực địa:** Cần bản vẽ shop manual / đo đạc trực tiếp trên máy thật nếu muốn công bố kích thước chốt, cổng dầu hoặc cấu hình CLSS chi tiết theo serial.

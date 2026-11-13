# Báo cáo Audit Kỹ thuật PC200-8 & Kiểm thử Chuyển động V3

**DRAFT · Kiểm tra nội bộ ngày 2026-11-12 (Bản nâng cấp V3 theo `ANIMATION_QUALITY_V3_BRIEF.md`).**
Phạm vi minh họa của bản Demo (42 giây) và bản Proof QA (16 giây) bao quát chuỗi truyền công suất từ động cơ diesel `SAA6D107E-1`, cụm bơm piston đĩa nghiêng thay đổi lưu lượng, hệ điều khiển `HydrauMind / CLSS` với tay trang `PPC`, đến phối hợp cơ cấu đa khớp (`Cần – Tay gầu – Gầu` xúc đất, nâng tải và giữ tải khi van về vị trí trung gian) cùng nhánh hồi qua két làm mát và lọc về thùng dầu. Toàn bộ sơ đồ nguyên lý luôn gắn nhãn rõ: **`"Sơ đồ giản lược · Chi tiết theo số sê-ri và cấu hình máy"`**.

---

## 1. Nguồn tài liệu kỹ thuật Komatsu PC200-8 đã đối chiếu (Giai đoạn 1 — Audit)

- **K1 · Brochure Komatsu PC200-8 / PC200LC-8 (`CEN00049-08`, mục Specifications):**
  - Động cơ: **Komatsu SAA6D107E-1**, 6 xi lanh, dung tích `6,69 L`, công suất bánh đà tịnh (**net horsepower**) **110 kW (148 HP) tại 2.000 rpm**.
  - Hệ thủy lực **HydrauMind (CLSS — Closed-center Load Sensing System)** với các van bù áp (**pressure compensation valves**) và van cảm nhận tải (**load-sensing valves**).
  - Bơm chính: Bơm piston kiểu đĩa nghiêng thay đổi lưu lượng (**variable displacement piston type**), lưu lượng cực đại danh định **439 L/phút**.
  - Mô tơ công tác: 1 mô tơ quay toa piston hướng trục có phanh giữ quay; 2 mô tơ di chuyển piston hướng trục có van phanh.
  - Áp suất cài đặt van giới hạn danh định (**relief valve settings**): Mạch công tác (**implement**) **37,3 MPa (380 kgf/cm²)**; mạch di chuyển (**travel**) **37,3 MPa**; mạch quay toa (**swing**) **28,9 MPa (295 kgf/cm²)**; mạch điều khiển (**pilot**) **3,2 MPa (33 kgf/cm²)**.
  - Kích thước xi lanh nâng cần (**boom cylinder**, 2 chiếc): Đường kính lòng **120 mm × đường kính ty 85 mm × hành trình 1.334 mm**.
- **K2 · Brochure Komatsu PC200-8 (`AESS688-01`):** Đối chiếu chéo thông số `SAA6D107E-1` (`110 kW @ 2.000 rpm`) và lưu lượng cụm bơm chính `439 L/phút`.
- **K3 · Shop Manual Komatsu PC200/220-8 (`SEN00084-03`, gồm `SEN00099` và `SEN00100`):**
  - Xác nhận cấu trúc hệ thống CLSS, van điều khiển chính, tín hiệu cảm nhận tải `LS`, van bù áp, van chống trôi cần (**boom drift prevention / holding valve** khóa dầu đầu đáy khi tay trang về giữa), khớp quay trung tâm (**center swivel joint**), mạch hồi qua két làm mát (**oil cooler**) và lọc hồi (**return filter**) về thùng dầu.
- **K4 · Chỉ mục bản vẽ mạch thủy lực `SEN00112-03`:** Tách biệt theo dải số sê-ri và cấu hình máy. Không sử dụng thông số của `PC200-8M0` (vốn dùng động cơ `SAA6D107E-1` ở mức công suất/điều khiển khác hoặc cấu hình đời sau) làm thông số mặc định của `PC200-8`.

---

## 2. Bảng đối chiếu 10 nội dung kỹ thuật bắt buộc & các chi tiết cần bản vẽ theo số sê-ri

| TT | Hạng mục kỹ thuật | Đã xác minh & thể hiện trong Demo V3 | Chi tiết phụ thuộc số sê-ri / cần xác nhận thêm cho tập dài |
|---|---|---|---|
| 1 | **Động cơ diesel SAA6D107E-1** | 6 xi lanh thẳng hàng, `6,69 L`, `110 kW (148 HP) @ 2.000 rpm` (K1). Minh họa 6 piston chuyển động theo thứ tự nổ `1-5-3-6-2-4` và trục truyền mô-men sang bơm. | Chi tiết đường nhiên liệu/khí nạp bên trong động cơ (không thuộc trọng tâm thủy lực). |
| 2 | **Cụm bơm thủy lực chính & cơ cấu đổi lưu lượng** | Bơm piston hướng trục đĩa nghiêng thay đổi lưu lượng, tổng lưu lượng cực đại `439 L/phút` (K1/K2). Minh họa góc nghiêng đĩa nghiêng $\alpha$ thay đổi hành trình piston theo cụm servo và tín hiệu `LS`. | Ký hiệu mã cụm bơm chi tiết (`HPV95+95` tandem) và đồ thị đặc tuyến $P-Q$ theo từng chế độ làm việc (`P, E, L, B`). |
| 3 | **Hệ thống HydrauMind, CLSS, cảm nhận tải & bù áp** | Mạch tâm kín cảm nhận tải (`CLSS`), nhánh phản hồi áp suất tải `LS` (màu tím) về bộ điều chỉnh bơm và cụm van bù áp giữ chia lưu lượng ổn định khi phối hợp nhiều thao tác (K1/K3). | Giá trị chênh áp điều khiển $\Delta P_{\text{LS}}$ danh định và chi tiết tiết diện rãnh bù áp theo từng cụm spool. |
| 4 | **Điều khiển joystick, mạch pilot & van phân phối** | Tay trang `PPC` cấp áp suất điều khiển pilot màu cam (`3,2 MPa` danh định) đẩy con trượt chính tỉ lệ với hành trình gạt tay trang, mở đường cấp `P → A` và đường hồi `B → T` (K1/K3). | Sơ đồ đánh số cổng pilot cụ thể trên vỏ van phân phối theo dải số sê-ri trong `SEN00112-03`. |
| 5 | **Xi lanh nâng cần, tay gầu và gầu** | Cặp xi lanh cần `120 × 85 × 1334 mm` (K1). Trong V3, cả **3 cụm xi lanh** (xi lanh cần, xi lanh tay gầu, xi lanh gầu + cơ cấu 4 khâu) đều hoạt động thực sự và dẫn động các khâu cứng quay quanh chốt. | Kích thước lòng/ty xi lanh tay gầu và gầu theo từng tùy chọn chiều dài tay gầu (`2,4 m / 2,9 m`) trong brochure K1. |
| 6 | **Mô tơ quay toa & bộ truyền giảm tốc** | Đã xác nhận 1 mô tơ piston hướng trục + hộp giảm tốc hành tinh + phanh giữ quay toa, áp giới hạn `28,9 MPa` (K1/K3). Đã lên kịch bản chi tiết trong `SCRIPT_YOUTUBE_PC200_8_FULL_V2.md`. | Dựng hoạt cảnh mặt cắt giảm tốc hành tinh và van chống giật quay toa ở Giai đoạn 4 (Full production). |
| 7 | **Hai mô tơ di chuyển & khớp quay trung tâm** | Đã xác nhận 2 mô tơ piston hướng trục có phanh + khớp quay trung tâm (**center swivel joint**) dẫn dầu từ khung trên xuống gầm xích, áp giới hạn `37,3 MPa` (K1/K3). | Dựng hoạt cảnh đường dầu qua lõi/vỏ khớp quay trung tâm ở Giai đoạn 4. |
| 8 | **Dầu hồi, lọc, làm mát & thùng dầu** | Đã minh họa trực tiếp trong cảnh `D06` (và Beat 4 của Proof 16s): dòng dầu hồi màu xanh đi qua **Két làm mát dầu (Oil Cooler) → Lọc hồi (Return Filter) → Thùng dầu thủy lực** (K3). | Chi tiết áp suất mở van bypass lọc hồi và van kiểm tra áp lưng mạch hồi. |
| 9 | **Các van bảo vệ, giới hạn áp suất & giữ tải** | Hiển thị rõ trị số van giới hạn áp suất mạch công tác `37,3 MPa` và minh họa **van khóa giữ cần (boom holding / drift prevention valve)** đóng kín giữ nguyên độ cao cần (`L_boom = 318,2`) khi van về giữa (K1/K3). | Chi tiết cấu tạo bên trong van chống trôi cần và van hút bù chống xâm thực (**suction safety valve**). |
| 10 | **Liên hệ Động cơ – Bơm – Lưu lượng – Áp suất – Tốc độ** | Nhấn mạnh xuyên suốt trong `D03–D06`: Động cơ cấp công suất cơ học $\rightarrow$ Bơm tạo **lưu lượng $Q$** quyết định tốc độ xi lanh ($v \approx Q/A$) $\rightarrow$ **Áp suất $p$** sinh ra do sức cản của tải ($F = p \cdot A$) và bị chặn trên bởi van an toàn. | Biểu đồ giảm lưu lượng theo đường cong công suất không đổi khi tải đạt cực đại ở Giai đoạn 4. |

---

## 3. Kiểm thử Chuyển động, Động học Cơ cấu & Chống Đứng Hình (Animation QA V3)

1. **Kiểm thử động học tự động trên toàn bộ các frame (`godot --headless --path godot -- --qa`):**
   - Kiểm tra **1.260 frame** của bản Demo 42 giây (`sequence`) và **480 frame** của bản Proof 16 giây (`proof_16s`) ở `30 FPS` — kết quả: **`QA PASS` 100%**.
   - **Bảo toàn kích thước khâu cứng (`scale == Vector2.ONE`):** Toàn bộ các khâu máy (`Boom`, `Stick`, `Bucket`, `BoomRamNear`, `BoomRamFar`) và toàn bộ các nút bộ phận nhân vật (`Engineer`, `Capy`, `Torso`, `Head`, `Hat`, `ArmR`, `ArmL`, `PawL`, `PawR`, `SafetyRail`) luôn giữ `scale == Vector2.ONE`, hoàn toàn không dùng mesh warp hay non-uniform scaling.
   - **Độ trùng tâm chốt (`< 0.01 px`) và độ lồng ty xi lanh (`rod_inside > 9` và `< barrel_length`):**
     - Xi lanh nâng cần (`BoomRamNear/Far`): khoảng cách 2 chốt tăng đơn điệu từ **`289,31 → 318,18`** đơn vị minh họa (`BARREL = 233`, `ROD = 176`).
     - Xi lanh tay gầu (`Stick cylinder`): khoảng cách 2 chốt biến thiên từ **`173,68 → 211,85`** đơn vị minh họa (`BARREL = 132`, `ROD = 111`).
     - Xi lanh gầu (`Bucket cylinder` + cơ cấu 4 khâu): khoảng cách 2 chốt biến thiên từ **`160,3 → 183,4`** đơn vị minh họa (`BARREL = 120`, `ROD = 90`).
2. **Kiểm thử chống đứng hình (0,25s Grayscale `320×180` MAD QA theo `ANIMATION_QUALITY_V3_BRIEF.md`):**
   - **Trước khi nâng cấp (Bản V1/V2):** Có tới **90 / 157** khoảng 0,25s trên file gốc (`39 / 82` khoảng trên bản nén) có `MAD < 0.5/255`, bị đóng băng hoàn toàn ở `17,5–21,7s` (`D04`) và `35,5–41,8s` (`D06`).
   - **Sau khi nâng cấp (Bản V3):**
     - **Clip Proof 16 giây (`CAPY-BK-EP02-PC200-8-v3-proof-16s.mp4`, `1920×1080`, `30 FPS`, `480 frames`):** **`0 / 59`** khoảng có `MAD < 0.5/255` (`Min MAD = 1.050`, `Mean MAD = 3.442`, `Max MAD = 32.760`).
     - **Video Demo 42 giây (`CAPY-BK-EP02-PC200-8-demo.mp4`, `1920×1080`, `30 FPS`, `1260 frames`):** Chỉ còn **`1 / 157`** khoảng chuyển cảnh sát ngưỡng (`24.27–24.53s`, `MAD = 0.331`), toàn bộ các đoạn đứng hình `17,5–21,7s` và `35,5–41,8s` đã được xóa bỏ hoàn toàn (`Mean MAD` tăng gấp đôi từ `1.704` lên `3.344`).
   - Xem bảng ảnh đối chiếu trực quan tại `build/EP02_pc200_8_demo_v3/EP02-V3-QA.png` và `build/EP02_pc200_8_demo_v3/EP02-V2-vs-V3-comparison.png`.

---

## 4. Báo cáo Tài nguyên Âm thanh còn thiếu (Stage 3 Review)

- **Đã có và tích hợp sẵn:**
  - `SIGNATURE.wav`: Trích từ file gốc đã được owner duyệt `Capy_Ki_Su_Oiii_v2_Nhe_Tu_Nhien.mp3`.
  - `MACHINE.wav` (42s) & `MACHINE_PROOF16.wav` (16s): Âm thanh máy đào, bơm thủy lực, van pilot và tiếng gầu xúc đất tổng hợp từ `make_foley.py`.
- **Còn thiếu (chờ owner cung cấp để ghép vào timeline CapCut Pro / bản Full):**
  - Các file WAV giọng đọc **ElevenLabs** đã duyệt của **CAPY** (`CAPY_D02.wav`, `CAPY_D06.wav`) và **ENGINEER** (`ENGINEER_D02.wav`, `ENGINEER_D03.wav`, `ENGINEER_D04.wav`, `ENGINEER_D05.wav`, `ENGINEER_D06.wav`) theo đúng bảng mốc thời gian trong `audio_timing.csv` và phụ đề `EP02_demo_vi.srt`. Tuân thủ nghiêm ngặt quy định: **không dùng eSpeak hoặc giọng TTS robot thay thế**.

# Asset manifest · EP02 DRAFT

Kiểm kê ngày 2026-11-12. Mã nguồn công khai dùng rig và hình kỹ thuật vẽ lại trong Godot. Hình nhận diện và bản thu nằm trong gói duyệt cục bộ. Logo BK cần đối chiếu quyền sử dụng trước khi phát hành.

| Tài nguyên | Nguồn, công cụ và thay đổi | Cảnh | Trạng thái |
|---|---|---|---|
| `local/studio-cels.png` | Studio EP01 V4 và bộ diễn V7 cục bộ. Xuất lớp hình gốc trước bố cục và phụ đề, 42 cel ở 10 fps, mỗi cel 520 × 737, atlas 7 cột × 6 hàng. Giữ lớp vẫy tay và miệng đồng bộ đoạn tag. | D01 | EP01 continuity, chờ duyệt bố cục EP02 |
| `local/field-hook.png`, `local/field-reply.png` | Hai góc G-01 và G-02 của EP01 V7. Xuất hình trước phụ đề và tiêu đề. Mỗi tấm 520 × 737, có chỉnh mũ trong pipeline EP01. | D02, D06 | EP01 continuity, chờ duyệt bố cục EP02 |
| `godot/art/pc200-parts.png` và `godot/art/worksite.png` | Hình 2D ImageGen dựa trên màu và nét EP01. Godot tách thân trên, xích, cần, tay gầu và gầu thành lớp cứng. Hai xi lanh có ty, vỏ và chốt riêng. [Nguồn hình và prompt](godot/art/PROVENANCE.md) | D02–D06 | Hình minh họa, DRAFT |
| Động cơ, bơm, joystick, van, mặt cắt và đường dầu | Đồ họa gốc vẽ bằng Godot. Đối chiếu [nguồn hãng](TECHNICAL_QA.md). Tóm tắt minh họa nhánh nâng, bao gồm mạch pilot và phản hồi tải LS. | D03–D05 | Sơ đồ giản lược, DRAFT |
| `SIGNATURE.wav` | Trích đúng đoạn 00:01.276–00:04.086 từ WAV thoại EP01 V7 đã dựng, bắt nguồn từ file `Capy_Ki_Su_Oiii_v2_Nhe_Tu_Nhien.mp3` của owner. | D01 | Bản đã sử dụng tại EP01, lưu cục bộ |
| `CAPY`, `ENGINEER` | Vị trí và lời trong SRT/CSV. Workspace có lời thoại EP01 nhưng chưa thấy bản thu đúng câu EP02 cho hai vai. | D02–D06 | Chờ WAV đã duyệt |
| Âm thanh máy nền | Foley tổng hợp cục bộ từ dao động và nhiễu, có điểm mở van và nhịp nâng, chạy riêng với giọng. | D02–D06 | DRAFT |

Kiểm kê thực tế: `origin/main` tại `735985878709e4a4fbb3fb0d11dc94c05ececcd5`. Có video EP01 V7, WAV, SRT, hình studio và công trường cục bộ. Bản thử EP02 26 giây được nhắc trong Issue #8 chưa tìm thấy ở cây Git hoặc workspace dưới dạng dự án hay video EP02 nhận diện được. Các tên file từ cuộc trò chuyện chỉ được đưa vào kiểm kê khi tìm thấy trên đĩa.

Để làm lại atlas, xuất cel studio 520 × 737 từ pipeline EP01 trước compositor tại các thời điểm `clamp(1.276 + i/10 - 0.480, 1.200, 4.100)`, với `i` từ 0 đến 41. Ghép hàng tuần tự 7 cột. Hai hình field dùng tư thế đầu của G-01 và G-02.

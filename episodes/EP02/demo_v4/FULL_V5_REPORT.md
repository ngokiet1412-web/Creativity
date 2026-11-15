# EP02 · Bản dựng đầy đủ V5 (DRAFT, chưa có thoại)

Ngày 2026-11-14. Nhánh `claude/ep02-full-v5`, nối tiếp `claude/ep02-v42-sc05-cylinder`. Bản này không ghi đè V3, V4 hay SC03–SC05 đã duyệt.
Theo yêu cầu “làm thành 1 video hoàn chỉnh”, đây là toàn bộ SC01–SC14 của `SCRIPT_YOUTUBE_PC200_8_FULL_V2.md`. Lời thoại giữ nguyên từng chữ: script tự đọc từ file kịch bản, không gõ lại.

## 1. Thời lượng và giọng

- **Thời lượng nháp:** khoảng 8 phút 42 giây. Thời gian tính theo ước lượng 4,2 âm tiết/giây.
- **Thoại thật:** kịch bản đặt mục tiêu 10–12 phút đo theo bản thu thật. Khi có WAV ElevenLabs owner duyệt, thay `est()` trong `tools/full/build_full.py` bằng độ dài WAV rồi build lại. Mọi key hoạt hình đều bám theo mốc thoại, nên hình tự giãn theo giọng, không phải tăng tốc lời.
- **Âm thanh hiện có:** chỉ tiếng máy tổng hợp ở −30 dBFS rms. Chưa có giọng, không dùng giọng thay thế.
- **Phụ đề:**
  - `EP02_FULL_V5_vi.srt` là file tách riêng.
  - `..._review_subs.mp4` là bản có phụ đề in sẵn, chỉ để duyệt.
  - `full_v5/audio_timing_full.csv` là bảng thời gian từng câu.

## 2. Các cảnh

| Cảnh | Nội dung hình | Nguồn |
|---|---|---|
| SC01 | Studio Capy (cel EP01 đã duyệt, có nhép theo câu). Màn hình trên tường bật lên cảnh PC200-8 xúc rồi nâng gầu đất. Camera đẩy liền mạch qua màn hình ra công trường, anh kỹ sư trả lời ở rào chắn. | mới |
| SC02 | Máy dừng, x-ray thân. Các bộ phận sáng lần lượt (vị trí minh họa tương đối). Chuỗi năng lượng: động cơ → bơm → van → xi lanh. | mới |
| SC03 | Động cơ và cụm bơm kép | đã duyệt, giữ nguyên |
| SC04 | CLSS | đã duyệt, giữ nguyên |
| SC05 | PPC → van → xi lanh, có xi lanh V4.2 | V4.2 |
| SC06 | Từng xi lanh chuyển động một. Chiều dài xi lanh điều khiển góc khớp. Mũi tên lực và chốt được tô sáng. Câu “tay cao su” của Capy bị gạch chéo, đổi sang khâu cứng quanh chốt, có chiều dài L chốt–chốt. | mới |
| SC07 | Mặt cắt xi lanh có hành trình bằng đúng xi lanh trên máy. F ≈ p·A, v ≈ Q/A. Tay đòn d tính từ chốt chân cần, M = F·d. Lực tại răng gầu khác lực piston. | mới |
| SC08 | Nhìn từ trên: chỉ thân trên quay, gầm đứng yên. Khung nhỏ: bánh răng nhỏ lăn trong vòng răng cố định (ăn khớp đúng tỉ số). | mới |
| SC09 | Mặt cắt khớp quay trung tâm (dầu thông qua rãnh vòng ở mọi góc quay). Xích nhìn ngang: bánh dẫn, mắt xích chạy vòng, mặt đất không trượt. Nhìn từ trên: hai xích cùng tiến thì đi thẳng, ngược chiều thì quay tại chỗ (góc quay = chênh hành trình hai xích / khoảng cách hai xích). | mới |
| SC10 | Đường hồi khái niệm: xi lanh → van → két làm mát → lọc (bắt cặn) → bình (tách bọt) → hút. | mới |
| SC11 | Gầu tì vào đá, áp tăng tới mức cài đặt thì dừng tăng, van relief mở về thùng. Bảng áp relief theo brochure. Van giữ tải (khái niệm). Cảnh báo an toàn. | mới |
| SC12 | Sơ đồ khối khái niệm: màn hình, bộ điều khiển động cơ, bộ điều khiển bơm, cảm biến, EPC. Tín hiệu điện tử vẽ nét đứt xanh lá. | mới |
| SC13 | 4 nhóm giả thuyết có hoạt hình nhỏ. So sánh biểu hiện giữa các chức năng. Đo theo quy trình, không thay bơm chỉ vì máy chậm. | mới |
| SC14 | Kéo lùi từ bản đồ hệ thống về màn hình studio, các nhánh sáng theo lời tổng kết của Capy. Thẻ kết “Tập 3”. | mới |

## 3. Kiểm chứng

- **K1 ✓, brochure CEN00049-08, đã đối chiếu lại hôm 2026-11-14:**
  - Relief: mạch công tác 37,3 MPa; di chuyển 37,3 MPa; quay toa 28,9 MPa; pilot 3,2 MPa.
  - Bơm piston thay đổi lưu lượng, 439 L/phút.
  - 2 mô tơ di chuyển (piston hướng trục, có phanh đỗ); 1 mô tơ quay toa (có phanh giữ quay).
  - 2 xi lanh cần, 1 xi lanh tay gầu, 1 xi lanh gầu.
- **NGUYÊN LÝ:** vị trí bộ phận trong SC02, khớp quay trung tâm, van relief, van giữ tải, đường hồi, sơ đồ khối điện tử, nhóm giả thuyết SC13.
- **QA tự động:**

| Cảnh | Điểm kiểm |
|---|---|
| SC06 | Mọi xi lanh trong hành trình; răng gầu trên mặt đất |
| SC08 | Gầm không quay |
| SC09 | Góc quay = chênh lệch hai xích / khoảng cách xích |

  Kết quả: xem `full_v5/qa/`.

## 4. Chưa xác minh / giới hạn

1. Vị trí bố trí bộ phận trên thân (SC02) chỉ là minh họa tương đối, đã ghi rõ trên hình.
2. Cấu tạo khớp quay trung tâm: phần nào gắn thân trên, phần nào gắn gầm còn tùy thiết kế. Hình chỉ là nguyên lý.
3. Số răng vòng quay toa và bánh răng nhỏ (90/14) là số minh họa.
4. Tỉ lệ máy nhìn từ trên là minh họa, không ghi kích thước.
5. Nhân vật chưa nhép theo thoại thật: chưa có file giọng, và chưa có bộ miệng cho anh kỹ sư.
6. Ngữ cảnh từ project FuelGuard/NCKH chưa được đưa vào: phiên làm việc này không đọc được chat của project khác. Dữ liệu FuelGuard không được lên repo công khai.

## 5. Dựng lại

```
cd episodes/EP02/demo_v4/tools/full && python3 build_full.py          # timing + scenes + SRT
godot --path ../../godot --fixed-fps 30 --write-movie out/scXX.avi res://full/scXX.tscn -- --qa
python3 assemble.py <thư mục render> <thư mục ra>
```

Ảnh studio cel và nhân vật nằm trong `godot/local/` (không có trên repo công khai). Thiếu thư mục này thì cảnh vẫn chạy, chỉ không có nhân vật.

## 6. Cập nhật V6 (2026-11-15, theo phản hồi owner)

- **Nhép miệng:** mọi nhân vật (Capy studio, hai nhân vật ở góc, hai nhân vật ở rào chắn) có miệng vẽ riêng, mở theo `godot/full/mouth.json`. Khi chưa có giọng, miệng mở một nhịp cho mỗi âm tiết của câu thoại. Khi có file giọng, miệng mở theo độ to thật của bản thu.
- **Giọng:** chưa chèn. Phiên làm việc này không có công cụ tạo giọng ElevenLabs, và giọng máy (piper/eSpeak) bị cấm theo yêu cầu. Đường ống đã sẵn: thả file vào `godot/local/voice/` theo tên trong `full_v5/VOICE_SHEET.csv` (một file cho mỗi câu thoại), chạy `build_full.py`, render lại, `assemble.py` tự trộn giọng lên nền tiếng máy. SC01, SC02, SC06–SC14 tự giãn hình theo độ dài giọng; SC03–SC05 giữ nhịp đã duyệt, giọng đặt ở đầu câu.
- **Studio:** cel đặt sát mép trái; phần còn lại là tường một màu lấy từ cel, mép hòa mềm 70 px, băng ghế và mặt bàn nối tiếp. Không còn sọc kéo dài. Màn hình lớn hơn.
- **SC02:** động cơ và bơm trong bản đồ là chính mặt cắt chi tiết của SC03 thu nhỏ (trục khuỷu quay, piston chạy), camera đẩy vào gần. Ghi chú và chuỗi năng lượng dời lên trên, không đè phụ đề.
- **Anh kỹ sư ở góc phải:** lật lại, quay mặt và chỉ tay vào trong khung hình.
- **Đống đất:** vẽ lại thành đống nằm trên mặt đất (bóng tiếp xúc, chân đống lởm chởm, ba dải sáng tối, viền mực). Chỉ xuất hiện ở cảnh có đào (SC01) và bị gầu khoét theo đúng đường răng gầu. Các cảnh khác máy đứng trên nền phẳng.
- **Thay đổi vào file dùng chung:** `segment_base.gd`, `crew.gd`, `env.gd` có thêm phần miệng, lật nhân vật và kiểu đống đất mới. Bản gốc đã duyệt vẫn nằm ở commit `b5ae650`.
- **QA:** 14/14 cảnh, 0 lỗi.

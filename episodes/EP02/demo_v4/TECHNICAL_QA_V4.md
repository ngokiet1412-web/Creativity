# EP02 V4 · Báo cáo kỹ thuật, điểm chưa xác minh và QA (DRAFT)

Ngày 2026-11-12. Phạm vi: bản mẫu 16 giây, gồm một lần nâng cần có tải và một lần cuộn gầu của máy dáng PC200-8, minh họa 2.5D. Đây không phải sơ đồ sửa chữa hay vận hành. Không đại diện cho một máy thật nào.

## 1. Phân loại nội dung trên hình

Mỗi nhãn trong video mang một trong hai thẻ:

| Thẻ | Nghĩa | Nhãn trong bản mẫu |
|---|---|---|
| **K1 ✓** | Đã đối chiếu brochure Komatsu PC200-8/PC200LC-8 CEN00049-08, mục Specifications | Động cơ SAA6D107E-1 · Bơm piston thay đổi lưu lượng · 2 xi lanh nâng cần Ø120 mm, hành trình 1.334 mm |
| **NGUYÊN LÝ** | Minh họa giản lược, chưa đối chiếu sơ đồ theo số sê-ri | Van mở: dầu cấp/dầu hồi · Con trượt mở P→A, B→T · Khoang đáy/khoang ty · Xi lanh gầu cuộn gầu |

Góc trên phải luôn có dòng “Sơ đồ giản lược · không phải sơ đồ cổng van theo số sê-ri”.

## 2. Thông số đã đối chiếu (K1)

| Mục | Giá trị | Dùng trong V4 |
|---|---|---|
| Động cơ | SAA6D107E-1, 110 kW (net) tại 2.000 rpm | Nhãn, tiếng máy |
| Hệ thủy lực | HydrauMind, closed-center, có van load sensing và van bù áp | Bơm ở lưu lượng chờ khi van đóng; tín hiệu LS khi van mở |
| Bơm chính | Piston, thay đổi lưu lượng, cực đại 439 L/phút | Đĩa nghiêng mở theo nhu cầu |
| Xi lanh cần | 2 × Ø120 × 1.334 × ty Ø85 mm | Hành trình rig; tốc độ dầu hồi ≈ 0,50 lần dầu cấp |
| Xi lanh gầu | 1 × Ø115 × 1.120 × 80 mm (tay gầu 2,41/2,93 m) | Trần hành trình xi lanh gầu |
| Van an toàn | 37,3 / 28,9 / 3,2 MPa | Không đưa lên hình |

## 3. Điểm chưa xác minh

1. **Cổng van, đường ống, vị trí bơm/van/thùng trong khoang máy:** bố trí trình bày. Cần bản vẽ thủy lực SEN00112 đúng số sê-ri. Hai bơm của PC200-8 vẫn vẽ gộp thành một.
2. **Tọa độ chốt xi lanh, chiều dài đóng, cơ cấu 4 khâu gầu:** hình học minh họa, chỉ ràng buộc để nằm trong hành trình K1. Không phải bản vẽ nhà máy.
3. **Chiều dài cần 5,70 m / tay gầu 2,925 m:** theo cấu hình tiêu chuẩn. Cần xác nhận với cấu hình tay gầu cụ thể.
4. **Van chống trôi cần / giữ tải:** shop manual SEN00100 có mô tả (trích từ audit V2), nhưng phiên này chưa mở lại tài liệu. V4 không ghi nhãn tên van này.
5. **Tốc độ nâng:** ty đi đều 3,7 px/s, tức khoảng 0,037 m/s. Chậm hơn máy thật để người xem kịp nhìn dầu và piston. Đây là nhịp dạy học, không phải số đo.
6. **Mức võng khi mở van (0,12°), mức nhún khi dừng (0,28°), độ lắc máy (≤ 0,13°), độ rung (≤ 0,45 px):** giá trị biên tập, cố ý nhỏ, không phải số đo.
7. **Phong cách hình máy:** atlas ImageGen gốc vẫn còn chất render; shader chỉ làm dịu. Muốn đạt minh họa 2.5D thật sự thì nên vẽ lại các lớp máy.
8. **Layer nhân vật:** vẫn cắt từ ảnh EP01, chỉ đầu Capy xoay và mí mắt. Chưa có layer miệng/tay, nên chưa khớp khẩu hình.
9. **Giọng:** chưa có WAV CAPY/ENGINEER cho EP02, nên không dùng giọng thay thế. Thời lượng hình đang giả định 3,9–4,1 âm tiết/giây.

## 4. QA chuyển động

`godot --path godot --fixed-fps 30 --quit-after 480 res://main.tscn -- --qa` → `qa_geometry.txt`, `telemetry.csv`.

| Kiểm tra | Kết quả |
|---|---|
| Khung kiểm | 480/480, **0 lỗi** |
| Ba xi lanh trong hành trình | Cần 56–83 / 133 px · tay gầu 49 / 149 (đứng yên) · gầu 90–104 / 112 |
| Cơ cấu 4 khâu, chốt khớp, không đổi tỷ lệ khâu | Đạt (sai < 0,05 px) |
| Không có xi lanh nhảy quá 6 px/khung, gầu không xuyên nền | Đạt |
| Cần không đi lên khi con trượt đóng (ngưỡng 2 px/s, bỏ qua dao động nén dầu) | Đạt |
| Ty đi đều khi lưu lượng không đổi | 3,704–3,713 px/s trong 6–11 s |
| Lắc máy | −0,12° đến +0,13°, mượt (lấy gia tốc trên cửa sổ ±0,2 s) |
| Mẫu gần như đứng hình (phép đo owner dùng) | **2/32**, cả hai trong studio 0–3 s. V3: 9/84 · V2: 34/82 |
| Đoạn gần như đứng lâu nhất | 0,13 s |

Hình kèm theo trong gói bàn giao (`qa/`):
- `EP02_V4_pin_coordinate_plot.png`: góc khớp, chiều dài 3 xi lanh so với giới hạn, quỹ đạo các chốt, tốc độ ty, đĩa nghiêng, áp bơm và lắc máy.
- `EP02_V4_pin_diagnostics.jpg`: 6 khung có đánh dấu chốt và chiều dài xi lanh.
- `before_after_V3_V4.jpg`: so sánh 4 cặp khung.
- `contact_every_1s.jpg`: một khung mỗi giây.

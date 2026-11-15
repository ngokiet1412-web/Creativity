# EP02 V3 · Báo cáo kỹ thuật và QA chuyển động (DRAFT)

Ngày 2026-11-12. Phạm vi: một lần múc đất và một lần nâng cần của Komatsu PC200-8, minh họa 2D. Đây là bản demo chờ owner duyệt theo `ANIMATION_QUALITY_V3_BRIEF.md` và Issue #8. Chưa dựng tập dài hoặc bản TikTok.

## 1. Thông số đã kiểm tra

| Mục | Giá trị dùng | Nguồn | Trạng thái |
|---|---|---|---|
| Động cơ | Komatsu SAA6D107E-1, 110 kW (net) tại 2.000 rpm, 6,69 L | K1 | Đã đối chiếu trực tiếp với brochure ngày 2026-11-12 |
| Hệ thủy lực | HydrauMind, closed-center, load sensing valves, pressure compensated valves | K1 | Đã đối chiếu. Brochure không dùng chữ “CLSS”; tên CLSS lấy theo shop manual (K3) |
| Bơm chính | Piston, thay đổi lưu lượng; lưu lượng cực đại 439 L/phút | K1 | Đã đối chiếu |
| Van an toàn | 37,3 MPa công tác/di chuyển, 28,9 MPa quay toa, 3,2 MPa pilot | K1 | Đã đối chiếu, **không** đưa lên hình demo |
| Xi lanh cần | 2 × 120 mm × hành trình 1.334 mm × ty 85 mm | K1 | Rig dùng đúng hành trình 1.334 mm; tỷ lệ diện tích vòng khuyên / khoang đáy = 1 − (85/120)² ≈ 0,50 dùng cho tốc độ vạch dầu hồi |
| Xi lanh tay gầu | 1 × 135 × 1.490 × 95 mm | K1 | Rig chỉ dùng 1.490 mm làm trần hành trình |
| Xi lanh gầu | 1 × 115 × 1.120 × 80 mm (tay gầu 2,41/2,93 m) | K1 | Rig chỉ dùng 1.120 mm làm trần hành trình |
| Cần / tay gầu | 5,70 m / 2,925 m | Cấu hình tiêu chuẩn PC200-8 | **Cần owner/reviewer xác nhận** với bảng kích thước brochure cho đúng cấu hình tay gầu |
| Van chống trôi cần | Có trong shop manual SEN00100 | K3 (trích từ audit V2 của Codex) | Chưa mở lại tài liệu trong phiên này |
| Khớp quay trung tâm, PPC, lọc, két làm mát | Có trong chương thủy lực | K3 | Chưa dùng trong demo nâng cần |

Nguồn:
- **K1** · Komatsu PC200-8 / PC200LC-8 brochure CEN00049-08, mục Specifications: https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf
- **K3** · Shop manual PC200/220-8 SEN00084-03 (SEN00099, SEN00100), theo `../demo/TECHNICAL_QA.md`.
- **K4** · Bản vẽ thủy lực SEN00112-03, cần để rà cổng van theo số sê-ri. Chưa có trong tay.
- Không dùng tài liệu PC200-8M0.

## 2. Phần nguyên lý giản lược (đã ghi trên hình)

- Vị trí động cơ, bơm, thùng, van, joystick và đường ống trong khoang máy là **bố trí trình bày**, không phải vị trí lắp thật. Hình có nhãn “Sơ đồ giản lược · không phải sơ đồ cổng van theo số sê-ri”.
- Hai bơm của PC200-8 được gộp thành một ký hiệu bơm. Chỉ vẽ một nhánh van cần. Van bù áp, PC/EPC, mạch ưu tiên và hợp lưu chưa vẽ.
- Tọa độ chốt xi lanh, chiều dài đóng của xi lanh, cơ cấu 4 khâu của gầu và tai treo lắp thêm trên tay gầu là hình học minh họa. Chúng được chọn để mọi xi lanh nằm trong hành trình hãng ghi (xem mục 4), không phải bản vẽ nhà máy.
- Màu là quy ước biên tập: đỏ áp lực, xanh hồi, cam pilot, tím tín hiệu tải LS.

## 3. Quan hệ vật lý được mô phỏng

- **Áp suất theo tải:** khi van ở giữa, bơm giữ lưu lượng chờ nhỏ, đĩa nghiêng góc nhỏ, kim áp ở vùng chờ. Khi con trượt mở, áp bơm tăng lên mức tải cộng chênh áp LS rồi mới có chuyển động. Không có cảnh bơm tự tạo áp cố định độc lập với tải.
- **Lưu lượng theo chuyển động:** vạch dầu dịch theo thể tích dầu mà piston đẩy (tính từ chiều dài xi lanh ở từng khung). Ty đứng thì dầu đứng, ty ra thì đỏ vào khoang đáy, xanh rời khoang ty với tốc độ ≈ 0,5 lần. Ty thu (chưa có trong demo) sẽ tự đảo màu hai ống.
- **Đĩa nghiêng:** góc tính từ tốc độ xi lanh ở 0,18 s phía trước, nên bơm tăng góc trước khi cần chạy.
- **Giữ cần:** van về giữa, hai cổng A/B bị chặn, khoang đáy vẫn đỏ (dầu giữ tải), cần đứng yên.
- **Đất rơi:** cục đất rời mép gầu với đúng vận tốc điểm đó, rơi với g = 9,81 m/s² (981 px/s² ở 100 px = 1 m) và nằm lại trên nền.

## 4. Kiểm thử chuyển động

Chạy: `godot --path godot --fixed-fps 30 --quit-after 1260 -- --qa` (cần phiên đồ họa). Kết quả ghi vào `qa_geometry.txt` và `telemetry.csv`.

| Kiểm tra | Kết quả |
|---|---|
| Số tư thế kiểm | 1.260 / 1.260 khung, **0 lỗi** |
| Chiều dài 3 xi lanh trong [chiều dài đóng, đóng + hành trình] | Đạt. Hành trình dùng: cần 51–83 / 133 px (0,51–0,83 m của 1,334 m), tay gầu 24–49 / 149 px, gầu 66–104 / 112 px |
| Cơ cấu 4 khâu của gầu luôn đóng được, thanh dẫn và thanh chữ H giữ đúng chiều dài (sai < 0,05 px) | Đạt |
| Khớp tay gầu và khớp gầu luôn nằm đúng chốt (sai < 0,05 px), không khâu nào bị đổi tỷ lệ | Đạt |
| Xi lanh không nhảy quá 6 px/khung | Đạt |
| Gầu không chui xuống nền ngoài vùng đống đất | Đạt (trong đống đất có lớp che sâu 40 px) |
| Cần không nâng khi con trượt đóng (từ 9,6 s) | Đạt. Đoạn múc đất 4–9 s dùng các nhánh van tay gầu/gầu/cần không vẽ trên sơ đồ |
| Không có mesh warp hay scale không đều | Mọi lớp là Sprite2D với scale đều; gầu dùng lật gương ngang (xem mục 6) |

Ảnh chẩn đoán chốt ở 6 tư thế: `qa/EP02_V3_pin_diagnostics.jpg` trong gói bàn giao (chạy lại với `-- --pins --start=T`).

### Đo độ “đứng hình” (cùng phương pháp owner dùng cho V2)

So khung t và t + 0,25 s mỗi 0,5 s, ảnh xám 320 × 180, ngưỡng sai khác trung bình 0,5/255:

| Bản | Mẫu gần như đứng | Ghi chú |
|---|---|---|
| V2 (Codex, 42 s) | 34 / 82 | Đứng hình khoảng 17,5–21,5 s và 35,5–40 s |
| **V3** | **9 / 84** | 6 mẫu ở intro studio 0–4 s (cel EP01 chỉ động ở miệng và tay, chiếm ít diện tích khung), 4,0 s (khung đầu cảnh), 30,5 s (cần dừng, nghỉ có chủ đích), 34,5 s (khung cắt), 41,5 s (cuối) |

Đoạn liên tiếp gần như đứng lâu nhất: 0,70 giây (41,27 s), nằm trong mức nghỉ 0,5–1 s mà brief cho phép. Báo cáo đầy đủ trong `motion_report.txt`.

## 5. Còn chưa chắc chắn hoặc còn thiếu

1. **Giọng EP02.** Chưa có WAV CAPY/ENGINEER nào cho EP02. Không dùng eSpeak hay giọng thay thế. Thời lượng hình đang giả định 3,8–4,8 âm tiết/giây.
2. **Lớp nhân vật.** Không có file layer Capy/anh kỹ sư. Bản này cắt từ ảnh EP01 `field-reply` bằng GrabCut: đầu Capy xoay quanh cổ, mí mắt vẽ thêm. **Thiếu lớp miệng nên chưa khớp khẩu hình**, tay anh kỹ sư không cử động. Đây là blocker cho bản dài.
3. **Gầu lật gương.** Atlas ImageGen vẽ gầu với miệng quay ra ngoài, ngược với máy đào gàu nghịch. V3 lật gương ngang để miệng gầu quay về cabin, đúng kiểu backhoe. Nên vẽ lại gầu (rỗng và đầy) thành 2 lớp riêng.
4. **Đất trong gầu được vẽ sẵn.** Atlas không có gầu rỗng, nên cảnh bắt đầu khi gầu đã cắm trong đống đất.
5. Cổng van, đường ống thật, vị trí bơm/van/thùng, mạch PC/EPC, van bù áp: cần SEN00112 đúng số sê-ri.
6. Chiều dài cần 5,70 m / tay gầu 2,925 m cần xác nhận theo cấu hình tay gầu.
7. Tỷ lệ thân trên / bánh xích theo atlas hơi “mập” hơn máy thật, vì chỉ được scale đều.

## 6. Trước / sau so với V2

| | V2 (PR #9) | V3 |
|---|---|---|
| Khớp chuyển động | Chỉ cần; tay gầu và gầu khóa cứng | Cần, tay gầu, gầu cùng chạy theo quỹ đạo đào (IK, 15 key/giây) |
| Xi lanh | Xi lanh cần thay đổi khoảng 10% chiều dài; xi lanh gầu vẽ cố định | 3 cụm xi lanh giải theo 2 chốt; gầu qua cơ cấu 4 khâu |
| Gầu | Miệng quay ra ngoài (ngược) | Lật gương, miệng quay về cabin |
| Tỷ lệ cần / bánh xích | 0,70 | 1,28 (đúng 5,7 m / 4,45 m) |
| Thủy lực | Mũi tên tĩnh trong khung sơ đồ | Nhìn xuyên vào khoang máy: piston động cơ, bơm quay, đĩa nghiêng, con trượt, LS, áp kế; dòng dầu tính từ thể tích piston |
| Nhân vật | Ảnh tĩnh trong khung | Đứng sau rào trong cùng cảnh với máy, nghiêng đầu, chớp mắt |
| Mẫu đứng hình | 34 / 82 | 9 / 84 |

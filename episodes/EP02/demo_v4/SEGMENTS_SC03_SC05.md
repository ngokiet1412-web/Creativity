# EP02 · Clip phân đoạn SC03, SC04, SC05 (DRAFT, chờ owner duyệt)

Ngày 2026-11-12. Nhánh `claude/ep02-segments-sc03-sc05`, tách từ `claude/ep02-v4-boom-proof`.
Kịch bản dùng: `episodes/EP02/SCRIPT_YOUTUBE_PC200_8_FULL_V2.md`, mục SC03–SC05. Lời thoại giữ nguyên từng chữ.

Phản hồi owner sau V4: phần x-ray “sơ sài, ghép mấy cái khối”. Ở đợt này mỗi bộ phận được vẽ lại thành **mặt cắt chi tiết**, có chuyển động đúng nguyên lý. Phong cách vẫn là blueprint tối và nét mực như V4.

| Clip | Thời lượng | Nội dung chính |
|---|---|---|
| SC03 · Động cơ và cụm bơm kép | 44,1 s | Mặt cắt động cơ 6 xi lanh thẳng hàng, trục khuỷu quay đồng bộ với trục bơm. Bơm piston hướng trục kép có đĩa nghiêng, 9 piston và guốc trượt, piston servo, mặt phân phối. So sánh góc nhỏ và góc lớn. |
| SC04 · Điểm khó: cảm nhận tải CLSS | 44,2 s | Bơm, van LS, van PC, hai nhánh van (cần, tay gầu) có van bù áp, van con thoi LS, xi lanh. Tay gạt trung gian thì LS về thùng, bơm ở lưu lượng chờ. Mở cần thì LS lên, đĩa nghiêng mở. Mở thêm tay gầu thì van bù áp chia dòng. Khi tải tăng, van PC giảm góc. |
| SC05 · Từ tay điều khiển đến van chính | 35,3 s | Mặt cắt van PPC (cần gạt, piston đẩy, lò xo đo, con trượt giảm áp). Áp pilot đẩy con trượt van chính, có vùng chết do độ chồng mép. P→A vào khoang đáy, B→T về thùng, xi lanh đi ra. Bảng so sánh mạch pilot 3,2 MPa với mạch công tác 37,3 MPa. |

## 1. Bộ phận đã vẽ lại (`godot/cutaway/`)

| File | Bộ phận | Chi tiết có trên hình | Chuyển động |
|---|---|---|---|
| `engine_cut.gd` | Động cơ SAA6D107E-1 (mặt cắt dọc) | Các te, trục khuỷu có má khuỷu và đối trọng, 6 thanh truyền, piston cắt nửa có xéc măng, sơ mi xi lanh, áo nước, nắp máy cắt có xupap và lò xo, kim phun, bu lông nắp, vỏ bánh đà | Trục khuỷu quay. Piston đi theo cơ cấu tay quay–con trượt thật (r, l). Thứ tự nổ 1-5-3-6-2-4. Xupap nâng theo pha chu trình. Có lóe cháy ở 0–45°. Ô nhỏ cho thấy hình chiếu đầu trục. |
| `pump_cut.gd` | Bơm HPV95+95 (2 bơm piston hướng trục nối tiếp) | Vỏ cắt, gối đỡ đĩa nghiêng, đĩa nghiêng, 9 piston có guốc trượt, khối xi lanh (nửa sau mờ), mặt phân phối, then hoa trục, piston servo nối với đĩa nghiêng, khối van giữa có cổng P1/P2 và cửa hút. Ô mặt phân phối có 2 rãnh bán nguyệt. | Guốc luôn tì lên mặt đĩa nghiêng. Hành trình = 2·Rb·tanα. Khoang đỏ khi piston đi về phía mặt phân phối (đẩy dầu), xanh khi hút. Mũi tên dầu chạy theo ∫n·tanα. |
| `spool_cut.gd` | Một nhánh van điều khiển chính, tâm kín | Thân van có rãnh T1/A/P/B/T2, con trượt có 3 vai và rãnh tiết lưu, nắp hai đầu có khoang pilot và lò xo định tâm, van bù áp | Con trượt dịch theo áp pilot. Vai chồng mép 27 px nên có vùng chết. Mở P→A và B→T cùng lúc. |
| `ppc_cut.gd` | Van PPC (joystick) | Tay nắm, đĩa đẩy, 2 piston đẩy, lò xo đo, con trượt giảm áp, khoang ra P1/P2, cấp pilot P, hồi T | Áp ra tỉ lệ hành trình cần (có vùng chết 8%). Bên không gạt nối về T. |

## 2. Kiểm chứng nội dung trên hình

| Thẻ | Nghĩa | Nhãn trong 3 clip |
|---|---|---|
| **K1 ✓** | Brochure Komatsu PC200-8 CEN00049-08, mục Specifications | SAA6D107E-1, 6 xi lanh, 6,69 L · Lưu lượng tối đa 439 L/phút · Van an toàn mạch công tác 37,3 MPa, mạch pilot 3,2 MPa |
| **K2 ✓** | Mục lục/thông số shop manual PC200-8 (bản tra cứu công khai) | Bơm HPV95+95 · Van điều khiển chính loại 6 con trượt · Van LS trên bơm |
| **NGUYÊN LÝ** | Cấu tạo chung, chưa đối chiếu bản vẽ theo số sê-ri | Còn lại: đĩa nghiêng, piston, servo, tâm kín, LS về thùng, con thoi LS, p_bơm = p_LS + Δp, van bù áp chia dòng, van PC giảm góc, PPC, vùng chết, P→A / B→T |

Van PC hạ từ K2 xuống NGUYÊN LÝ, vì câu “giữ trong công suất động cơ” là mô tả cách hoạt động, không phải thông số đã đối chiếu.

## 3. Điểm chưa xác minh

1. **Số piston trong HPV95:** vẽ 9 piston, là số thường gặp ở bơm piston hướng trục. Chưa đếm trên bản vẽ PC200-8.
2. **Tỉ số truyền động cơ–bơm:** vẽ 1:1 (bơm nối với bánh đà qua giảm chấn). Chưa đối chiếu.
3. **Thứ tự nổ 1-5-3-6-2-4:** đây là thứ tự chuẩn của động cơ 6 xi lanh thẳng hàng. Chưa đối chiếu tài liệu SAA6D107E-1.
4. **Giá trị chênh áp LS (Δp) và đường cong van PC:** chỉ minh họa định tính. Bảng thanh bên trái SC04 có ghi “minh họa định tính, không phải số đo”.
5. **Bố trí cổng trong thân van, vị trí van bù áp, cổng nào nối khoang đáy:** đều là sơ đồ nguyên lý, không phải cổng van theo số sê-ri (cần SEN00112).
6. **Bơm trước/sau cấp cho nhánh nào, mạch gộp/tách dòng:** SC04 chỉ vẽ bơm trước. Phần gộp/tách dòng của PC200-8 chưa đưa lên hình.
7. **LS-EPC và điện tử:** không vẽ ở SC04. Để dành cho SC12 theo kịch bản.
8. **Hình học PPC:** cấu tạo chung của van giảm áp kiểu PPC, không lấy từ bản vẽ Komatsu.
9. **Tốc độ chuyển động:** nhịp dạy học, chậm hơn máy thật. Không phải số đo.

## 4. Thời gian lời thoại và VO

- `segments_sc03_sc05/EP02_SC0X_vi.srt`: phụ đề tách riêng, không burn vào hình.
- `segments_sc03_sc05/audio_timing_segments.csv`: mỗi câu có khung hình, thời lượng nói ước tính (4,2 âm tiết/giây + 0,25 s) và cột kiểm “fit”.
- **Giọng:** chưa có file ElevenLabs owner đã duyệt cho EP02, nên clip chỉ có tiếng máy tổng hợp (`tools/make_foley_segments.py`, chạy theo telemetry, −24 dBFS rms). Không dùng giọng thay thế.
- Khi ước tính dài hơn khung hình, máy **giữ trạng thái lâu hơn** chứ không tăng tốc lời: thêm thời gian lúc đang chạy đều (`tools/segment_timing.py`). Sau khi chỉnh, cả 24/24 câu đều vừa khung. Khi có bản thu thật, chỉ cần sửa `INSERTS` rồi build lại; key, nhãn, nháy mắt và SRT dịch theo cùng một quy tắc.

## 5. QA

Chạy: `godot --path godot --fixed-fps 30 --write-movie out.avi res://segments/sc0X.tscn -- --qa` → `SC0X_qa.txt`, `SC0X_telemetry.csv` (đã chép vào `segments_sc03_sc05/`).

| Clip | Kiểm tra tự động |
|---|---|
| SC03 | Trục bơm quay đúng góc trục khuỷu ở mọi khung. Lưu lượng ∝ n·tanα. |
| SC04 | Tay gạt trung gian thì không có lưu lượng làm việc. p·Q không vượt trần PC. Tỉ lệ chia dòng theo độ mở hai con trượt. |
| SC05 | Không mở van khi tay gạt trong vùng chết. Xi lanh không đi lùi khi P→A đang mở. Ty không chạm cuối hành trình. |

| Clip | Khung kiểm | Lỗi | Mẫu gần đứng hình (cách owner đo: t với t+0,25 s, mỗi 0,5 s) | Đoạn đứng lâu nhất |
|---|---|---|---|---|
| SC03 | 1.322 | 0 | 0/88 | 0,03 s |
| SC04 | 1.326 | 0 | 1/88 (khung 0) | 0,00 s |
| SC05 | 1.058 | 0 | 2/70 (khung 0; 5,0 s lúc đổi người nói) | 0,27 s |

Khi tay gạt ở trung gian, van tâm kín không có dầu chảy, nên SC05 dùng camera đẩy chậm để hình không đứng. Không tạo dòng dầu giả.

## 6. Chưa làm (đợi owner duyệt)

- Các cảnh SC01, SC02, SC06–SC14 và bản 10–12 phút đầy đủ.
- Bản TikTok 9:16.
- Thay x-ray cũ trong cảnh máy V4 (`hydraulics.gd`) bằng bộ mặt cắt mới.
- Ghép VO ElevenLabs khi owner gửi file.

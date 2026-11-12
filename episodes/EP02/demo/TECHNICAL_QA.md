# Audit PC200-8 và kiểm thử demo nâng cần

**DRAFT · Kiểm tra nội bộ ngày 2026-11-12.** Phạm vi minh họa là một lần nâng cần, đọc theo mẫu PC200-8 tiêu chuẩn. Bản mô hình có tỷ lệ và tọa độ minh họa. Để xác nhận sơ đồ lắp ráp, cần dải số sê-ri, cấu hình tay gầu và revision tài liệu tương ứng.

## Nguồn đã đối chiếu

- **K1** · Brochure Komatsu PC200-8/PC200LC-8, CEN00049-08, mục Specifications. Tham chiếu chính cho mẫu, động cơ, cụm thủy lực, mô tơ, xi lanh và trị số danh định. [Brochure Komatsu](https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf)
- **K2** · Brochure Komatsu AESS688-01 bản thị trường khác. Dùng kiểm tra chéo SAA6D107E-1 và 439 L/phút. [Komatsu Perú](https://komatsu.pe/images/pdf-construccion/excavadora/PC200200LC-8SALESBROCHUREAESS688-012006EV-2.pdf)
- **K3** · Shop manual Komatsu PC200/220-8, SEN00084-03. SEN00099 bao quát thiết bị và CLSS. SEN00100, phần `Boom drift prevention valve 1`, mô tả dầu cấp vào đầu đáy khi nâng. Chương thủy lực liệt kê khớp quay trung tâm, PPC, đường hồi, lọc và két làm mát. Chỉ áp dụng nội dung có phạm vi PC200-8. [Bản đọc shop manual Komatsu](https://pdfcoffee.com/pc200-8-sen00084-03pdf-2-pdf-free.html)
- **K4** · Chỉ mục shop manual PC200-8 nêu tài liệu bản vẽ thủy lực SEN00112-03, tách PC200/200LC-8 và PC220/220LC-8. Cần bản vẽ và revision đúng máy để rà cấp cổng. [Chỉ mục Komatsu](https://www.manualslib.com/manual/2507934/Komatsu-Pc200-8.html)

## Phạm vi kỹ thuật

| Chủ đề | Đã xác nhận / dùng trong demo | Còn mở trước khi dựng tập dài |
|---|---|---|
| Động cơ | SAA6D107E-1, 6,69 L, công suất hữu ích 110 kW tại 2.000 rpm theo K1. Demo thể hiện trục truyền công suất sang bơm. | Kích thước, vật liệu và bố trí từng phần bên trong động cơ. |
| Bơm chính | Bơm piston thay đổi dung tích riêng, lưu lượng cực đại brochure 439 L/phút cho cụm. K3 phân biệt phần bơm trước và sau. Hình nguyên lý gộp thành một ký hiệu. | Đặc tuyến điều chỉnh, model bơm và giới hạn lưu lượng theo chế độ. |
| HydrauMind và CLSS | Tâm kín, cảm nhận tải, bù áp theo K1/K3. Demo dùng mũi tên tím từ phía van về bộ điều chỉnh bơm để chỉ tín hiệu LS. | Toàn bộ mạch LS/PC/EPC, ngưỡng và logic hợp/chia lưu lượng theo thao tác. |
| Joystick, pilot, van | PPC là tín hiệu điều khiển, van chính mở đường công tác theo K1/K3. Màu cam dành riêng cho pilot. | Cổng van, spool, tín hiệu điện và bố trí pilot theo phiên bản. |
| Xi lanh cần, tay gầu, gầu | K1 ghi hai xi lanh cần, mỗi xi lanh đường kính lòng 120 mm, hành trình 1.334 mm, ty 85 mm. Nâng cấp khoang đáy theo K3, dầu khoang ty hồi trong mạch tác động kép giản lược. K1 ghi kích thước xi lanh gầu thay đổi theo tay gầu. | Vị trí chốt, chiều dài và góc lắp thực, hành trình gầu/tay gầu theo cấu hình. Rig hiện kiểm tra nâng cần, tay gầu/gầu giữ góc tương đối. |
| Quay toa | Một mô tơ piston hướng trục và phanh giữ quay theo K1, cấu tạo truyền động ở K3. | Chi tiết giảm tốc, bố trí phanh và chiều dầu. |
| Di chuyển và khớp quay trung tâm | Hai mô tơ piston hướng trục có phanh theo K1. K3 liệt kê center swivel joint. Gầm giữ nguyên vị trí trong demo nâng. | Bản vẽ cổng khớp quay, điều khiển tiến/lùi và quay. |
| Hồi, lọc, làm mát, thùng | K3 xác nhận các phần tử. Demo chỉ gom đường hồi về thùng trong nhánh đang xét. | Các nhánh hồi, bypass, thứ tự theo mạch và chế độ. |
| Relief và giữ cần | K1 ghi cài đặt danh định 37,3 MPa cho công tác/di chuyển, 28,9 MPa quay toa, 3,2 MPa pilot. K3 có van chống trôi cần. Demo minh họa cần giữ vị trí khi van về giữa. | Xác nhận các cài đặt theo revision, mạch relief và van giữ tải; không dùng con số brochure để chỉnh máy. |
| Công suất, áp suất, lưu lượng, tốc độ | Động cơ cung cấp công suất. Bơm đưa dầu thành dòng. Chênh áp cần để thắng tải; tốc độ lý tưởng phụ thuộc lưu lượng và diện tích tác dụng. Dầu hai khoang đổi thể tích theo hành trình. | Tổn thất, áp hồi, giới hạn công suất và lực tới răng gầu. Các mức áp brochure chưa đưa lên hình demo. |

Màu là quy ước biên tập. Mũi tên đỏ đi từ bơm qua van vào khoang đáy, xanh từ khoang ty qua van về thùng. Khi piston dừng, mũi tên công tác tắt. Dịch chuyển mũi tên đỏ và xanh theo tiến độ ty, xanh khoảng một nửa đỏ theo tỷ số diện tích vòng khuyên/khoang đáy từ 85/120 mm, với quy ước hình minh họa. Mũi tên tím biểu thị hướng phản hồi áp tải. Các vị trí nối trên hình là vị trí trình bày, chưa xác minh theo từng cổng. Tài liệu PC200-8M0 nằm ngoài căn cứ dùng cho demo.

## Kiểm thử chuyển động

- `godot --headless --path godot -- --qa` chạy 1.260 tư thế ở 30 fps. Kiểm tra điểm mắt ty trùng chốt, hai xi lanh có cùng khoảng cách chốt, ty còn phần lồng trong vỏ, gầu nằm đúng gốc khớp, khâu không đổi tỷ lệ và đoạn giữ cần không trôi.
- Khoảng cách chốt tăng đơn điệu từ **269,20 đến 299,45 đơn vị minh họa**. Góc nâng bắt đầu ở 24,5 giây, tới đích ở 35,3 giây. Góc tay gầu và gầu tương đối giữ nguyên trong thao tác này.
- QA hình kiểm tra 6 cảnh, gồm vị trí trước, trong và sau lần nâng. Hình xi lanh trong khung cắt dùng chính tiến độ của rig máy. Hành trình minh họa, áp suất và tải chưa được kiểm thử trên máy thật.
- Movie Maker ghi 1.260 frame ở 30 fps. Windows giới hạn cửa sổ thu về 1875 × 1055. Bản bàn giao H.264 1920 × 1080 giữ tỷ lệ khi nội suy và thêm biên, không kéo méo khung hình.
- Rà giọng CAPY và ENGINEER, khẩu hình thoại mới và nhịp dựng theo bản thu khi có WAV đã duyệt. Demo hiện dùng đoạn tag EP01 và tiếng máy minh họa.

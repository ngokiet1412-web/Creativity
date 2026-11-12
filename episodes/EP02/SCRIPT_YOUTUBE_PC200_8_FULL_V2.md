# KĨ SƯ ƠIII! / CAPY BK — EP02 (YOUTUBE LONGFORM V2)

**Tên tập:** BÊN TRONG HỆ THỐNG THỦY LỰC KOMATSU PC200-8: Vì sao tay gầu khỏe, máy quay được, bánh xích chạy được?

**Trạng thái:** KỊCH BẢN TIỀN KỲ — cần duyệt giọng, kiểm tra bản vẽ từng mạch và đối chiếu serial. Đây là bản đầy đủ kiến trúc hệ thống, KHÔNG phải hướng dẫn tháo lắp/sửa chữa máy.

**Mục tiêu:** YouTube 10–12 phút (đo bằng bản thu thoại thực tế); 16:9 1920×1080, 30 fps. Sau đó biên tập một bản TikTok 2–3 phút, 9:16 1080×1920, không kéo giãn hay cắt vô nghĩa.

**Nhân vật:** Capy BK (hài, ngạc nhiên, giọng nam trẻ miền Nam), Anh Kỹ Sư (ấm, mạch lạc, không phát thanh), kênh có sound logo vui 'Kĩ Sư Ơiiii!'. Giọng thu/tạo trong ElevenLabs được duyệt và tách WAV theo scene; không dùng eSpeak, không ép lời cho đúng mốc thời gian.

**Phong cách:** 2D hoạt hình nhất quán với EP01, có phòng studio xanh, ly BK, micro; cắt ra máy đào vàng tại khu vực quan sát an toàn. Sơ đồ dầu cần vẽ LẠI bằng vector 2D, có phân biệt dầu áp lực, dầu hồi, pilot, tín hiệu điện. Không lấy nguyên trang manual đưa lên video làm tài sản hình ảnh.

---

## SC01 — 00:00–00:40 | BÍ ẨN GẦU ĐẤT

**Hình:** Sound-logo trong studio, Capy uống ly BK; màn hình bật cảnh PC200-8 nâng gầu đất. Máy đào đứng yên, chỉ cần và gầu chuyển động đúng khớp.

**CAPY:** 'Kĩiii sưuuu ơiiii! Ê anh! Bữa trước mình coi nguyên công trường rồi đó. Mà tui vẫn thắc mắc: cái tay máy đào này nhìn như mấy miếng sắt nối với nhau, sao nó nâng được một gầu đất nặng dữ vậy? Nó có giấu cơ bắp trong đó hả?'

**ANH KỸ SƯ:** 'Không có cơ bắp đâu. Thứ đáng xem nằm bên trong thân máy: một hệ thống thủy lực được điều khiển khá thông minh. Hôm nay mình lấy Komatsu PC200-8 làm ví dụ, đi từ động cơ cho tới tận gầu, rồi xem luôn quay toa và hai bánh xích.'

## SC02 — 00:40–01:20 | VẼ BẢN ĐỒ CẢ HỆ THỐNG

**Hình:** Mặt cắt PC200-8 2D. Highlight lần lượt động cơ, hai bơm chính, bình dầu, cụm van, các xi lanh, mô tơ quay toa, hai mô tơ di chuyển, két làm mát, lọc. Mỗi bộ phận có nhãn do editor gắn.

**CAPY:** 'Ủa, thủy lực có phải chỉ là một cái bơm nối với một cái xi lanh không?'

**ANH KỸ SƯ:** 'Đơn giản hóa như vậy thì dễ học bước đầu, nhưng chưa đủ cho PC200-8. Trên chiếc máy này còn có điều khiển tải, các đường dầu đến nhiều cơ cấu, van phân phối, điều khiển pilot và tín hiệu điện tử phối hợp. Mình sẽ lần theo dòng năng lượng trước: động cơ quay bơm; bơm đưa dầu vào hệ thống; van điều khiển dòng dầu; xi lanh hoặc mô tơ thủy lực biến năng lượng đó thành chuyển động.'

## SC03 — 01:20–02:10 | ĐỘNG CƠ VÀ CỤM BƠM KÉP

**Hình:** Cận SAA6D107E-1 với trục dẫn động sang bơm. Bản vẽ cắt đôi bơm piston hướng trục với đĩa nghiêng, nhóm piston quay và hành trình piston dài/ngắn. So sánh vị trí đĩa nghiêng lớn và nhỏ.

**ANH KỸ SƯ:** 'Động cơ diesel cấp công suất cơ học cho bơm. Dữ liệu PC200-8 cho thấy động cơ Komatsu SAA6D107E-1; phần bơm chính là loại piston thay đổi lưu lượng, có hai phần bơm để điều phối các nhu cầu làm việc. Bên trong bơm piston hướng trục, khi góc đĩa nghiêng thay đổi, hành trình piston thay đổi theo. Góc lớn hơn thường cho lưu lượng lớn hơn ở cùng tốc độ quay; góc nhỏ hơn thì lưu lượng giảm.'

**CAPY:** 'Vậy ga máy tăng chưa chắc gầu lúc nào cũng chạy nhanh nhất?'

**ANH KỸ SƯ:** 'Đúng. Lưu lượng đến cơ cấu còn tùy bơm đang được điều khiển ra sao, van đang mở thế nào, tải và các giới hạn công suất. Đó mới là điều thú vị.'

## SC04 — 02:10–03:00 | ĐIỂM KHÓ: LOAD SENSING / CLSS

**Hình:** Khung song song: tay trang chưa gạt — đĩa nghiêng giảm, lưu lượng nhu cầu thấp; tay trang mở — đường LS báo nhu cầu tải, đĩa nghiêng điều chỉnh. Đường áp lực đỏ, dầu hồi xanh, LS tím, không vẽ LS như đường cấp trực tiếp cho xi lanh.

**CAPY:** 'Thế cái tên CLSS nghe như mật mã là gì anh?'

**ANH KỸ SƯ:** 'Đó là hệ thống thủy lực tâm kín có cảm nhận tải. Nói đơn giản: khi các tay điều khiển ở trung gian, máy không cần cấp lưu lượng lớn tới mọi cơ cấu. Khi một cơ cấu cần làm việc, tín hiệu cảm nhận tải — gọi là LS — cùng các bộ điều chỉnh trên bơm giúp thay đổi lưu lượng phù hợp. Van bù áp còn hỗ trợ phân chia dòng dầu khi nhiều cơ cấu làm việc cùng lúc.'

**CAPY:** 'À! Không phải cứ nổ máy là bơm xả hết công suất đi khắp nơi. Nó phải nghe xem ai đang cần dầu!'

**ANH KỸ SƯ:** 'Hiểu theo mức nhập môn thì đúng. Nhưng điều khiển thực tế có cả giới hạn công suất của động cơ và các điều kiện vận hành.'

## SC05 — 03:00–03:45 | TỪ TAY ĐIỀU KHIỂN ĐẾN VAN CHÍNH

**Hình:** Cabin và hai joystick; sơ đồ PPC pilot tạo tín hiệu điều khiển cho spool; mặt cắt một nhánh van phân phối. Thêm nhãn 'sơ đồ nguyên lý minh họa, không phải sơ đồ cổng van theo serial'.

**CAPY:** 'Tui gạt cái cần nhỏ xíu trong cabin, sao điều khiển nổi một cái xi lanh bự vậy?'

**ANH KỸ SƯ:** 'Tay điều khiển không tự đưa toàn bộ lưu lượng của bơm chính. Trên PC200-8, mạch điều khiển pilot và cụm van chính thực hiện việc phân phối dầu đến các cơ cấu. Gạt joystick làm thay đổi tín hiệu điều khiển, từ đó dịch chuyển phần tử van tương ứng để cho dầu đi đến khoang thích hợp của xi lanh hoặc mô tơ.'

**CAPY:** 'Tức là một tín hiệu nhỏ có thể điều khiển cả dòng năng lượng lớn?'

**ANH KỸ SƯ:** 'Đúng, nhưng phải có nguồn năng lượng từ động cơ và bơm phía sau.'

## SC06 — 03:45–04:45 | XI LANH CẦN, TAY GẦU VÀ GẦU

**Hình:** Máy đào đã dừng. Tô màu 2 xi lanh cần, 1 xi lanh tay gầu, 1 xi lanh gầu theo cấu hình tiêu biểu trong brochure PC200-8; mũi tên lực đi qua chốt. Tách riêng từng khớp và xi lanh; rod chuyển động thẳng dọc trục, không co giãn vỏ.

**ANH KỸ SƯ:** 'Cần nâng hạ bằng các xi lanh cần; tay gầu tiến lùi nhờ xi lanh tay gầu; gầu cuộn hoặc mở bằng xi lanh gầu. Dầu vào một khoang tạo lực làm piston dịch chuyển, còn dầu ở khoang còn lại phải có đường thoát thích hợp. Qua các chốt và tay đòn, lực tịnh tiến của xi lanh biến thành chuyển động quay của các khâu.'

**CAPY:** 'Ủa vậy mình không được vẽ nguyên cái tay máy cong queo như cao su?'

**ANH KỸ SƯ:** 'Chính xác! Các khâu cứng quay quanh chốt, còn chiều dài xi lanh và góc khớp phải phù hợp hình học.'

## SC07 — 04:45–05:30 | ÁP SUẤT, LƯU LƯỢNG VÀ LỰC THẬT

**Hình:** Cận xi lanh, hiệu ứng dầu đẩy piston. Công thức F=p·A và v≈Q/A hiện từng phần; nhấn mạnh chiều quay tay đòn và lực tại răng gầu khác lực piston.

**CAPY:** 'Nghe nói áp suất càng cao là máy càng mạnh, đúng hông?'

**ANH KỸ SƯ:** 'Đúng một phần thôi. Với một khoang xi lanh lý tưởng, lực do áp suất tác dụng xấp xỉ F bằng p nhân diện tích A. Muốn piston chuyển động nhanh, còn cần lưu lượng Q; tốc độ lý tưởng gần bằng Q chia A. Nhưng lực tới răng gầu phụ thuộc thêm góc xi lanh, tay đòn, ma sát, tổn thất và giới hạn bền. Vì vậy không thể lấy lực piston rồi nói máy nâng được đúng chừng đó ký đất.'

**CAPY:** 'À! Áp suất là điều kiện tạo lực, lưu lượng liên quan tốc độ. Còn cơ cấu mới quyết định lực ra tới gầu!'

## SC08 — 05:30–06:15 | QUAY TOA BẰNG MÔ TƠ THỦY LỰC

**Hình:** Máy nhìn từ trên xuống: phần trên quay, khung bánh xích đứng yên. Highlight swing motor, bộ truyền giảm tốc, vòng quay toa; chỉ quay cabin và thân trên, không quay cả gầm.

**CAPY:** 'Tay gầu thì dùng xi lanh. Nhưng tại sao nguyên cái thân trên quay vòng vòng được?'

**ANH KỸ SƯ:** 'Đó là mạch quay toa. Dầu cấp đến mô tơ thủy lực quay toa; mô tơ cùng bộ truyền giảm tốc tạo mô men để xoay phần trên của máy trên vòng quay toa. Hệ thống có chức năng hãm và giữ quay theo thiết kế. Ở hình này, gầm xích vẫn đứng yên còn phần thân trên xoay — nhìn vậy mới đúng.'

## SC09 — 06:15–07:10 | ĐIỀU KHIỂN HAI BÁNH XÍCH VÀ KHỚP QUAY TRUNG TÂM

**Hình:** Cắt ngang thân trên–gầm dưới, tô các đường dầu qua center swivel joint. Hai travel motor ở gầm chạy với tốc độ/direction tương ứng, sprocket và dải xích chuyển động đồng bộ; minh họa tiến thẳng, quay vòng.

**CAPY:** 'Nhưng động cơ với bơm ở thân trên, hai mô tơ di chuyển nằm dưới gầm xích. Khi thân trên xoay, ống dầu không bị xoắn như mì gói hả?'

**ANH KỸ SƯ:** 'Giữa hai phần có khớp quay phân phối dầu ở trung tâm, thường gọi center swivel joint. Nó cho phép dẫn các mạch dầu xuống bộ phận di chuyển trong khi phần trên có thể quay tương đối với gầm. Mỗi bên xích có mô tơ thủy lực và bộ truyền cuối, nên có thể điều khiển hai bên để tiến, lùi hoặc đổi hướng.'

**CAPY:** 'Vậy bánh xích không phải cái hình chữ nhật xoay nguyên cục à!'

**ANH KỸ SƯ:** 'Đúng. Bánh dẫn quay, mắt xích chạy theo đường vòng, và xe dịch chuyển do tương tác với mặt đất.'

## SC10 — 07:10–08:00 | DẦU HỒI: LỌC VÀ LÀM MÁT

**Hình:** Dầu rời cơ cấu theo đường hồi về cụm van, lọc dầu, làm mát và bình chứa; mô phỏng bọt khí, tạp chất một cách khái niệm. Màu đường hồi khác áp lực; không nói mọi dòng đều buộc đi qua cùng một phần tử theo một thứ tự duy nhất.

**CAPY:** 'Nãy giờ toàn thấy dầu đi vô, vậy dầu đi đâu mất anh?'

**ANH KỸ SƯ:** 'Nó tuần hoàn trong mạch thủy lực. Sau khi thực hiện công việc, dầu quay về theo các đường hồi, được làm mát và lọc phù hợp với đường mạch trước khi trở lại bình. Dầu thủy lực không phải nhiên liệu để đốt trong xi lanh. Nó truyền năng lượng, bôi trơn và giúp tản nhiệt, nên độ sạch và nhiệt độ rất quan trọng.'

## SC11 — 08:00–08:55 | VAN GIỚI HẠN ÁP VÀ AN TOÀN

**Hình:** Tưởng tượng gầu chạm vật cản, mạch tăng áp; relief mở đúng chiều về đường hồi. Bên cạnh: các van giữ tải/ngăn trôi cần, ghi nhãn 'khái niệm'. Capy không chạm ống dầu áp cao.

**CAPY:** 'Ủa, gầu gặp cục đá cứng quá thì áp suất cứ tăng mãi sao? Nghe sợ à nha!'

**ANH KỸ SƯ:** 'Hệ thống cần van giới hạn áp và các chức năng bảo vệ để tránh vượt giới hạn thiết kế. PC200-8 có các mạch với mức áp thiết kế khác nhau. Tài liệu hãng nêu áp cài đặt relief danh định cho mạch công tác, mạch di chuyển, mạch quay toa và pilot; không nên gộp thành một con số cho mọi mạch. Ngoài ra còn có giải pháp chống trôi hoặc giữ tải cho cần. Tuy nhiên đừng bao giờ tự nới van relief hay sờ đường dầu áp cao để thử.'

**CAPY:** 'Vậy mấy cái van an toàn mới là đội bảo vệ của dàn cơ bắp thủy lực!'

## SC12 — 08:55–09:50 | ĐIỆN TỬ CÓ THAM GIA KHÔNG?

**Hình:** Cảnh cabin monitor, engine controller, pump controller, solenoid EPC, feedback pressure/speed; sơ đồ 'engine + hydraulic + electronics' không mô tả dây điện chính xác theo máy chưa biết serial.

**CAPY:** 'Nhưng tui học ô tô, tui muốn tìm ECU cơ! Hệ thống thủy lực này có điện tử không?'

**ANH KỸ SƯ:** 'Có. Một số tín hiệu vận hành từ động cơ, cảm biến và bộ điều khiển được dùng để phối hợp công suất động cơ với yêu cầu thủy lực, điều khiển van điện từ và chế độ làm việc. Ở hệ CLSS, LS/PC và EPC là những đầu mối cần học kỹ. Nhưng sơ đồ dây, cổng điện và hiệu chỉnh phải tra đúng shop manual của phiên bản máy, chứ không đoán theo một ảnh trên mạng.'

## SC13 — 09:50–10:50 | TẠI SAO MÁY LẠI CHẬM / YẾU?

**Hình:** Capy đi cạnh máy đang dừng; màn hình hiện 4 nhóm giả thuyết bằng hoạt hình nhỏ: động cơ không đủ công suất; bơm/điều khiển bơm; van/cảm biến/pilot; dầu/ống/lọc/nhiệt và cơ cấu. Không làm cảnh sửa máy khi chưa có thợ và biện pháp an toàn.

**CAPY:** 'Vậy nếu một ngày máy đào tự nhiên yếu, gầu lên chậm, có phải hư bơm không anh?'

**ANH KỸ SƯ:** 'Chưa thể kết luận. Phải tách khả năng động cơ thiếu công suất; điều khiển bơm hoặc tín hiệu LS bất thường; van phân phối, pilot, rò rỉ bên trong, lọc dầu, nhiệt độ dầu; thậm chí ma sát cơ khí. Quan trọng là biểu hiện khi nâng cần, co tay gầu, quay toa và chạy xích có giống nhau hay khác nhau. Đo và đối chiếu đúng quy trình an toàn mới khoanh vùng được, chứ không thay bơm chỉ vì thấy máy chậm.'

## SC14 — 10:50–11:35 | KẾT VÀ KÉO SANG TẬP 3

**Hình:** Camera trở về studio, Capy cầm ly BK; sơ đồ toàn hệ thống tự sáng từng nhánh; hình máy đào ngoài công trường thu lại như ảnh trong sổ học tập.

**CAPY:** 'Để tui tổng kết nha! Động cơ cho năng lượng, hai bơm biến thành dòng dầu, CLSS giúp điều chỉnh theo tải, van phân phối, xi lanh và mô tơ tạo chuyển động. Dầu còn phải về lọc, làm mát, có van bảo vệ nữa. Hóa ra không phải cái gầu khỏe — mà nguyên hệ thống đang phối hợp!'

**ANH KỸ SƯ:** 'Chính xác. Và đó mới là bản đồ tổng thể. Muốn giải mã đến từng cổng, từng spool hay mã lỗi của PC200-8, mình sẽ phải xem đúng serial và sơ đồ hãng.'

**CAPY:** 'Tập sau mình thử xem CLSS điều khiển bơm thế nào và vì sao máy có lúc bị ì nha! Bye bye!'

---

## SHOT REQUIREMENTS / CODEx HANDOFF

- **Master format:** YouTube 1920×1080 30fps; cắt riêng TikTok 1080×1920, bố cục phải dựng lại cho dọc (không crop mù những sơ đồ rộng).
- **Voice:** Capy + engineer WAV separate, exact confirmed voice IDs retained by owner; sound logo original owner-approved private (KHÔNG commit raw private voice lên repo public).
- **Animation rigs:** 3 links boom/arm/bucket rigid, 4 cylinder assemblies with telescoping rods, body rotation independent of tracked undercarriage, track links animate along closed path, oil routes segmented with directional highlights. Optional simplification if no kinematic solver: show one actuator at a time; never fake rod length at fixed endpoints.
- **Visual language:** oil high-pressure red; return blue; pilot orange; LS purple; electronic signal green dashed. Note the color convention is editorial, not factory wire color.
- **Mandatory legal banner:** 'Minh họa nguyên lý — chi tiết cụ thể theo serial và cấu hình máy.'
- **No misleading claims:** do not say pumps 'create pressure regardless of load'; don't equate ideal piston force with bucket lift capability; don't use PC200-8M0 documents as exact PC200-8 drawing without checking differences. No sensitive field data/owner machine ID/customer material uploaded to public repo.
- **DRAFT QA:** technical reviewer verifies numerical data, symbols, machine configuration; owner approves narrative; Codex makes sample 20–30s (piston+valve+boom) before 11-minute production. CapCut Pro manages licensed music/SFX, subtitles, final render. No AI voice generated as part of this script file.

## REFERENCED PUBLIC SOURCES (for independent verification)

1. Komatsu PC200-8 product brochure, CEN00049-08, HydrauMind CLSS, pump/motor, nominal circuit relief values, cylinder bore: https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf
2. PC200-8 Shop Manual SEN00084 series; sections 401 Hydraulic System 1 (SEN00099), 402 Hydraulic System 2 (SEN00100), 403 Hydraulic System 3 (SEN00160): https://www.manualslib.com/manual/2507934/Komatsu-Pc200-8.html
3. PC200-8M0 manual for comparative context ONLY, not a replacement for standard -8: https://www.manualslib.com/manual/1665308/Komatsu-Pc200-8m0.html

**Unverified:** The actual serial, serial-specific circuit and aftermarket modifications of any on-site PC200-8. Do not imply all public brochure specs apply unchanged to that individual machine.
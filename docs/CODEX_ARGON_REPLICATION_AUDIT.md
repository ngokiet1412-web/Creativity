# Codex audit of the Argon engineering pipeline

Ngày kiểm tra 2026-11-17, múi giờ Asia/Bangkok. Trạng thái DRAFT để owner duyệt tích hợp.

Pipeline NX → MATLAB → Blender của Argon có thể tái sử dụng cho hoạt hình cơ cấu. Chạy lại MATLAB tái tạo đúng bảng chuyển động đã nộp. Kiểm tra độc lập trên file Blender xác nhận quan hệ trục và chiều dài liên kết trong dung sai 0,25 mm qua 1.079 trạng thái. Tuy nhiên, kiểm tra Boolean trên CAD gốc xác nhận giao khối ở ba cặp cụm được thử. Nghiệm thu hình học lắp ráp cần bổ sung trước khi công bố cơ cấu hoạt động đúng thực tế.

## Phiên bản và phạm vi thực sự đã đọc

Đóng băng PR #15 tại `51f10d630fe32b40d1501500c4a989ac8259a959`, nhánh `argon/ep02-v7-nx-blender-cinematic`. Main dùng để đọc handoff là `491bc6372d739f0bd7a3a9521264cbd4a0c114af`. Báo cáo nằm trên nhánh `codex/argon-replication-audit`. [PR #15](https://github.com/ngokiet1412-web/Creativity/pull/15)

Đã đọc toàn bộ năm file mã thực thi trong PR, gồm `inventory_nx_v2.py`, `export_nx_v2_parts_for_blender.py`, `solve_ep02_v3_motion.m`, `build_ep02_v3_cinematic.py`, `materials_v3.py`, cùng manifest, CSV, JSON QA, log và bốn tài liệu giải thích. Đã đối chiếu thêm `geometry_v2_argon.py` và `nx_pilot_v2_argon.py` của nguồn NX cục bộ. Các file mã cục bộ tương ứng PR có cùng nội dung sau khi chuẩn hóa xuống dòng. SHA theo byte khác do cách lưu xuống dòng, vì vậy mọi tham chiếu mã bên dưới trỏ đến commit cố định.

Đã mở `.blend` bằng Blender background với `--disable-autoexec`, mở assembly NX bằng journal, chạy MATLAB trong bản sao tạm, kiểm tra 53 STL cục bộ và hash 40 file `.prt` so với inventory. Cả 40 hash đều khớp. File Blender được kiểm tra là `EP02_PC2008_V3_CINEMATIC.blend`, SHA-256 `d3b508611db006f580deae1afb17176d9a8fdcf6e48631993d7a7aa234db7147`. Các file V7.1 hiện có trên máy nằm ngoài phạm vi phiên bản này.

## Kiến trúc và cách tái sử dụng

| Tầng | Dữ liệu vào và cách thực hiện | Đầu ra và kỹ thuật nên giữ |
| --- | --- | --- |
| Inventory | Liệt kê `.prt`, STEP, CSV, log và script, tính SHA-256 | Danh mục nguồn có hash và phân loại giúp xác định đúng phiên bản CAD |
| NXOpen | Mở từng part, lấy solid từ `part.Bodies`, ánh xạ qua `feature.GetBodies()`, phân nhóm theo tên feature | 24 part nguồn → 42 STL phân nhóm và 11 STL toàn part dùng so sánh |
| Tessellation | `DexManager.CreateStlCreator`, binary STL, chordal 0,08 mm, adjacency 0,025 mm, tự tạo normal | 52.746 tam giác trong các nhóm chính. Manifest lưu số body, bounding box và datum |
| MATLAB | Kiểm ba tư thế theo CSV NX, giải động học thuận và giao hai đường tròn cho cơ cấu bốn khâu | Một trace 540 hàng điều khiển animation và kiểm dày hơn ở 120 Hz |
| Blender | STL theo vai trò, scale 0,001 áp vào vertex, parent theo chốt, xi lanh và thanh liên kết dùng `LOCKED_TRACK` | Mesh có tên và vật liệu riêng, khung kim loại giữ tỷ lệ, chuyển động đi qua đúng pivot |
| Hình ảnh | Shader thủ tục, bevel nhỏ, normal/cạnh sắc, đèn key/fill/rim, camera theo nhịp giải thích | Thư viện vật liệu và các bố cục hero, cận xi lanh, phân rã, mặt cắt có thể dùng lại |
| QA và đóng gói | CSV kiểm từng frame và midpoint, JSON tổng hợp, ảnh PNG, MP4 đóng gói bên ngoài Blender | Bằng chứng theo từng tầng, dễ tìm điểm sai mà không phải dựng lại toàn bộ |

NX kiểm tổng số tag và số tag duy nhất sau phân nhóm, nên có chốt chặn bỏ sót hoặc gán trùng body. Với dữ liệu hiện tại, tất cả 53 STL đều đúng số tam giác và độ dài binary `84 + 50 × n` so với manifest. Số 53 bao gồm bản toàn part phục vụ QA. Tổng tam giác 52.746 chỉ cộng nhóm chính. Blender gọi tên nhóm cần nhập trực tiếp nên tránh nạp thêm toàn part trùng hình. Khi tái sử dụng, nên bổ sung phép so sánh tập tag đầu vào/đầu ra và hash STL, thay vì chỉ kiểm số lượng. [NX exporter, dòng 97–165 và 218–253](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/cad_exchange/export_nx_v2_parts_for_blender.py#L97)

MATLAB hiện đọc `pose_check.csv` và `joint_map.csv` làm đối chứng, trong khi hằng số hình học được khai báo trực tiếp trong `.m`. Blender cũng khai báo lại kích thước và tọa độ chốt. Trace là nguồn thời gian chung nhưng chưa có một nguồn tham số duy nhất xuyên suốt ba phần mềm. Đây là điểm tích hợp nhỏ cần ưu tiên khi đổi loại máy hoặc đổi bản CAD. [MATLAB, dòng 17–44](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/animation/solve_ep02_v3_motion.m#L17)

## Hệ tọa độ, rig và bất biến

NX dùng mm, Blender dùng m. Gốc tại chốt chân cần, X hướng về cụm công tác, Y ngang máy, Z lên. `Matrix.Scale(0.001, 4)` tác động lên mesh, sau đó object scale bằng một. `forward_axis="Y", up_axis="Z"` trong lời gọi STL import phù hợp quy ước nhập của Blender đang sử dụng. Các điểm thế giới đã kiểm xác nhận cách nhập này giữ quan hệ X/Z mong muốn. Phép quay dương trong mặt phẳng XZ tương ứng Euler Y âm trong Blender. [Nhập và chuẩn hóa mesh, dòng 52–113](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/blender_project/build_ep02_v3_cinematic.py#L52)

`Pivot_BoomBase` mang cần, `Pivot_BoomTip` là con của cần tại X = 5,700 m, `Pivot_StickTip` là con của tay gầu tại X = 2,925 m. Góc local lần lượt bằng `-boom`, `+arm_relative`, `bucket_relative - 90°`. Chốt gối bốn khâu lấy tọa độ thế giới từ trace. Mỗi vỏ xi lanh hướng +X từ chốt chân tới chốt ty, mỗi ty hướng +X ngược lại. `LOCK_Y` giữ trục ngang, phù hợp cơ cấu phẳng này. Máy có cơ cấu lệch mặt phẳng hoặc xoay thêm bậc tự do sẽ cần định nghĩa lại hướng khóa. [Rig, dòng 909–987](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/blender_project/build_ep02_v3_cinematic.py#L909)

| Bất biến | Đơn vị và phép kiểm | Phạm vi chứng minh |
| --- | --- | --- |
| Cần/tay gầu | Khoảng cách pivot 5.700/2.925 mm | Đúng tham số concept đã chọn |
| Bốn khâu | Khoảng cách side–knee 650 mm, boss–knee 750 mm | Khép vòng và chọn cùng nhánh nghiệm |
| Xi lanh | Khoảng cách hai chốt trừ chiều dài đóng nằm trong stroke | Hợp lệ với chiều dài đóng giả định |
| Đồng trục | Vector +X sau constraint trỏ tới chốt đối diện | Vỏ và ty theo cùng đường trục |
| Tỷ lệ | Scale thế giới của mesh cơ khí xấp xỉ một | Không phát hiện biến dạng bằng scale trong tập được kiểm |
| Va chạm | Boolean giao solid giữa các cụm | Cần phép kiểm riêng, độc lập với tâm chốt |

## Kết quả kiểm tra độc lập

Các kiểm tra dưới đây chạy ngày lập báo cáo. MATLAB dùng bản sao từ commit cố định. Bộ tính Python dùng NumPy và SciPy `CubicSpline` với điều kiện biên clamped, tự viết lại phép quay và động học, không gọi `evaluate_pose` của Argon. Bộ kiểm Blender đọc scene có sẵn, không gọi hàm QA của Argon và không render.

| Kiểm tra | Kết quả đo lại | Đánh giá |
| --- | --- | --- |
| Mở NX Reach | 0 unloaded part, 27 occurrence, 11 constraint | PASS mở assembly hiện hữu |
| STL | 24 part, 42 nhóm + 11 toàn part, 53 file đúng binary length/count | PASS kiểm cấu trúc exchange, chưa chứng nhận sai số bề mặt CAD–mesh |
| Chạy MATLAB R2026b | `motion_trace_v3.csv`, `joint_map_v3.csv`, JSON QA trùng nội dung commit sau chuẩn hóa xuống dòng | PASS tái chạy thực tế |
| MATLAB với CSV ba pose NX | Max distance error 3,93471e-7 mm, coordinate error 6,71697e-7 mm | PASS đối chiếu nội bộ |
| Python độc lập, 540 hàng | Max coordinate difference 1,09139e-11 mm, max angle difference 5,54223e-13° | PASS tái lập toán học |
| Python độc lập, 2.161 mẫu | Min clearance theo hull 83,380142 mm, min overlap 398,343420 mm, max closure 1,02318e-12 mm | PASS trong mô hình này. Chênh mức làm tròn so với MATLAB 9,09495e-13 mm |
| Stroke tại 120 Hz | Boom 572,054280–859,807578 mm, arm 272,470938–471,213934 mm, bucket 878,301541–981,656580 mm | PASS trong giới hạn khai báo |
| Lưu lượng tính độc lập | Sai khác cap ≤ 1,73e-11 L/min, rod ≤ 8,61e-12 L/min | PASS công thức lưu lượng lý tưởng một xi lanh |
| Blender 5.3, 1.079 trạng thái | 13 origin mesh chốt trùng pivot, max link error 0,003477 mm, max axis endpoint error 0,000992 mm | PASS dưới 0,25 mm. Chưa đo tâm lỗ thực trên bề mặt mesh |
| Scale thế giới, mesh cơ khí trong collection 02–07 | Max deviation 3,57628e-7 | PASS gồm cả nhóm linkage mà danh sách QA gốc bỏ sót |
| Gầu thực, vertex mesh trước modifier | Min clearance tới mặt phẳng Z = −1,5849 m là 195,772671 mm tại frame 1 | Khác hull MATLAB 83,380142 mm. Cả hai đều dương |
| Bốn hose tại Reach | Endpoint dữ liệu curve đã evaluate trùng origin ferrule | PASS tại tư thế này. Chưa kiểm bán kính uốn, va chạm hoặc mọi thời điểm |
| MP4 cục bộ | H.264, 1.920 × 1.080, 30 fps, 540 frame, 18 s, 11.869.604 byte, giải mã hết thành công, không có audio stream | PASS metadata/decode |

Matlab Trial chạy được và báo còn 6 ngày tại thời điểm kiểm. Đây là tình trạng runtime hiện tại, không phải xác nhận quyền sử dụng lâu dài hay sản xuất thương mại. Blender báo 5.3.0, build `02f0899d78e3`. Lượt audit chỉ mở và kiểm file, chưa benchmark lại GPU/render hoặc xác thực hợp đồng license NX.

## Phát hiện và cải tiến nhỏ đề xuất

**1. Giao khối CAD vẫn tồn tại dù tâm chốt khớp.** Đã chạy 280 Boolean test ở Reach trên ba cặp cụm nguồn V2. Boom–boom rod phải có 5 cặp body giao nhau trong 80 test, boom–arm barrel có 10/144, side link–H-link có 8/56. Không có lỗi NX trong các test. Đây là số cặp body, không phải số vùng va chạm độc lập. PR #15 lấy mesh và tọa độ từ `NX_NATIVE_V2_ARGON_20261116`. Nhánh sửa fit ở PR #14 là phiên bản khác, chưa được đưa vào pipeline này. Phần giải thích exploded view chỉ giải thích các chi tiết tách xa trong file phân rã, chưa xử lý các giao khối trong assembly lắp. Cần chọn một revision CAD, xuất lại đúng nhóm STL bị ảnh hưởng và đồng bộ tọa độ MATLAB/Blender trước khi kiểm lại. [Nguồn CAD của exporter](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/cad_exchange/export_nx_v2_parts_for_blender.py#L168)

**2. Ý nghĩa QA rộng hơn phép đo thực tế.** `pin_dev_mm` chỉ đối chiếu X/Z của bốn empties tại frame nguyên. Midpoint ghi 0 vì không thực hiện phép đối chiếu đó. `min_bucket_ground_clearance_mm` lấy từ CSV, không đo gầu Blender. Kiểm scale gốc đọc local scale và bỏ nhóm four-bar trong `metal_objs`. Đề xuất ghi midpoint chưa đo là null, thêm số lượng mẫu thực đo mỗi metric, kiểm scale thế giới và tách metric hull/mesh/va chạm. Đo lại ở đây xác nhận rig hiện tại đạt các bất biến đã nêu, đồng thời làm rõ giới hạn của PASS. [QA, dòng 748–821](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/blender_project/build_ep02_v3_cinematic.py#L748)

**3. Spline nối sang hold không liên tục gia tốc.** Tại t = 16,8 s, đạo hàm bậc hai từ bên trái của ba góc lần lượt khoảng −0,562382, −0,751770 và −0,654642 °/s². Đoạn hold có gia tốc bằng 0. Điều kiện clamped giữ vận tốc đầu/cuối bằng 0 nhưng không buộc gia tốc bằng 0. Mô tả C2 đúng trong đoạn spline, còn đường nối hold chỉ đạt C1. Đề xuất sửa ngắn đoạn hãm cuối với điều kiện cả vận tốc và gia tốc bằng 0 rồi kiểm lại jerk/stroke, giữ các pose đã duyệt. [Clamp thời gian và spline, dòng 299–307](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/animation/solve_ep02_v3_motion.m#L299)

**4. Thể tích dầu MATLAB và hình khoang Blender chưa dùng chung kích thước.** Gọi L là khoảng cách chốt boom cylinder, đơn vị mm. MATLAB dùng chiều dài khoang đáy `L − 1900`, khoang ty `3760 − L`. Blender dùng `L − 2172` và `3956 − L`. Khoang đáy lệch 272 mm, tương ứng 3,07625 L nếu cùng tiết diện bore 120 mm. Riêng khoang ty Blender gồm đoạn wear ring/piston phụ nên cần định nghĩa lại mặt biên khoang trước khi đối chiếu thể tích. Bán kính dầu minh họa 58,5 mm và lỗ 43,2 mm cũng khác tiết diện thủy lực dùng tính Q. Đề xuất một bảng vị trí head/piston/gland chung, với lớp hiển thị dầu được gắn nhãn minh họa. Giữ `Q = A·v` với đơn vị m², m/s và hệ số 60.000 sang L/min. Twin boom cần cộng hai nhánh khi trình bày tổng lưu lượng. [MATLAB khoang dầu, dòng 350–360](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/animation/solve_ep02_v3_motion.m#L350), [Blender khoang dầu, dòng 720–728](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/blender_project/build_ep02_v3_cinematic.py#L720)

**5. Một số mô tả cần sinh từ dữ liệu.** Tài liệu báo 13 vật liệu nhưng file mở có 17. Tài liệu ghi dải arm/bucket khác JSON và kết quả replay. `duration_s` trong JSON là timestamp cuối 17,966667 s, trong khi 540 frame có thời lượng phát 18 s. Các giá trị đều có thể diễn giải được nhưng nên đặt tên `last_sample_time_s`, `playback_duration_s` riêng. Blender kiểm 1.079 trạng thái ở frame nguyên/nửa frame, tương đương lấy mẫu 60 Hz tới t = 17,966667 s. MATLAB kiểm 2.161 mẫu tới 18 s ở 120 Hz. Hai tập kiểm có mục đích khác nhau.

**6. Khả năng tái chạy từ checkout cần cấu hình đường dẫn và bằng chứng đầu vào.** Default path của NX exporter giả định workspace nằm cạnh thư mục CAD cục bộ. Clone repo không có bộ STL/native. `open_readonly` dùng API mở part thông thường, không bật một chế độ read-only cưỡng chế. Script không gọi save nhưng `CloseAll` có thể đóng tài liệu đang mở nếu chạy trong GUI. Đề xuất chạy bằng process journal riêng, thêm tham số `--source-dir/--output-dir`, preflight dependency, hash input/output và kiểm `PartLoadStatus`. Ghi lệnh encode FFmpeg vào manifest để tái tạo MP4. [Quản lý part, dòng 16–40](https://github.com/ngokiet1412-web/Creativity/blob/51f10d630fe32b40d1501500c4a989ac8259a959/episodes/EP02/blender_v3_argon/cad_exchange/export_nx_v2_parts_for_blender.py#L16)

## Giới hạn độ chính xác PC200-8 và quyền sử dụng

Source register phân biệt rõ boom/arm danh nghĩa 5.700/2.925 mm với khoảng cách tâm chốt đang giả định cùng giá trị. Bộ xi lanh khai báo bore/stroke/rod lần lượt 120/1334/85 mm, 135/1490/95 mm và 115/1120/80 mm cho cấu hình đã chọn. Các phép kiểm trên chỉ xác nhận ba chương trình sử dụng nhất quán bộ số này. Độ chính xác OEM vẫn cần tọa độ chốt, chiều dài đóng thực, tai gá, linkage, tiết diện, dung sai và cấu hình máy tương ứng. Truy cập lại brochure trong lượt audit bị timeout hai lần, nên việc xác nhận trực tiếp trang nguồn hôm nay còn BLOCKED. Giá trị nguồn trong báo cáo dựa trên register và bằng chứng kiểm trước đó. [CAD Source Register](../episodes/EP02/CAD_SOURCE_REGISTER_PC2008.md), [brochure Komatsu CEN00049-08](https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf)

Đường áp suất được tác giả ghi rõ là minh họa và mã dùng hàm phụ thuộc góc/vận tốc. Pipeline chưa giải tải, mô men, tổn thất, bơm–van, LS/PC, nén dầu, lực xi lanh hoặc động lực học đất. C2 hoặc sai số khép vòng rất nhỏ chỉ xác nhận tính chất toán học. Không thể suy ra cảm giác trọng lượng, khả năng chịu lực hay độ chính xác thủy lực của máy từ các metric đó.

Mã đã đọc dùng asset CAD concept cục bộ, vật liệu thủ tục và Bfont. Không thấy bước tải model hoặc texture bên ngoài trong các script này. Đây là kiểm tra nguồn triển khai, chưa thay thế chứng từ quyền sở hữu hay điều khoản license thương mại của toàn bộ tài sản. Nội dung CAD native, STEP, STL, blend và log chứa đường dẫn máy được giữ ở bộ bằng chứng cục bộ.

## Quan sát hình ảnh và video

Đã xem cả bốn PNG ở độ phân giải gốc. Hash bốn ảnh cục bộ khớp ảnh trong commit. SHOT_01 cho thấy rõ silhouette cụm công tác và bệ thử, SHOT_02 làm rõ chrome và gland, SHOT_03 xếp các chi tiết dọc trục dễ theo dõi, SHOT_04 phân biệt hai khoang bằng màu và có nhãn mặt cắt minh họa. Các lựa chọn này nên được giữ khi tích hợp Capy. Cụm đang đặt trên bệ thử, phạm vi asset chưa gồm chassis, cabin và bánh xích của máy hoàn chỉnh.

Video đã được giải mã toàn bộ và kiểm hình lấy mẫu mỗi giây trên cả 18 s. Chuỗi cho thấy cần thực sự nâng, camera tiến vào xi lanh, mặt cắt xuất hiện khoảng 8–14 s rồi camera rút ra. Việc xem ảnh lấy mẫu chưa đủ để kết luận độ mượt ở từng frame, âm thanh hoặc nhịp thoại. MP4 hiện có không có audio stream. Mặt cắt và mũi tên vẫn cần được hiểu là hình nguyên lý.

## Kế hoạch tích hợp có giới hạn

1. Chốt revision CAD và ghi `cad_revision`, hash, đơn vị, hệ trục, `parameter_status` vào manifest. Đưa các tọa độ chốt và chiều dài đóng vào một bảng dùng chung. Khi áp dụng sửa fit PR #14, tái xuất các part đổi và cập nhật cả solver lẫn rig theo cùng bảng.
2. Tái sử dụng bộ chia solid, kiểm phân hoạch, STL theo vai trò và vật liệu. Thêm xác thực hash, bounding box và metadata source cho mỗi nhóm. Các episode máy khác chỉ cần bộ tham số và ánh xạ feature mới.
3. Giữ solver phẳng, cách giải bốn khâu, trace và kiểm 120 Hz cho cơ cấu tương thích. Bổ sung test đổi nhánh nghiệm, toggle, biên stroke, đoạn hãm/hold và metric sai khác khi thay một pin ±10 mm. Sai khác nguồn phải làm preflight thất bại thay vì chấp nhận âm thầm.
4. Giữ rig parent theo pivot và barrel/rod cứng. Mở rộng QA gồm world scale, pin reference ở mọi mẫu, mặt biên khoang dầu, mesh clearance và tập cặp collision có quy định tiếp xúc hợp lệ. Đặt tên metric theo đối tượng thực đo.
5. Chỉ sau khi các thay đổi nhỏ đạt kiểm tra, tạo một preview ngắn theo yêu cầu owner. Tận dụng bốn bố cục và vật liệu hiện tại cho bước tích hợp Capy, giọng và SRT. Báo cáo này chưa phê duyệt dựng lại cả tập hoặc nghiệm thu CAD OEM.

## Bằng chứng cục bộ và cách tái kiểm

Các script kiểm độc lập và log của lượt audit được lưu ở `D:/Creativity_CAPY_BK_EP01_Assets_For_Codex/CAPY_BK_EP02_NX_CODEX_PILOT/CODEX_ARGON_AUDIT_20261117/`. Bộ gồm `independent_math.py/.log`, `independent_blend.py/.log`, `matlab_replay.log`, `nx_check_helpers.py`, `nx_selected_audit.py`, `nx_recheck.log`, hai CSV Boolean và `video_decode.log`. Script Python toán tham chiếu snapshot tạm `codex-argon-pr15-51f10d6` dưới TEMP. Khi tái kiểm trên máy khác, tạo snapshot từ commit đã khóa và cập nhật root trong bản sao script audit.

Chạy MATLAB bằng `matlab.exe -batch` với `addpath` trỏ tới `animation` trong snapshot, rồi gọi `solve_ep02_v3_motion(snapshot_root)`. So sánh nội dung CSV/JSON sinh lại với `git show 51f10d6:<path>`. Kiểm Blender bằng `blender.exe --background <V3.blend> --disable-autoexec --python <independent_blend.py>`. Kiểm NX bằng `run_journal.exe <nx_selected_audit.py>`, đặt `CAPY_FIT_INPUT` vào thư mục V2 và `CAPY_FIT_AUDIT_OUT` vào thư mục bằng chứng mới. Audit NX thực hiện Boolean trong bộ nhớ rồi undo và đóng part. File CSV output phải chưa tồn tại. Kiểm MP4 bằng FFmpeg giải mã toàn bộ sang null output.

Chỉ file báo cáo này là thay đổi repo của lượt audit. Các phép replay và kiểm tra ghi kết quả vào snapshot/bộ bằng chứng cục bộ.

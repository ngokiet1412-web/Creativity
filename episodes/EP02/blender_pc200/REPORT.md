# EP02 · PC200-8 · thử nghiệm Blender 2.5D (DRAFT)

Một cảnh minh họa 9 giây, 1920 × 1080, 30 fps. Máy hạ gầu đang có đất xuống sát nền, khép gầu, nâng tải rồi hãm nhẹ và giữ. Góc máy ngang tiến vào nhẹ để nhìn cơ cấu. Clip thử hình không có thoại hoặc nhạc.

## Blender và tài nguyên

- Máy Dell Precision 7560 chạy Blender 5.3.0 (build `02f0899d78e3`) tại `C:\Program Files\Blender Foundation\Blender 5.3\blender.exe`. Lệnh `-b --python-expr` tạo object, đặt tọa độ bằng `mathutils`, chèn keyframe và kiểm tra action thành công. Blender có Python 3.13.13 và NumPy 2.3.4. Máy ghi nhận Xeon W-11855M, RAM 32 GB và RTX A3000 Laptop 6 GB. Dùng EEVEE và FFmpeg có sẵn.
- Năm PNG tách lớp `upper`, `undercarriage`, `boom`, `arm`, `bucket` và nền `worksite.png` dùng nguyên bản từ `../demo_v4/godot/art/`. Nguồn là atlas và phông ImageGen của dự án ngày 2026-11-12, tiếp nối nét vẽ EP01, trạng thái DRAFT. Từng layer gắn vào chốt và đổi tỷ lệ đều khi nhập. Cả sáu ảnh đã nhúng vào `.blend` để mở được khi chuyển file. [Manifest V4](../demo_v4/ASSET_MANIFEST.md) · [Prompt và nguồn V2](../demo_v4/godot/art/source/PROVENANCE_codex_v2.md).
- Dùng lại `art/rig.json` và hàm động học thuận trong `tools/kinematics.py` của Godot. Chiều dài cần 5,70 m và tay gầu 2,925 m theo cấu hình đã chọn. Tọa độ các tai xi lanh, chiều dài đóng, cơ cấu gầu và đường kính hình vẽ là tham số minh họa. [Brochure Komatsu PC200-8/PC200LC-8 CEN00049-08](https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf).
- Xi lanh, chốt, tai treo, hai thanh dẫn gầu, đèn và bóng được tạo bằng Python trong Blender cho cảnh thử ngày 2026-11-16. Từng vỏ và ty là mesh chiều dài cố định, xoay theo hai chốt bằng ràng buộc Damped Track. Hai xi lanh cần dùng cùng hình chiếu chốt nhưng nằm ở hai lớp chiều sâu. Thân và đất giữ màu vẽ gốc, còn phần cơ khí nhận đèn ấm phía trên trái và ánh trời hắt nhẹ.
- Art hiện có phù hợp với góc ngang và cận vừa. Cabin, xích và gầu là hình vẽ một góc, đổi sang góc nhìn chéo lớn sẽ lộ mặt phẳng. Hình gầu đã có đất vẽ sẵn, nên cảnh bắt đầu sau khi lấy đất. Nhịp hạ–khép–nâng do keyframe điều khiển, có lấy đà và giảm tốc, chưa mô phỏng lực hay đất rời.

## Kiểm tra hình học

270 khung xuất và 807 mẫu giữa khung (tổng 1.077 mẫu). Đọc transform đã tính của Blender rồi đối chiếu với động học dùng chung.

| Phép kiểm | Kết quả |
|---|---|
| Khoảng cách hai chốt cần và tay gầu | 5,70 m và 2,925 m, giữ nguyên |
| Thanh dẫn bên và thanh chữ H | 0,65 m và 0,75 m, khép được ở mọi mẫu |
| Sai lệch chốt hoặc trục lớn nhất | 0,0045 mm với ngưỡng kiểm tra 0,1 mm |
| Phần ty đi ra so với vị trí đóng, cần (cả hai) | 0,547–0,846 m trong hành trình 1,334 m |
| Phần ty đi ra, tay gầu | 0,467–0,623 m trong hành trình 1,490 m của rig |
| Phần ty đi ra, gầu | 0,974–1,103 m trong hành trình 1,120 m |
| Khoảng hở nhỏ nhất giữa biên gầu và cao độ nền | 0,043 m theo mô hình |

Các vỏ và ty luôn còn phần lồng vào nhau. Mở lại file bằng Blender và kiểm tra đủ sáu ảnh đã nhúng, scene EEVEE, 270 khung và scale (1,1,1) của toàn bộ lớp và chi tiết rig. Sai số trên nói về tính khép kín của rig minh họa.

## So với Godot của EP02

| | Godot EP02 V13, cảnh SC05 khoảng 3:38–4:14 | Blender proof 9 giây |
|---|---|---|
| Hình học | Lớp 2D quay quanh chốt, cùng bộ tham số và cùng lời giải động học. | Giữ quan hệ chốt, thay phần xi lanh vẽ bằng vỏ, ty và tai bắt có chiều sâu dựng được trong Blender. |
| Hình và ánh sáng | Viền và bóng vẽ hợp nét phim. Nhãn, vòng chốt và mũi tên giúp theo dõi bài giảng. | Giữ hình vẽ máy và nền, ánh sáng phản trên ty và các cạnh kim loại, giữ khuôn hình xoay quanh hành động khép gầu và nâng tải. Một số tai bắt vẫn ít chi tiết hơn phần máy vẽ sẵn. |
| Nhịp | Lần lượt bật từng khâu để minh họa lời giảng, có host và phụ đề. | Hạ thấp trước khi khép, ngừng ngắn rồi nâng, có một nhịp hãm. Shot chỉ kiểm chứng chuyển động máy. |
| Sử dụng | Tái dùng đường dầu, lớp thuyết minh và hệ thống sản xuất của cả tập. | Có thể chọn góc khung và sửa ánh sáng/chi tiết cơ khí. Nếu đổi chuyển động gầu, chạy lại script để tính chuỗi chốt J theo cơ cấu bốn khâu. |

Blender phù hợp cho cận cảnh cơ khí như ty xi lanh hoặc tai chốt, chèn vào mạch Godot khi cảnh cần thấy rõ độ dày và ánh sáng. Cảnh này chưa kiểm chứng bố trí đường dầu, quay toa hay vận hành bánh xích.

Trên Dell 7560, EEVEE mất 280,49 giây để xuất 270 PNG Full HD ở 16 mẫu, tính cả khởi động và ghi file. Log Godot V10 SC01 ghi 1.218 khung trong 81 giây khi xuất AVI ở thiết lập của scene đó. Hai mốc thời gian là số đo thực tế của hai công việc khác nhau, với định dạng đầu ra khác nhau. MP4 Blender H.264 có 270 khung và dài 9,000 giây. FFmpeg giải mã hết video thành công. Ảnh đối chiếu `EP02_PC200_SO_SANH.jpg` ghép Godot V13 tại 3:58 với khung nâng tải ở 5,97 giây của demo.

## Dựng lại và chỉnh sửa

Mở `EP02_PC200_BLENDER_DRAFT.blend` trong Blender 5.3. Timeline có mốc Lower, Curl, Lift, Ease out và Hold. Muốn đổi góc nhìn, chọn Camera. Muốn đổi nhịp hoặc góc khớp, sửa `POSES` ở `build_shot.py`, sau đó dựng lại để chốt J, các thanh dẫn và kiểm tra hình học cập nhật cùng nhau. Các constraint xi lanh nằm sẵn trong file, không cần bật auto-run Python để mở.

Từ gốc repo, chạy PowerShell. Lệnh thứ nhất dựng file và xuất `geometry.csv`. Lệnh thứ hai render PNG. Dùng đường dẫn FFmpeg đã có ở máy cho lệnh thứ ba.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe'
$out = 'build/EP02_blender_pc200'
$ffmpeg = (Resolve-Path '../.capy-tools/python/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe').Path
& $blender -b --factory-startup --python-exit-code 7 --python episodes/EP02/blender_pc200/build_shot.py -- --out $out
& $blender -b "$out/EP02_PC200_BLENDER_DRAFT.blend" -o '//frames/pc200_' -F PNG -a
& $ffmpeg -framerate 30 -start_number 1 -i "$out/frames/pc200_%04d.png" -frames:v 270 -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart "$out/EP02_PC200_BLENDER_DRAFT.mp4"
```

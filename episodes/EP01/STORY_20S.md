# EP01 · Capy BK lái máy xúc

**DRAFT / OWNER REVIEW** · 20 giây · 1080×1920 · 30 fps

| Thời gian | Cảnh |
|---|---|
| 00:00–00:04.60 | Mở thẳng trong cabin. Capy cầm hai cần điều khiển, kim dầu tụt và Capy bật ra câu hỏi. |
| 00:04.60–00:07.50 | Máy xúc bò trên dốc. Góc máy theo xe, cần gầu rung nhẹ, bụi đất và tiếng máy chạy. |
| 00:07.50–00:12.50 | Cắt vào bình dầu giả định, bình nghiêng trong khi mặt dầu nằm ngang. Cảm biến gần đầu nâng lên thấy độ sâu giảm. |
| 00:12.50–00:17.60 | Capy đứng cạnh máy đã đỗ và nói với người xem. |
| 00:17.60–00:20.00 | Capy trở lại studio gốc, nhún người chốt câu. |

Ba khung hình cabin, máy xúc và Capy đứng cạnh xe được tạo bằng **ImageGen tích hợp**, dùng ảnh Capy đã duyệt làm tham chiếu. Chúng nằm trong `build/story-plates/`. [Manifest cảnh](story_20s.json) lưu prompt đầy đủ, nguồn, SHA-256 và trạng thái DRAFT của từng khung. Cảnh studio dùng GIF gốc và giữ cả ly lẫn bảng BK. Cảnh ngoài và cabin dùng chuyển động 2.5D từ các khung đã tạo. Sơ đồ bình dầu dùng hình học chiếu 3D.

Giọng nam Điềm Đạm là giọng tổng hợp dùng trong bản duyệt. Lời thoại chia thành các câu ngắn với dấu câu và khoảng ngắt dành cho diễn xuất. Khẩu hình cabin, cảnh đứng và studio theo mốc âm vị. Các stem âm thanh 48 kHz để riêng cho dựng CapCut. [Nguồn giọng](https://huggingface.co/vnhellboy/vietnamese-piper-voices)

## Render

Dùng phụ thuộc và tệp giọng trong [hướng dẫn pilot](PILOT.md). Đặt `cabin.png`, `machine.png` và `standing.png` vào `build/story-plates/`.

```powershell
& $py scripts/render_capy_story.py --plates build/story-plates --model build/voice-diemdam/vi_VN-diemdam-medium.onnx --tokens build/voice-diemdam/tokens.txt --font C:/Windows/Fonts/seguisb.ttf --out build/story-20s-review-media
& $py scripts/build_video.py --manifest episodes/EP01/story_20s.json --media-dir build/story-20s-review-media --out build/story-20s-review-capcut
```

Mở `DRAFT_preview.mp4` trong bộ đầu ra. Để chỉnh riêng từng cảnh trong CapCut, nhập năm clip hình, WAV thoại, WAV hiệu ứng và SRT, rồi xếp theo `shot_table.csv`.

## Duyệt

- Đối chiếu áo BK, tỷ lệ mascot và chiếc máy giữa ba khung ImageGen. Cảnh studio dùng đúng nguồn gốc để kiểm tra nhận diện.
- Bình giả định kín, chữ nhật đối xứng, đầy một nửa và dầu đứng yên. Độ sâu thay đổi tại vị trí cảm biến đã minh họa trong khi mặt dầu đi qua tâm bình và thể tích giữ nguyên. Một lần đọc thấp trên dốc chưa đủ để kết luận lượng nhiên liệu thực tế giảm.
- Duyệt giọng và khẩu hình trên video ghép trước khi chốt sản xuất. Những khung ImageGen và video duyệt lưu cục bộ.

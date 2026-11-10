# EP01 · Bản thử 20 giây

**DRAFT / OWNER REVIEW** · 8 cảnh · 1080×1920 · 30 fps. Cảnh studio dùng GIF Capy đã duyệt, với khẩu hình theo giọng Việt. Các cảnh cắt dùng bảng màu pastel, kim đồng hồ hạ, thanh so sánh động, bọt thước cân bằng và điểm nhấn màu. Âm thanh hiệu ứng tự tổng hợp đi kèm WAV riêng.

Bản MP4 duyệt dùng giọng nam Điềm Đạm đã chọn cho cảnh thử trước. Đây là giọng tạm để duyệt nhịp và màu. [Nguồn mô hình](https://huggingface.co/vnhellboy/vietnamese-piper-voices)

## Thử giọng Adam

Trong **CapCut → Text to Speech**, xem danh sách giọng trên tài khoản và thử dòng đầu với Adam nếu giọng đó xuất hiện. Chọn từng dòng dưới đây làm một lớp văn bản. Một số giọng có thể khả dụng khác nhau theo tài khoản. [Hướng dẫn CapCut](https://www.capcut.com/vi-vn/help/voice-options-missing)

Nếu cần đúng Adam của ElevenLabs, mở giọng **Adam** trong thư viện và thử **Eleven v3** với câu đầu tiếng Việt. Nghe thử dấu và cách nhả chữ trước khi tạo cả tám câu. [Giọng Adam](https://elevenlabs.io/voice-library/adam) · [Ngôn ngữ Eleven v3](https://elevenlabs.io/docs/overview/models#eleven-v3)

```text
Ủa, ai uống dầu của tôi?!
Máy mới leo dốc thôi mà!
Đồng hồ tụt cái rụp!
Bình nghiêng, mặt dầu vẫn ngang.
Chỗ cảm biến, mức dầu thấp hơn.
Trong ví dụ này, lượng dầu vẫn vậy.
Về chỗ bằng phẳng, rồi đo lại.
Khoan bắt oan cái dốc!
```

**Prompt cho Video Studio nếu dùng tính năng trợ lý**

> Dùng 8 câu thoại tiếng Việt theo thứ tự S01 đến S08. Thử giọng Adam nếu tài khoản có. Đọc rõ chữ, nhấn “uống dầu”, “cái rụp” và “bắt oan”. Giọng vui kiểu kể meme, giữ ngắt câu ngắn. Giữ nguyên 8 clip, hiệu ứng và phụ đề đã dựng. Tạo từng câu thoại riêng để tôi đặt vào timeline 20 giây. Cho tôi nghe thử câu đầu trước.

Đặt các stem mới theo `shot_table.csv` và căn điểm vào giọng theo `captions_vi.srt`. Giữ các stem SFX. Với S01 và S08, căn lại khẩu hình theo nhịp giọng Adam thực tế trước khi duyệt bản ghép.

## Build

Dùng phụ thuộc và tệp giọng Điềm Đạm trong [hướng dẫn pilot](PILOT.md). Thư mục đầu ra giữ MP4 xem thử, 8 clip hình, WAV 48 kHz, SRT và bảng thời gian.

```powershell
& $py scripts/render_capy_multishot.py --manifest episodes/EP01/proof_20s.json --model build/voice-diemdam/vi_VN-diemdam-medium.onnx --tokens build/voice-diemdam/tokens.txt --font C:/Windows/Fonts/seguisb.ttf --out build/proof-20s-media
& $py scripts/build_video.py --manifest episodes/EP01/proof_20s.json --media-dir build/proof-20s-media --out build/proof-20s-review-capcut
```

Sơ đồ là ví dụ bình chữ nhật đối xứng, đầy một nửa và không hao hụt, với dầu đứng yên. Vị trí cảm biến giả định nằm về đầu cao khi bình nghiêng. Các thanh là minh họa, không gán thông số cho một mẫu máy.

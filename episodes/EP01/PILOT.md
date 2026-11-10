# EP01 · S01 studio pilot

Xem [bản thử màu 20 giây và kịch bản Adam](PROOF_20S.md) để duyệt nhịp tám cảnh.

## Bản B · giọng nam và bốn cảnh

**DRAFT / OWNER REVIEW** · 7,80 giây · 1080×1920 · 30 fps. Capy phản ứng → máy xúc leo dốc → sơ đồ bình dầu → Capy chốt. Hai cảnh studio dùng chính GIF đã duyệt. Hai cảnh minh họa dùng hình vẽ 2D gốc với nét viền và nền giấy ấm. Nhịp cắt và cách minh họa tham khảo các khung xem trước quanh mốc 0:39. [Video tham chiếu](https://www.youtube.com/watch?v=dTWuRMURNyU&t=39s)

Giọng nháp nam **Điềm Đạm** thay cho Trầm Vang, với cao độ tự nhiên cao hơn, giảm dải trầm nhẹ và nhấn dải rõ chữ. Khẩu hình được dựng lại theo giọng mới. Hồ sơ mô hình nêu nguồn dữ liệu của checkpoint tổ tiên có điều khoản dùng cho nghiên cứu. Giữ bản lồng tiếng này ở phạm vi duyệt nội bộ và duyệt giọng cuối trước khi phát hành. [Hồ sơ mô hình](https://huggingface.co/vnhellboy/vietnamese-piper-voices#vietnamese-piper-voices-medium)

Sau khi cài phụ thuộc ở mục Build, tải `vi_VN-diemdam-medium.onnx` và `tokens.txt` vào `build/voice-diemdam/`. Script kiểm tra SHA-256 của cả hai. [Tệp mô hình](https://huggingface.co/vnhellboy/vietnamese-piper-voices/tree/main/vits-piper-vi_VN-diemdam-medium)

```powershell
& $py scripts/render_capy_multishot.py --model build/voice-diemdam/vi_VN-diemdam-medium.onnx --tokens build/voice-diemdam/tokens.txt --font C:/Windows/Fonts/seguisb.ttf --out build/multishot-clear-media
& $py scripts/build_video.py --manifest episodes/EP01/pilot_multishot.json --media-dir build/multishot-clear-media --out build/multishot-clear-capcut
```

Mở `build/multishot-clear-capcut/DRAFT_preview.mp4` để duyệt. Trong CapCut, xếp S01–S04 cùng WAV tương ứng theo `shot_table.csv` và nhập `captions_vi.srt`.

## Bản A · một cảnh studio

**DRAFT / OWNER REVIEW** · 7.20 s · 1080×1920 · 30 fps

Capy hỏi “Ủa, máy xúc vừa lên dốc mà mức dầu tụt rồi?” rồi tự sửa “Khoan, số đo đổi đâu có nghĩa là mất dầu!” Cảnh thử dùng các tư thế tay và nhún từ GIF chuẩn, với biến dạng giới hạn ở vùng miệng theo mốc âm vị tiếng Việt. Tấm nền studio đầy đủ nằm trong khung dọc, gồm laptop, mic, logo trên áo, ly và bảng BK. GIF gốc được kiểm tra SHA-256 trước khi render.

## Build

Requires Python 3.11+ and FFmpeg 7+ with libx264, libass and ffprobe. The assembly step uses only the Python standard library. The pilot render uses Pillow, NumPy and Piper with its alignment extra. Run from the checkout root in PowerShell. Substitute a local Vietnamese-capable TrueType font when reproducing on another OS. Use the same font and dependency versions for byte-level comparison on one machine.

```powershell
pwsh -File scripts/import_approved_assets.ps1
python -m venv .venv
$py = ".venv/Scripts/python.exe"
& $py -m pip install "Pillow>=11,<13" "piper-tts[alignment]==1.8.0"
New-Item -ItemType Directory -Force build/voice | Out-Null
& $py -m piper.download_voices --download-dir build/voice vi_VN-vais1000-medium
& $py scripts/render_capy_pilot.py --model build/voice/vi_VN-vais1000-medium.onnx --font C:/Windows/Fonts/seguisb.ttf --out build/pilot-media
& $py scripts/build_video.py --manifest episodes/EP01/pilot.json --media-dir build/pilot-media --out build/pilot-capcut
```

Both build commands accept `--ffmpeg`. The assembly command also accepts `--ffprobe`. Use a new output directory on rebuild. The scripts stage outputs before publishing them into the requested folder.

The draft voice is synthesized locally with Piper 1.8.0 and the pinned Vietnamese VAIS1000 model. The VAIS-1000 dataset is credited under CC BY 4.0 in the voice's model card. Its upstream Lessac checkpoint has separate dataset terms. Voice casting and reuse clearance remain owner review items. [Vietnamese model card](https://huggingface.co/rhasspy/piper-voices/blob/main/vi/vi_VN/vais1000/medium/MODEL_CARD) · [Lessac model card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/lessac/medium/MODEL_CARD)

## CapCut Pro Desktop

1. Tạo dự án cục bộ mới, khung **9:16**. Nhập `clips/S01_picture.mp4` và `audio/S01_voice.wav` từ `build/pilot-capcut/`. Đặt cả hai tại **00:00** theo `shot_table.csv`. Giữ nguyên khung hình để thấy cả ba vị trí logo và ly.
2. Trong **Captions → Add Captions → Import file**, nhập `captions_vi.srt` UTF-8. Kiểm tra dấu tiếng Việt, hai mốc phụ đề và vị trí trên vùng giao diện TikTok. [Hướng dẫn CapCut](https://www.capcut.com/vi-vn/help/how-to-import-subtitles)
3. Phát cả cảnh. Soi khẩu hình ở “máy”, “mức” và “mất”, động tác nhún, logo trên áo và bảng, logo trên ly và mức thoại. Dùng `DRAFT_preview.mp4` làm bản xem có tiếng và phụ đề. Bản xuất kiểm tra cục bộ dùng **1080×1920, 30 fps, H.264**.
4. Nếu thử giọng khác, **Text to Speech** và **Video → Basic → Lip Sync** cần thao tác trong CapCut. Nếu thử chuyển động sinh thêm, dùng ảnh tĩnh đã duyệt trong **Video Studio / Image to Video**. Kiểm tra công cụ có khả dụng cho tài khoản, chi phí credit và độ ổn định nhận diện trước khi Generate. So sánh với cảnh gốc và cân lại mốc thoại nếu thay giọng. [Hướng dẫn Lip Sync](https://www.capcut.com/help/lip-sync-feature)

Video Studio was visible in CapCut Pro Desktop 9.7.1.4203. Desktop control ended before the local timeline import. The package uses standard media and does not require an AI generation step.

## Pilot verification

- All eight package files matched the pinned manifest, and the canonical master matched the GIF89a signature.
- The preview decoded in full as 1080×1920 H.264, 216 frames at 30 fps, with 7.20 s of 48 kHz AAC. The decoded mix measured −19.1 dBFS mean and −2.8 dBFS peak.
- Two complete runs on the same workstation produced identical preview SHA-256 `d71072df57aa68bd853fe9d72da64e1522a683e0367cfed9d933680eeb2a4eff`. Sampled frames retain the shirt emblem, mug, panel and full studio. Final voice quality, expressive lip sync and subtitle placement in CapCut remain review items.

## Extending the pipeline after review

Use a separate manifest per edit, based on [pilot.json](pilot.json). Set `stage` to `episode` and use `tiktok` for 1080×1920 or `youtube` for 1920×1080. Both use 30 fps. Author a separate composition, script and voice track for each. Aim for 3,600 frames (2 minutes) or 18,000 frames (10 minutes) respectively. Use contiguous shot starts in frames, captions relative to each shot in milliseconds, a picture and voice stem per shot, optional SFX, and provenance for every shot.

Assembly checks input presence, aspect ratio, shot coverage, cue timing, output duration, frame count and codecs, then decodes the complete preview as a smoke check. It creates shot-ordered files, 48 kHz WAV stems, UTF-8 SRT, a shot table, and H.264/AAC MP4. Generated draft media stays in the local `build/` folder. Production of both full cuts is gated by owner review of the pilot and technical review of the scripts.

Run `python -m unittest discover -s scripts -p test_video_pipeline.py` for the missing-input and two-shot landscape smoke tests. Set `CAPY_FFMPEG` and `CAPY_FFPROBE` if the binaries are outside PATH.

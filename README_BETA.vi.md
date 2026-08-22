# DouyinLiveRecorder UI Beta

Bản Windows beta bổ sung giao diện local cho dự án mã nguồn mở
[ihmily/DouyinLiveRecorder](https://github.com/ihmily/DouyinLiveRecorder).

## Tính năng

- Thêm link live Douyin/TikTok từ giao diện trình duyệt local.
- Nút `▶` bắt đầu hoặc ghi phiên mới.
- Nút `Ⅱ Dừng` dừng riêng phòng và giữ file đang ghi.
- Nút `Go Live` mở trang live gốc.
- Nút `Mở output` mở thư mục video.
- Theo dõi nhiều phòng và tự ghi khi phòng bắt đầu live.

## Chạy bản EXE portable

1. Giải nén toàn bộ file ZIP vào một thư mục có quyền ghi.
2. Chạy `DouyinLiveRecorderBeta.exe`.
3. Trình duyệt mở `http://127.0.0.1:8765`.
4. Dán link và bấm `▶ Bắt đầu ghi`.

Không di chuyển riêng file EXE ra khỏi thư mục đã giải nén. Thư mục `_internal`,
`ffmpeg` và `node` là thành phần bắt buộc.

## Cookie và dữ liệu riêng tư

Lần chạy đầu tạo `config/config.ini`. Một số phòng Douyin/TikTok có thể yêu cầu
cookie của chính người dùng. Điền cookie vào file này và không gửi file đó cho
người khác. `config/config.ini`, danh sách link, log và video đều bị loại khỏi Git.

## File video

- Trong lúc ghi, file `.ts` có thể chưa mở ổn định hoặc tạm hiển thị 0 KB do bộ đệm.
- Khi dừng, recorder đóng file và có thể tạo thêm MP4 theo cấu hình.
- Cấu hình beta giữ file TS gốc sau khi chuyển MP4 để giảm nguy cơ mất dữ liệu.

## Giới hạn beta

- Windows 10/11 x64.
- UI chỉ nghe trên `127.0.0.1`; không dùng như web server mạng LAN/public.
- TikTok và một số nền tảng có thể cần proxy/cookie riêng.
- EXE chưa ký số nên Windows SmartScreen hoặc antivirus có thể cảnh báo.

## Chạy từ source

Yêu cầu Python 3.11, FFmpeg và Node.js:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe ui.py
```

Đóng gói lại trên Windows bằng `powershell -ExecutionPolicy Bypass -File
.\build_beta.ps1` sau khi FFmpeg và Node.js đã có trong `PATH`.

## Giấy phép

Phần source kế thừa giấy phép MIT của upstream. Gói portable chứa FFmpeg GPLv3
và Node.js MIT dưới dạng chương trình độc lập; xem `THIRD_PARTY_NOTICES.md` và
thư mục `THIRD_PARTY_LICENSES` trong gói phát hành.

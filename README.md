# DouyinLiveRecorder UI Beta

Giao diện local và gói Windows portable để theo dõi, ghi live Douyin/TikTok mà
không chiếm màn hình làm việc. Dự án được phát triển từ mã nguồn mở
[`ihmily/DouyinLiveRecorder`](https://github.com/ihmily/DouyinLiveRecorder).

## Dùng nhanh

1. Tải file ZIP trong mục **Releases** và đối chiếu SHA-256.
2. Giải nén **toàn bộ** ZIP vào một thư mục có quyền ghi.
3. Chạy `DouyinLiveRecorderBeta.exe`.
4. Dán link live rồi bấm `▶ Bắt đầu ghi`.

Không tách riêng EXE khỏi các thư mục `_internal`, `ffmpeg` và `node`. Cookie,
danh sách phòng, log và video chỉ được tạo trên máy người dùng, không có trong
source hay gói phát hành.

Xem hướng dẫn, giới hạn beta và cách build tại [README_BETA.vi.md](README_BETA.vi.md).
Tài liệu nguyên bản của upstream được giữ tại [README_UPSTREAM.md](README_UPSTREAM.md).

## Trạng thái

Phiên bản hiện tại: `0.1.0-beta.3` cho Windows 10/11 x64. EXE chưa ký số nên
SmartScreen có thể cảnh báo. Xem [SECURITY.md](SECURITY.md),
[UPSTREAM.md](UPSTREAM.md) và [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

MIT cho source kế thừa và phần UI. Gói portable chứa các chương trình độc lập
FFmpeg và Node.js theo giấy phép nêu trong third-party notices.

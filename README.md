# Health Focus: tài khoản và phân quyền

Ứng dụng Flask trong thư mục này có đăng ký/đăng nhập, hồ sơ sức khỏe, lịch sử phân tích, kế hoạch tuần theo tài khoản và trang quản trị. Phần MLP và luật chuyên gia nằm trong `src/`.

## Chạy ứng dụng

Tại thư mục gốc, cài các gói trong `requirements.txt`, đặt biến môi trường `FLASK_SECRET_KEY` bằng một chuỗi ngẫu nhiên dài, rồi chạy `python app.py`. Đây là ứng dụng chính, gồm cả đăng nhập và trang admin. Cơ sở dữ liệu SQLite mặc định nằm tại `instance/health.db`. Có thể đặt `HEALTH_DATABASE_URI` để dùng một cơ sở dữ liệu SQLite khác. Trước khi chạy với dữ liệu thật, sao lưu `health.db`; ứng dụng tự thêm các cột còn thiếu và tạo bảng mới. Việc nâng cấp này dành cho SQLite.

Mã ứng dụng cũ được giữ nguyên trên máy tại `_archive/legacy-root/`. Hai bản project cũ khác nằm tại `_archive/KLCN_2026-main/`. Thư mục `_archive/` không được đưa lên GitHub và không được ứng dụng chính sử dụng.

Tạo admin đầu tiên trong terminal tại cùng thư mục:

```powershell
.\.venv\Scripts\python.exe -m flask --app app create-admin ten_admin
```

Lệnh hỏi mật khẩu trực tiếp trong terminal. Đăng ký trên website luôn tạo tài khoản `user`, không có đăng ký admin công khai.

## Quyền truy cập

- `user`: xem và tạo hồ sơ, kết quả, lịch sử của chính mình.
- `admin`: xem danh sách tài khoản, hồ sơ và các lần phân tích của mọi người dùng; khóa/mở khóa tài khoản user; xem nhật ký truy cập. Admin không thể khóa tài khoản admin khác trong giao diện này.
- Mỗi lượt admin mở hồ sơ hoặc kết quả của người khác được ghi vào `audit_logs`.
- Khi khóa tài khoản hoặc đổi mật khẩu, phiên cũ bị vô hiệu ở yêu cầu tiếp theo.
- Sau 5 lần nhập sai mật khẩu liên tiếp, tài khoản tạm ngừng đăng nhập trong 15 phút.

Khi triển khai qua HTTPS, đặt `FLASK_HTTPS=1` để bật cookie `Secure`. Không dùng khóa bí mật mặc định của môi trường phát triển ở máy chủ triển khai.

## Kiểm thử

Chạy tại thư mục gốc:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Bộ kiểm thử dùng SQLite trong bộ nhớ, không ghi vào cơ sở dữ liệu người dùng.

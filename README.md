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

## Lựa chọn chuẩn BMI khi phân tích

Biểu mẫu `/health` cho chọn `current` hoặc `vietnam_asia`. Luồng Expert/Hybrid `current` của gói xuất không cộng điểm BMI; phần đánh giá thể trạng trong ứng dụng dùng ngưỡng BMI WHO quốc tế. `vietnam_asia` cộng điểm BMI theo ngưỡng tham chiếu Bộ Y tế Việt Nam trong Expert và dùng ngưỡng này ở phần đánh giá thể trạng. Lựa chọn được lưu cùng hồ sơ và từng kết quả, nên mở lại lịch sử vẫn thấy đúng chuẩn đã dùng. Kết quả cũ chưa có trường này được hiểu là `current`.

Trong ứng dụng Flask, cả hai lựa chọn dùng cùng mô hình MLP. `models/health_inference.py` tính Expert và Hybrid theo profile đã chọn, dùng ngưỡng trong `models/config.json`. Kết quả lưu riêng mục tiêu MLP, mục tiêu Expert và mục tiêu cuối từ Hybrid. `vietnam_asia` thêm điểm BMI +2/+4 theo thiết kế thực nghiệm của nhóm. Ứng dụng còn chạy bộ luật an toàn riêng cho hướng dẫn và gợi ý; gợi ý món ăn/vận động hiện vẫn dựa trên mục tiêu người dùng đã chọn cùng bộ luật an toàn này, không tự động thay bằng mục tiêu Hybrid.

Hiện cả hai ngưỡng Hybrid trong `models/config.json` cùng là `0.5`. Chỉ mô tả chúng là ngưỡng đã được tối ưu riêng khi có kết quả validation chứng minh điều đó. Nếu cập nhật gói xuất từ Colab, cần cập nhật đồng bộ `health_inference.py`, `config.json`, model, preprocessor và label encoder rồi kiểm thử đối chiếu.

Nguồn ngưỡng: [WHO](https://www.who.int/en/news-room/fact-sheets/detail/obesity-and-overweight) và [Bộ Y tế Việt Nam, Quyết định 2892/QĐ-BYT](https://daithaoduong.kcb.vn/huong-dan-chan-doan-va-dieu-tri-benh-beo-phi%26p%3D6).

## Sàng lọc món ăn theo dị ứng thực phẩm

Biểu mẫu `/health` cho người dùng khai báo dị ứng thực phẩm đã biết. Thông tin được lưu theo hồ sơ và từng lần phân tích. Bộ lọc dùng luật dị ứng trong `expert_system/expert_system/` trước khi xếp hạng món ăn; mã `expert_system/expert_recommendation.py` do nhóm bổ sung được giữ riêng, không thay thế luồng `src/expert_recommendation.py` đang xử lý xung đột mục tiêu và cấu hình BMI. Biểu mẫu không còn thu thập bệnh lý nền cho lượt phân tích mới; dữ liệu trong lịch sử cũ được giữ nguyên.

Món có dị nguyên trùng hoặc thiếu thông tin dị nguyên bị loại khỏi gợi ý sơ bộ; giá trị `none` trong CSV chỉ là khai báo của dữ liệu, không thay thế kiểm tra nguyên liệu và nguy cơ lẫn chéo.

Kế hoạch thực đơn 7 ngày hiện không được tự động tạo khi có dị ứng, vì bộ ghép bữa chưa kiểm soát đủ dị nguyên và nguy cơ lẫn chéo. Người dùng vẫn xem được các ứng viên món ăn sau bước sàng lọc trên trang kết quả. Lượt phân tích cũ có khai báo bệnh lý vẫn giữ kết quả và giới hạn kế hoạch tuần đã lưu. Tham khảo [FDA về dị ứng thực phẩm](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies); các luật đang chờ thẩm định chuyên môn.

## Kiểm thử

Chạy tại thư mục gốc:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Bộ kiểm thử dùng SQLite trong bộ nhớ, không ghi vào cơ sở dữ liệu người dùng.

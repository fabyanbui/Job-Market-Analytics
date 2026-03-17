# Đề tài: Ứng dụng phân tích dữ liệu trên nền tảng tuyển dụng các ngành nghề thuộc lĩnh vực công nghệ thông tin (TopDev) và rút ra những insights có ích cho những đối tượng liên quan.

## Lý do chọn:
- TopDev là nền tảng tuyển dụng lớn trong lĩnh vực công nghệ thông tin, nơi thu thập nhiều dữ liệu từ các nhà tuyển dụng và ứng viên. Việc phân tích dữ liệu từ nền tảng này sẽ cung cấp các insights quan trọng về xu hướng tuyển dụng, nhu cầu kỹ năng và định hướng nghề nghiệp, giúp các bên liên quan đưa ra quyết định phù hợp.

## Nguồn dữ liệu:
- Dữ liệu sẽ được thu thập từ nền tảng TopDev.vn.

## Đối tượng hướng đến:
- Nhà tuyển dụng: Cải thiện chiến lược tuyển dụng và lựa chọn ứng viên phù hợp.
- Ứng viên: Hiểu rõ các kỹ năng và kiến thức được yêu cầu trong ngành để định hướng phát triển sự nghiệp.
- Các tổ chức đào tạo: Điều chỉnh chương trình giảng dạy phù hợp với nhu cầu của thị trường.
- Nhà nghiên cứu và các cơ quan quản lý: Đưa ra các phân tích, dự báo về xu hướng nghề nghiệp trong lĩnh vực công nghệ.

## Cách thức crawl dữ liệu:
- Thư viện sử dụng: Selenium, là một thư viện rất phù hợp cho việc thu thập dữ liệu động (dynamic data hay là real-time data).
- Thư viện khác: Pandas, là một thư viện dùng để thao tác và phân tích dữ liệu, và trong trường hợp này dùng để lưu trữ dữ liệu vào file .csv.
- Các bước thu thập dữ liệu:
    1. Import các thư viện cần thiết.
    2. Cài đặt driver cho selenium.
    3. Sử dụng selenium để đăng nhập vào GitHub từ đó đăng nhập vào trong trang chính TopDev.
    4. Tải toàn bộ trang chính chứa tất cả các thông tin việc làm IT của TopDev bằng cách scroll liên tục tới cuối trang.
    5. Sử dụng selenium để lấy tất cả các link đến từng job có trong địa chỉ trang web trên.
    6. Tiến hành crawl tất cả các thông tin (thuộc tính) có trong mỗi link job.
    7. Định dạng cho phù hợp và sử dụng Pandas để lưu trữ dữ liệu vừa crawl vào một dataframe và xuất csv.

## Thuộc tính (features):
- `ten_cong_viec`: là tên của công việc đó/vị trí đó.
- `ten_cong_ty`: là tên của công ty tuyển dụng công việc đó.
- `muc_luong`: là mức lương của công việc đó.
- `dia_chi`: là địa chỉ làm việc của công ty đó ứng với công việc đó.
- `ngay_dang`: là ngày đăng thông tin tuyển dụng của công việc đó lên trang TopDev.
- `nganh_nghe`: là lĩnh vực mà công ty đó chuyên về (domain).
- `quy_mo_cong_ty`: được ước tính bởi số nhân viên trong công ty đó.
- `nam_kinh_nghiem`: là số năm kinh nghiệm tối thiểu để có thể đáp ứng yêu cầu của công việc đó.
- `cap_bac`: là cấp bậc mà công việc đó yêu cầu như Intern, Fresher, Senior,...
- `loai_hinh`: là loại hình của công việc đó ví dụ như In Office, Remote hay là Hybrid.
- `loai_hop_dong`: là loại hợp đồng của công việc đó ví dụ như Full-time, Part-time hay Freelance.
- `cong_nghe_su_dung`: là các công nghệ mà ứng viên cần phải đáp ứng khi ứng tuyển vào công việc đó (skills).
- `quy_trinh_phong_van`: là quy trình phỏng vấn của công việc đó.
- `url`: là đường dẫn đến trang web của công việc đó (dự tính sử dụng như một ID để phân biệt các job với nhau giúp xử lý dữ liệu real-time dễ dàng hơn).

## Một số insights cơ bản:
- Mức lương và kinh nghiệm: Có thể rút ra mối quan hệ giữa mức lương và số năm kinh nghiệm yêu cầu. Chẳng hạn, các vị trí Senior thường có mức lương cao hơn đáng kể so với Fresher hoặc Intern.
- Địa điểm làm việc: Phân tích dữ liệu địa chỉ có thể cho biết những khu vực nào có nhu cầu tuyển dụng IT cao nhất, từ đó giúp ứng viên chọn nơi làm việc phù hợp với khả năng phát triển nghề nghiệp.
- Công nghệ phổ biến: Thống kê từ thuộc tính công nghệ sử dụng sẽ cung cấp danh sách các công nghệ được yêu cầu nhiều nhất, từ đó cho thấy xu hướng kỹ thuật trong ngành.
- Loại hình công việc và cấp bậc: Phân tích loại hình công việc (Remote, In Office, Hybrid) theo cấp bậc có thể chỉ ra rằng cấp bậc nào có xu hướng làm việc từ xa nhiều hơn, giúp ứng viên định hướng lựa chọn công việc phù hợp.
- Xu hướng tuyển dụng theo thời gian: Phân tích ngày đăng có thể cho biết những thời điểm trong năm có nhu cầu tuyển dụng cao nhất, giúp ứng viên tối ưu thời gian tìm kiếm việc làm.
- Quy mô công ty và lương: Phân tích quy mô công ty so với mức lương có thể cung cấp insight về việc các công ty lớn có xu hướng trả lương cao hơn hay không so với các công ty nhỏ.
- Loại hợp đồng phổ biến: Dựa vào loại hợp đồng, có thể thấy loại hình hợp đồng nào được ưa chuộng hơn trong ngành, giúp ứng viên chuẩn bị kế hoạch dài hạn cho sự nghiệp (Full-time, Part-time, Freelance).

## Hướng thực hiện đề tài và sản phẩm:
> Làm dashboard
>
> Process: Crawl > Preprocess > Analyze > *(ML if necessary)* > Dashboard > Insights


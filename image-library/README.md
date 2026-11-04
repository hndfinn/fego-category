# Chỉ mục ảnh gốc FEGO

Ảnh gốc ở OneDrive. Repo chỉ chứa metadata; không chứa ảnh gốc, thumbnail, link chia sẻ có mã truy cập hoặc URL tải tạm.

Nguồn khởi tạo: thư mục OneDrive local `Ảnh sản phẩm`. **Chưa xác minh thư mục này khớp chính xác folder trong link owner cung cấp.** Xem `summary.json` để biết thời điểm, số ảnh và trạng thái đầy đủ của lần quét. Dung lượng là dung lượng logic trên OneDrive, không phải số byte đã tải.

## Cập nhật metadata

```powershell
pwsh -File scripts/index_onedrive_images.ps1 -SourceRoot '<OneDrive>/Ảnh sản phẩm'
```

Script chỉ duyệt thư mục và lấy metadata file; không mở nội dung, tính checksum nội dung, copy hoặc giải mã ảnh. OneDrive có thể tải metadata thư mục khi duyệt. Thư mục chưa đồng bộ vào máy sẽ không xuất hiện. Kiểm tra `enumeration_error_count` và `local_enumeration_complete` trước khi dựa vào số lượng.

`files.csv`: mã ảnh (hash đường dẫn, không phải checksum nội dung), đường dẫn tương đối, dung lượng, thời gian sửa và thuộc tính. Mã giữ nguyên khi đường dẫn giữ nguyên; đổi tên/di chuyển sẽ đổi mã. Không suy luận SKU từ tên lộn xộn.

## Dùng ảnh trong task

1. Tìm tên/nhóm sản phẩm trong CSV bằng công cụ local; không đưa toàn bộ CSV vào context AI.
2. Chỉ lấy thumbnail cho nhóm đang làm. Nếu lấy qua OneDrive, ưu tiên thumbnail có sẵn; đọc file placeholder bằng phần mềm ảnh có thể tải nguyên bản.
3. Đối chiếu ảnh với sản phẩm đã xác minh trước khi ghi mapping SKU. Metadata ban đầu chưa phải phân loại đã duyệt.
4. Chỉ tải ảnh gốc được chọn; lưu ảnh và thumbnail trong `.image-cache/` (Git ignored).

Chưa có kết nối API OneDrive hay công cụ tải thumbnail tự động. Máy khác cần quyền truy cập nguồn; `git pull` chỉ lấy chỉ mục và script. Không đổi tên, di chuyển hay chỉnh sửa ảnh nguồn.


## Đồng bộ giữa các repo FEGO

Bản chỉ mục gốc được cập nhật tại `hndfinn/fego-product-pipeline/image-library/`; blog, category và analytics giữ bản sao để tra cứu ngay trong repo. Sau lần quét mới, đồng bộ `files.csv` và `summary.json` sang cả ba repo, giữ nguyên mã ảnh. Kiểm tra `generated_utc` để nhận biết bản cũ. Khi cần ảnh content, dùng đường dẫn tương đối trong CSV để lấy đúng file từ thư mục OneDrive đã có quyền truy cập; Git không chứa dữ liệu ảnh.

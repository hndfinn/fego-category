# SESSION HANDOFF — TÁI CẤU TRÚC MEGAMENU, KEYWORD TRACKING & DỰNG HUB `/khong-gian/`

- **Ngày bàn giao:** 2026-11-18
- **Repository:** `https://github.com/hndfinn/fego-category.git` (thư mục `khong-gian-hub/`)
- **Trạng thái:** Đã hoàn tất 100% cập nhật Megamenu live, cập nhật Keyword Tracking trên Google Sheets, chốt Prototype & toàn bộ bộ ảnh WebP cho `/khong-gian/` + 7 Archive Không gian; **đang chờ thông tin `WP_USER` + `WP_APP_PASS` của `fegowoodworker.com` để đẩy lên WordPress qua REST API.**

---

## 1. Những Việc Đã Hoàn Thành 100% (Live & Verified)

### 1.1. Tái cấu trúc 3 Megamenu & CSS trên `https://fegowoodworker.com/`
- **CSS (`functions.php` — WoodMart Child Theme, handle `fego-mega-menu`):**
  - Tinh chỉnh `.fmm-thumb` bỏ viền (`background: #f6f5f3; border-radius: 8px`), `.fmm-title` giảm xuống `font-weight: 500`, bổ sung `.fmm-grid-6` (6 cột) theo đúng vibe `muebles.es`.
  - Gỡ lazy-load placeholder SVG (`wd-lazy-load`) khỏi ảnh trong 3 megamenu để thumbnail hiển thị ngay lập tức khi rê chuột vào.
- **`cms_block` `15950` (*FEGO Mega Menu — Tất cả sản phẩm*):**
  - Bỏ mục **Giường** (ít SKU) và xóa toàn bộ **10 link danh mục ảo (HTTP 404)**.
  - Chuyển sang cấu trúc **Hybrid**: giữ danh mục con thật cho *Bàn*, *Kệ & Giá sách*, *Tủ lưu trữ* (đã bổ sung `Tủ đựng đồ` `/danh-muc/tu-luu-tru/tu-da-nang/`), *Ghế*; còn *Gương* (7 SKU) và *Trang trí & Phụ kiện* (6 SKU) hiển thị sản phẩm thật + nút xem tất cả.
- **`cms_block` `15951` (*FEGO Mega Menu — Không gian*):** Sửa toàn bộ 7 link từ `/phong/...` (404) sang `/khong-gian/<slug>/` (đặc biệt Bếp & phòng ăn → `/khong-gian/nha-bep/`).
- **`cms_block` `15952` (*FEGO Mega Menu — Chất liệu*):** Sửa `/chat-lieu/go-plywood/` → `/chat-lieu/plywood/` và `/chat-lieu/go-mdf/` → `/chat-lieu/go-cong-nghiep/`.
- **Kiểm tra:** **44/44 URL** trên cả 3 megamenu trả về **HTTP 200 (0× 404)**.

### 1.2. Cập nhật `[FEGO] Master Keyword Tracking (High - Medium - Low) 2026`
- **Google Sheet ID:** `1VAPT_zAU4o-M6nXcnormNirQMvlr7gn17qEYRhRXmcc`
- Đã ghi thêm **32 dòng từ khóa mới** vào `0_Master_All!A220:I251` (**STT `218` → `249`**):
  - **6 Danh mục sản phẩm còn thiếu** (`STT 218–228`, mức `MEDIUM`): `tu-luu-tru` (`tủ gỗ`), `tu-da-nang` (`tủ đựng đồ gỗ`), `ghe` (`ghế gỗ`), `decor-phu-kien` (`đồ decor gỗ`), `do-trang-tri` (`đồ trang trí bằng gỗ`), `phu-kien-ban-lam-viec` (`phụ kiện bàn làm việc gỗ`).
  - **2 Archive Chất liệu còn thiếu** (`STT 229–232`, mức `LOW`): `go-tan-bi` (`nội thất gỗ tần bì`, `nội thất gỗ ash`), `go-cong-nghiep` (`nội thất gỗ công nghiệp`, `đồ gỗ mdf tối giản`).
  - **7 Archive Không gian + 1 Hub `/khong-gian/`** (`STT 233–249`): dùng bộ từ khóa bao trùm mọi chất liệu (`nội thất gỗ phòng khách`, `nội thất gỗ phòng ngủ`, `nội thất gỗ phòng làm việc`, `nội thất gỗ phòng bếp`, `nội thất lối vào nhà`, `nội thất phòng tắm gỗ`, `đồ gỗ trang trí ban công`, `nội thất gỗ theo không gian`).
- **Quy tắc ghi nhớ:** Luôn kiểm tra Google Sheet này mỗi khi người dùng nhắc tới `keyword` hoặc `keyword ranking`.

### 1.3. Prototype & Bộ ảnh WebP Hoàn Chỉnh (`khong-gian-hub/`)
- **Prototype đã duyệt 100%:** `khong-gian-hub/khong-gian-prototype.html`
  - **Design Anchor:** Hệ màu & hình khối của `/chat-lieu/plywood/` (`#111111`, `#f3f0ea`, `#e6e2da`, `#8b5a2b`, `border-radius: 2px`).
  - **Cấu trúc 4 phần (tách rạch ròi với `/shop/` để chống cannibalization):**
    1. **Hero Full-width (Elementor Container + background image):** Breadcrumb + H1 (`Chọn nội thất gỗ theo từng căn phòng`) + Subtitle, **không có kicker & không nút CTA**.
    2. **Lưới 4×2 Không gian sống (`4:5`):** 7 ô ảnh studio trắng sáng mơ màng dẫn về 7 archive `/khong-gian/<slug>/` + ô thứ 8 màu đen `#111111` (hover `#8b5a2b`) không dùng ảnh cho **Đóng theo kích thước riêng** (`/dich-vu-custom/`).
    3. **Gợi ý phối đồ thực tế cho từng không gian (Hotspot Mosaic + Carousel):** Ảnh bối cảnh thật `shop_room_living_anchor.webp` + 4 ô phụ có chấm hotspot bấm mở thẻ sản phẩm + dải sản phẩm đồng bộ.
    4. **Linh hoạt cho mọi không gian sống (Split Banner thuần nội dung, không CTA)** + **Khối thông điệp xưởng `#111111`** + **4 thẻ Chính sách/Điều hướng** (kèm icon nét mảnh `28px` + dòng chú thích đích mảnh: `/shop/`, `/huong-dan-dat-hang-va-thanh-toan/`, `/chinh-sach-doi-tra/`, `/ve-chung-toi/`).

- **Danh sách 16 file ảnh `.webp` trong `khong-gian-hub/`:**
  - **Cards dọc `4:5` / `3:4` cho `/khong-gian/` (8 files):**
    - `space_phong_khach_anchor.webp` (`896×1200`, lossless)
    - `space_phong_ngu.webp` (`819×1024`)
    - `space_phong_lam_viec.webp` (`896×1200`, lossless)
    - `space_nha_bep.webp` (`896×1200`, lossless)
    - `space_loi_vao.webp` (`896×1200`, lossless)
    - `space_phong_tam.webp` (`896×1200`, lossless)
    - `space_ban_cong.webp` (`896×1200`, lossless)
    - `space_custom.webp` (`896×1200`, lossless — bản dự phòng)
  - **Shop the Room Anchor (1 file):**
    - `shop_room_living_anchor.webp` (`1264×848`, lossless)
  - **Ảnh bìa ngang cho 7 trang Archive `/khong-gian/<slug>/` (7 files):**
    - `archive_cover_phong_khach_anchor.webp` (`1376×477`, lossless `459 KB`)
    - `archive_cover_phong_ngu.webp` (`1024×356`)
    - `archive_cover_phong_lam_viec.webp` (`1024×355`)
    - `archive_cover_nha_bep.webp` (`1024×355`)
    - `archive_cover_loi_vao.webp` (`1024×355`)
    - `archive_cover_phong_tam.webp` (`1024×356`)
    - `archive_cover_ban_cong.webp` (`1024×355`)

---

## 2. Thông Số Rank Math SEO Đã Chốt Cho `/khong-gian/`

- **Slug:** `khong-gian` (`https://fegowoodworker.com/khong-gian/`)
- **Focus Keyword:** `nội thất gỗ theo không gian`
- **SEO Title (54 ký tự):** `Nội Thất Gỗ Theo Không Gian Sống Cho Từng Phòng | FEGO`
- **Meta Description (149 ký tự):** `Khám phá nội thất gỗ theo không gian sống tại FEGO: phòng khách, phòng ngủ, góc làm việc, bếp ăn, lối vào đến ban công. Đóng trực tiếp tại xưởng.`
- **Robots:** `index, follow`

---

## 3. Việc Cần Làm Tiếp Trên Máy Mới (Qua WordPress REST API)

1. **Cấu hình quyền API WordPress (`fegowoodworker.com`):**
   - Tạo Application Password trên `fegowoodworker.com` (`Users → Profile → Application Passwords`), lưu `WP_USER` và `WP_APP_PASS` vào `.env` (lưu ý: `SIMICART_WP_USER=simi-team` đang có trong env là của site khác, trả về `401 invalid_username` trên FEGO).
2. **Triển khai qua REST API (`/wp-json/wp/v2/`):**
   - Upload 15 file `.webp` (`space_*.webp`, `shop_room_living_anchor.webp`, `archive_cover_*.webp`) lên `/wp-json/wp/v2/media`.
   - Tạo & xuất bản Page `/khong-gian/` (tắt Page Title của WoodMart, dựng Hero full-width Elementor/native container + 4 section đã chốt, điền Rank Math meta).
   - **Kiểm tra ngay rewrite rule:** Đảm bảo cả `https://fegowoodworker.com/khong-gian/` lẫn `https://fegowoodworker.com/khong-gian/phong-khach/` đều trả về HTTP 200 (không xung đột slug `khong-gian` với attribute base `pa_khong-gian`).
   - Cập nhật link mục **Không gian** trên Main Menu (`menu-item-15725` từ `#` → `/khong-gian/`), thêm footer `"Xem tất cả không gian →"` vào `cms_block` `15951` và `"Xem tất cả bài viết →"` vào `cms_block` `15954`.
   - Cập nhật 7 ảnh bìa ngang `archive_cover_*.webp` cho 7 term của `pa_khong-gian` (`phong-khach`, `phong-ngu`, `phong-lam-viec`, `nha-bep`, `loi-vao-hanh-lang`, `phong-tam`, `ban-cong`).

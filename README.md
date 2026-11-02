# FEGO Category agent

Bộ workflow riêng cho **WooCommerce category**. Codex tạo khung; bạn biên tập với Gemini; sau đó mới SEO và triển khai. Không dùng quy trình viết blog Codex-first.

## Dùng ngay

Clone repo về bất kỳ thư mục nào và mở thư mục repo làm workspace/project của Codex, rồi gửi:

> Dùng $fego-category cho category [URL]. Nguồn [Drive URL]. Block [ID nếu biết]. Hãy nghiên cứu và chuẩn bị khung để tôi làm tiếp với Gemini; dừng ở Gate 1.

Nếu chat hiện tại chưa nạp skill, yêu cầu đọc `AGENTS.md` và `.agents/skills/fego-category/SKILL.md` trong repo hiện tại trước khi làm. Bốn role TOML và project config đã có trong `.codex/`; chúng được dùng khi client nạp project này. Đây không phải cài đặt global vào mọi chat hoặc thay đổi cấu hình trên máy cá nhân. Không cần tạo chat mới nếu agent hiện tại đọc được các file và có công cụ subagent; có thể truyền role prompt tương ứng.

## Hai gate

1. **Duyệt nội dung**: bạn trả bản sau Gemini và xác nhận đúng phiên bản. Codex chưa được tối ưu thành bản triển khai/ghi CMS trước bước này.
2. **Duyệt đăng**: xem gói hoàn chỉnh (text + SEO + ảnh/link + target + diff/preview), xác nhận rồi mới ghi/publish.

Có thể cấp trước Gate 2 trong cùng tin nhắn: "Nội dung v2 này đã duyệt; tối ưu SEO rồi đăng luôn vào [category]". Agent vẫn chuẩn bị, QA và ghi nhận phạm vi; không hỏi lại. Sửa nội dung có thay đổi ý/facts cần mở lại Gate 1. Gói triển khai đổi sau duyệt cần duyệt lại Gate 2, trừ phạm vi cho phép trước đã bao phủ.

Checkpoint tự động không thêm gate: facts, mapping ảnh, keyword, heading, link, code/CMS, readback, mobile/render, cache. Thiếu dữ liệu thực sự thì hỏi; không biến mọi kiểm tra thành xin phép.

## Agent và subagent

Root điều phối là người duy nhất ghi Drive/CMS/SEO. Subagent trả đề xuất và evidence, không cùng ghi website:

| Role | Output |
|---|---|
| category_research | Facts, nguồn, IDs/URL, ảnh, mâu thuẫn |
| category_framework | Dàn ý, questions, khung và Gemini handoff |
| category_seo | Sau Gate 1: keyword map, bounded diff, title/meta/heading/link |
| category_qa | Review độc lập, PASS/FAIL/UNVERIFIED có bằng chứng |

Giữ nguyên model của agent cha. Chạy song song chỉ các phần độc lập; các bước phụ thuộc và mọi website write chạy tuần tự.

## Hồ sơ và preflight

`runs/<slug>/` được bỏ qua bởi Git: brief, nguồn đã freeze, facts, approved-content, media, payloads, review, approvals và backup. Không chứa bản sao credential. Không tạo sẵn gate approved cho category đã làm trước đây.

Ví dụ CLI, chạy từ project root. Chỉ ghi nhận `--message` khi có đúng lời xác nhận thật của user, không dùng ví dụ làm approval:

```sh
python scripts/workflow.py init --run runs/new-category --category-url https://fegowoodworker.com/danh-muc/REPLACE/ --term-id 123 --block-id 456
python scripts/workflow.py approve-content --run runs/new-category --file approved-content.md --gemini-edited --message 'Lời xác nhận thực tế của user cho bản này'
python scripts/workflow.py prepare --run runs/new-category --manifest deployment-manifest.json
python scripts/workflow.py approve-publish --run runs/new-category --message 'Lời duyệt gói triển khai thực tế của user'
python scripts/workflow.py check-publish --run runs/new-category
```

Sau init: tạo các file từ `templates/`, xác minh target IDs, điền source hash trong manifest từ state, chuẩn bị file QA có evidence thực tế. `prepare` chỉ thành công khi đủ payload/review và tất cả preparation checks PASS. Có thể lưu `approve-publish --advance` ngay sau Gate 1 khi user đã rõ ràng cho "SEO rồi đăng luôn". Không dùng flag này để tự bỏ gate.

Helper chỉ kiểm tra local hash/state. Nó không xác thực người duyệt, không cấp quyền, không tự gọi website, và không chứng minh live QA. Coordinator vẫn phải đọc user messages, recheck live baseline, backup, apply/publish và kiểm tra public category. Không đánh dấu hoàn tất nếu required visual/render QA chưa xác minh được.

## Chuẩn mặc định đã rút ra từ phiên triển khai

- Một H1 từ category template; block bắt đầu H2.
- Intro ngắn ở taxonomy description phía trên grid; không lặp intro trong block.
- Link trong caption hoặc câu; tránh CTA "Xem…" đứng riêng và link lặp vô ích.
- Link có gạch chân, màu tương phản, hover/focus; CSS chỉ trong phạm vi cần chỉnh.
- Ưu tiên WebP bàn giao, caption/alt riêng, phân biệt gallery thật và ảnh minh họa.
- Title/meta phải đúng hàng hóa, không keyword stuffing; focus-keyword không phải tín hiệu xếp hạng.
- API write success chưa phải live success; published Elementor có autosave cần promote/publish.
- Không đưa ghi chú nội bộ lên body; không đổi slug/grid/template hay điều chỉnh global ngoài phạm vi.

## Kiểm tra bộ workflow

```sh
python -m unittest discover -s tests -v
```

Các test kiểm tra gate/hash/target và thay đổi sau duyệt, không xác nhận runtime WordPress hay đăng bài.

## Cài trên local hoặc cloud mới

Yêu cầu: Git, Python **3.11+**, Codex app hoặc CLI có công cụ subagent và hỗ trợ MCP. Workflow/helper dùng thư viện chuẩn Python, không cần pip install. Repo không gắn với `/workspace` hoặc đường dẫn máy cụ thể.

```sh
git clone https://github.com/hndfinn/fego-category.git
cd fego-category
python scripts/check_setup.py
python -m unittest discover -s tests -v
```

Trên macOS/Linux có thể dùng `python3`; Windows có thể dùng `py -3.11`. Private repo yêu cầu GitHub login có quyền clone. Mở **thư mục repo** trong Codex hoặc chạy `codex -C .`; chấp nhận trust project khi client yêu cầu. Root đọc AGENTS.md; project config đăng ký 4 role. Nếu client không nạp role/skill mới trong phiên hiện tại, mở lại phiên hoặc truyền role instructions qua subagent tools. File TOML không tự bổ sung tính năng subagent vào một client không hỗ trợ.

### Kết nối Elementor cho mỗi môi trường

Credential không đi theo Git. Nếu môi trường đã kết nối và tools/list hoạt động, dùng kết nối đó. Nếu cần cấu hình Codex mới, chạy trong terminal tương tác:

```sh
python scripts/connect_elementor.py --username YOUR_WORDPRESS_USERNAME
```

Nhập Application Password tại prompt ẩn. Script xác minh MCP initialize, rồi lưu riêng vào `$CODEX_HOME/config.toml` nếu được cấu hình, hoặc thư mục home của máy: `~/.codex/config.toml` trên Linux/macOS, `%USERPROFILE%\.codex\config.toml` trên Windows. Không đổi các server khác. Server cùng tên đã có sẽ bị từ chối, trừ khi chủ động thêm `--replace`.

Mỗi máy nên dùng Application Password riêng để thu hồi độc lập. Không dùng mật khẩu quản trị chính; không paste secret vào repo, brief, command history hoặc chat. Config/backup nằm ngoài repo và có chứa secret; local OS phải bảo vệ tài khoản/thư mục đó. Không đặt CODEX_HOME trong repo. Có thể revoke tại WordPress → Users → Profile → Application Passwords.

### Cloud

Clone/open repo trong môi trường cloud có Python và công cụ agent. Kết nối WordPress và Google Drive qua cơ chế kết nối/secret của nền tảng; không commit secret. Nếu cloud có terminal tương tác và dùng Codex CLI, có thể dùng script kết nối như local. Nếu không có terminal tương tác, cấu hình MCP bằng UI hoặc secret provisioning được nền tảng hỗ trợ; không tự động đưa password lên command line. Kiểm tra egress HTTPS tới website/Google, quyền truy cập Drive và tool availability ở mỗi phiên.

Google Drive/Docs là kết nối riêng: cấu hình plugin/OAuth của client đang dùng; Elementor MCP không cấp quyền Drive. Nếu không có connector, user có thể cung cấp file export và ảnh tại local để tiếp tục. Gate 1 vẫn cần user sửa với Gemini và xác nhận. Browser/render QA cần browser tools của môi trường; thiếu thì báo UNVERIFIED, không giả định đã xem giao diện.

GitHub Actions được cấu hình kiểm tra Ubuntu/Windows/macOS với Python 3.11/3.12. Đây là kiểm tra offline về cấu hình và gates; không kiểm chứng WordPress/Drive/browser của từng máy.

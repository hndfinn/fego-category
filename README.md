# FEGO Category agent

Bộ workflow riêng cho **WooCommerce category**: agent tạo bản nháp trực tiếp trên Google Doc kèm toàn bộ ảnh cần thiết trong cùng lượt; bạn review và viết lại bằng Gemini; agent triển khai bản Gemini lên WordPress. Không dùng quy trình viết blog.

## Dùng ngay

Clone repo về bất kỳ thư mục nào và mở thư mục repo làm workspace/project của Codex, rồi gửi:

> Dùng $fego-category cho category [URL]. Nguồn [Drive URL]. Block [ID nếu biết]. Tạo bản nháp trên Google Doc và các ảnh cần thiết.

Sau khi sửa bằng Gemini:

> Đây là bản Gemini [link Doc]. Triển khai lên WordPress cho category [URL].

Nếu chat hiện tại chưa nạp skill, yêu cầu đọc `AGENTS.md` và `.agents/skills/fego-category/SKILL.md` trong repo hiện tại trước khi làm. Bốn role TOML và project config đã có trong `.codex/`; chúng được dùng khi client nạp project này. Đây không phải cài đặt global vào mọi chat hoặc thay đổi cấu hình trên máy cá nhân. Không cần tạo chat mới nếu agent hiện tại đọc được các file và có công cụ subagent; có thể truyền role prompt tương ứng.

## Quy trình 3 bước, không gate duyệt trung gian

1. **Bản nháp + ảnh trong một lượt**: xem template/section category hiện tại và category tham chiếu, tính số đoạn/heading/ảnh theo từng section, rồi tạo một Google Doc kèm ảnh đã map đúng vị trí. Không duyệt dàn ý, không duyệt ảnh anchor, không quota ảnh.
2. **Bạn review và viết lại bằng Gemini** ngay trên Doc. Agent không thao tác Gemini thay bạn.
3. **Triển khai bản Gemini lên WordPress** khi bạn yêu cầu; không hỏi lại duyệt nội dung/duyệt đăng. Agent giữ nguyên lời văn, chỉ sửa lỗi kỹ thuật (link hỏng, thiếu alt, vỡ layout); sai fact hoặc cần viết lại đáng kể thì báo bạn.

Kiểm tra bắt buộc (không phải xin phép): đúng category/term ID và block ID, mapping ảnh–section có alt/provenance, QA chuẩn bị, backup giá trị hiện tại ngay trước khi ghi, rồi readback API + public HTML/render sau khi đăng. Chỉ hỏi khi target hoặc phạm vi vẫn mơ hồ sau khi kiểm tra read-only.

## Agent và subagent

Root điều phối là người duy nhất ghi Drive/CMS/SEO. Subagent trả đề xuất và evidence, không cùng ghi website:

| Role | Output |
|---|---|
| category_research | Facts, nguồn, IDs/URL, ảnh, mâu thuẫn |
| category_framework | Fit section/template, kế hoạch copy và mapping ảnh cho bản nháp Doc |
| category_seo | Trên bản Gemini: title/meta, heading, link, lỗi triển khai; giữ lời văn |
| category_qa | Review độc lập, PASS/FAIL/UNVERIFIED có bằng chứng |

Giữ nguyên model của agent cha. Chạy song song chỉ các phần độc lập; các bước phụ thuộc và mọi website write chạy tuần tự.

## Hồ sơ và preflight

`runs/<slug>/` được bỏ qua bởi Git: brief, link Doc, media map, bản Gemini đã freeze, facts, payloads, QA, backup và live QA. Không chứa bản sao credential.

Ví dụ CLI, chạy từ project root. `--message` ghi đúng lời user giao bản Gemini để triển khai:

```sh
python scripts/workflow.py init --run runs/new-category --category-url https://fegowoodworker.com/danh-muc/REPLACE/ --term-id 123 --block-id 456
python scripts/workflow.py record-draft --run runs/new-category --doc https://docs.google.com/document/d/REPLACE --media media-map.json
python scripts/workflow.py record-gemini --run runs/new-category --file gemini-source.md --message 'Lời user giao bản Gemini để triển khai'
python scripts/workflow.py prepare --run runs/new-category --manifest deployment-manifest.json
python scripts/workflow.py record-backup --run runs/new-category --file backup.json
python scripts/workflow.py check-deploy --run runs/new-category
# ... ghi WordPress, publish, rồi kiểm tra live ...
python scripts/workflow.py record-live-qa --run runs/new-category --file live-qa.json
```

Template trong `templates/`: `media-map.json` (ảnh → section, alt, caption, provenance), `deployment-manifest.json`, `qa-preflight.json`, `backup.json`, `live-qa.json`. `prepare` chỉ thành công khi target có term ID + block ID khớp, manifest bao gồm bản Gemini + media map + QA và mọi check chuẩn bị PASS. `check-deploy` yêu cầu thêm backup đúng target. `record-live-qa` đặt `complete` chỉ khi mọi live check PASS, ngược lại `needs_attention`.

Helper chỉ kiểm tra local hash/state; không tự gọi website, không cấp quyền và không chứng minh live QA. Coordinator vẫn phải re-read live baseline, backup, apply/publish và kiểm tra public category. Không đánh dấu hoàn tất nếu render QA chưa xác minh được.

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

Các test kiểm tra hash nguồn Gemini, target category/block, media mapping, QA, backup và trạng thái live QA; không xác nhận runtime WordPress hay đăng bài.

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

Để dùng cùng MCP từ các thiết bị truy cập **cùng cloud**, chạy bước sau trong
setup/startup của cấu hình cloud `fego-category`, trước khi khởi động agent:

```sh
python scripts/cloud_elementor.py
```

Script giữ kết nối Elementor đã có, chạy MCP `initialize`, thông báo
`initialized` và toàn bộ các trang `tools/list`. Nếu chưa có cấu hình trong
runtime, script nhận `FEGO_WP_USERNAME` và `FEGO_WP_APPLICATION_PASSWORD` từ
secret cloud rồi chỉ lưu cấu hình sau khi kiểm tra thành công. Không đặt giá trị
secret vào startup command, Git hoặc chat. Cấu hình được lưu riêng ngoài repo,
quyền file 0600. Không thay cấu hình server khác và không ghi website.

Nền tảng phải cấp credential trong setup và/hoặc nạp lại cấu hình khi tạo runtime
mới; một file tạo thủ công trong container cũ không bảo đảm tồn tại ở lần chạy
sau. Cho phép HTTPS tới `fegowoodworker.com` trong network policy của cloud.
Nếu đã có tên biến secret khác, giữ setup hiện có để nạp kết nối; không cần tạo
credential mới chỉ để đổi tên biến.

Kiểm tra lại kết nối mà không lưu cấu hình:

```sh
python scripts/cloud_elementor.py --check-only
```

Kết quả PASS xác nhận transport và danh sách tool, chưa xác nhận tool được nạp
native vào chat hoặc quyền từng đối tượng. Sau khi lưu setup cloud, tạo một phiên
cloud mới, xác nhận agent gọi được một tool đọc thật từ `tool_names`; thử lại từ
thiết bị thứ hai bằng cùng tài khoản/cloud. Không dùng lệnh ghi CMS làm phép thử.
Repo không tự sửa setup/secret/network policy đã lưu trên nền tảng. Thay đổi
script trong repo phải được đưa vào nhánh mà cấu hình cloud checkout trước khi
startup sử dụng được.

Clone/open repo trong môi trường cloud có Python và công cụ agent. Kết nối WordPress và Google Drive qua cơ chế kết nối/secret của nền tảng; không commit secret. Nếu cloud có terminal tương tác và dùng Codex CLI, có thể dùng script kết nối như local. Nếu không có terminal tương tác, cấu hình MCP bằng UI hoặc secret provisioning được nền tảng hỗ trợ; không tự động đưa password lên command line. Kiểm tra egress HTTPS tới website/Google, quyền truy cập Drive và tool availability ở mỗi phiên.

Google Drive/Docs là kết nối riêng: cấu hình plugin/OAuth của client đang dùng; Elementor MCP không cấp quyền Drive. Nếu không có connector, user có thể cung cấp file export và ảnh tại local để tiếp tục. Bản triển khai vẫn là bản user đã sửa bằng Gemini. Browser/render QA cần browser tools của môi trường; thiếu thì báo UNVERIFIED, không giả định đã xem giao diện.

GitHub Actions được cấu hình kiểm tra Ubuntu/Windows/macOS với Python 3.11/3.12. Đây là kiểm tra offline về cấu hình và preflight; không kiểm chứng WordPress/Drive/browser của từng máy.

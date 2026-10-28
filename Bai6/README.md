# Bài 6: Bảo mật với DevSecOps

Thực hành CI/CD với GitLab (mục 6.2), gồm 2 phần:

| Phần | Nội dung | Sách |
|---|---|---|
| test-project (trên GitLab) | Pipeline đầu tiên: 4 job `build-job`, `test-job1`, `test-job2`, `deploy-prod` qua 3 stage build → test → deploy | 6.2.1 |
| `pipeline-tutorial/` | Site Docusaurus + `.gitlab-ci.yml` build bằng Node và triển khai lên GitLab Pages | 6.2.2 |
| Mở rộng | Thêm các security gate vào pipeline trên: SCA (`npm audit`), SAST (Semgrep), Secret Detection (Gitleaks) | 6.1 |
| `screenshots/` | Ảnh kết quả chạy thực tế | |

Môi trường: Windows 11, Git 2.55, Node.js 24.19, npm 12.0; runner là **instance runner
có sẵn của GitLab.com** (không tự dựng runner).

Repo GitLab:

- `https://gitlab.com/Counting128/test-project` (private)
- `https://gitlab.com/Counting128/my-pipeline-tutorial-project`

---

## 1. Tạo và chạy pipeline đầu tiên (6.2.1)

### Chuẩn bị

Kiểm tra Git, Node.js, npm trên máy:

![versions](screenshots/01_env_versions.png)

Tạo project trống `test-project` trên GitLab.com (khởi tạo kèm README):

![test-project](screenshots/02_test_project.png)

Vào **Settings > CI/CD > Runners**: tab *Instance* có 136 runner dùng chung, đã bật
*Turn on instance runners for this project* nên không cần tạo runner riêng:

![runners](screenshots/03_runners.png)

### Tạo `.gitlab-ci.yml`

Trong **Code > Repository**, chọn nhánh `main` → **+ > New file**, đặt tên
`.gitlab-ci.yml` và dán cấu hình của sách:

```yaml
build-job:
  stage: build
  script:
    - echo "Hello, $GITLAB_USER_LOGIN!"

test-job1:
  stage: test
  script:
    - echo "This job tests something"

test-job2:
  stage: test
  script:
    - echo "This job tests something, but takes more time than test-job1."
    - echo "After the echo commands complete, it runs the sleep command for 20 seconds"
    - echo "which simulates a test that runs 20 seconds longer than test-job1"
    - sleep 20

deploy-prod:
  stage: deploy
  script:
    - echo "This job deploys something from the $CI_COMMIT_BRANCH branch."
  environment: production
```

![new file](screenshots/04_new_gitlab_ci_yml.png)

Bấm **Commit changes** → pipeline tự chạy.

### Kết quả

**Pipeline #2995334754 – Passed:** 3 stage build → test → deploy, 4 job đều xanh;
`test-job1` và `test-job2` cùng stage nên chạy song song. Tổng 1 phút 34 giây:

![pipeline](screenshots/05_pipeline_stages.png)

Tab **Jobs**: `test-job2` mất 44 giây, lâu hơn `test-job1` (25 giây) đúng vì có `sleep 20`:

![jobs](screenshots/06_pipeline_jobs.png)

**Log `build-job`:** biến `$GITLAB_USER_LOGIN` được điền khi chạy → `Hello, Counting128!`:

![build-job](screenshots/07_job_build_job.png)

**Log `deploy-prod`:** `$CI_COMMIT_BRANCH` được điền → `This job deploys something from
the main branch.`, kết thúc `Job succeeded`:

![deploy-prod](screenshots/08_job_deploy_prod.png)

---

## 2. Pipeline build và deploy site Docusaurus (6.2.2)

```
pipeline-tutorial/
├── .gitlab-ci.yml          # build → test → deploy: build-job, dependency-audit, SAST,
│                           #   secret_detection, pages (bản cuối, gồm cả phần mở rộng)
├── docusaurus.config.js    # url / baseUrl trỏ về GitLab Pages của project
├── package.json            # Docusaurus 3.10.2
├── blog/  docs/  src/  static/   # nội dung site mẫu do npm init docusaurus sinh ra
└── .gitignore              # bỏ node_modules/, build/, .docusaurus/
```

### Tạo project Docusaurus

```powershell
git clone https://gitlab.com/Counting128/my-pipeline-tutorial-project.git pipeline-tutorial
cd pipeline-tutorial
npm init docusaurus            # chọn toàn bộ mặc định, site sinh trong website/
mv website/* .                 # chuyển lên thư mục gốc
rm -r website
```

![npm init docusaurus](screenshots/09_npm_init_docusaurus.png)

Sửa `docusaurus.config.js`:

```js
url: 'https://Counting128.gitlab.io',
baseUrl: '/my-pipeline-tutorial-project/',
```

![docusaurus config](screenshots/10_docusaurus_config.png)

```powershell
git add .
git commit -m "Add simple generated Docusaurus site"
git push origin
```

Sau khi push, project trên GitLab có đủ `blog/`, `docs/`, `src/`, `static/`, `docusaurus.config.js`, `package.json`...
(`node_modules/` không bị đẩy lên vì đã có trong `.gitignore`):

![pushed](screenshots/11_docusaurus_pushed.png)

### Xây dựng `.gitlab-ci.yml` từng bước

Các bước sau đều sửa trực tiếp bằng **Build > Pipeline editor** trên GitLab (mỗi bước
là một commit `Update .gitlab-ci.yml file`), sau đó `git pull` về máy.

**Bước 1 – job đầu tiên:**

```yaml
test-job:
  script:
    - echo "This is my first job!"
    - date
```

Log job in `This is my first job!` và giờ hiện tại của runner (`Tue Oct 27 16:31:44 UTC 2026`):

![test-job](screenshots/12_job_test_job.png)

**Bước 2 – job build site,** lưu thư mục `build/` thành artifacts:

```yaml
build-job:
  image: node:20
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - "build/"
```

Trong Pipeline editor, GitLab kiểm tra cú pháp ngay khi sửa (*Pipeline syntax is
correct*). Sau khi commit, pipeline #2995466830 tự chạy cho commit `c917ee67`:

![pipeline editor](screenshots/13_pipeline_editor_build_job.png)

Log `build-job`: `npm install` cài 1295 gói, `docusaurus build` báo
`[SUCCESS] Generated static files in "build"`, sau đó upload 139 file của `build/` lên làm
artifacts:

![build-job](screenshots/14_job_build_site.png)

Bấm **Browse** ở bên phải log để xem artifacts: `index.html`, `404.html`, `sitemap.xml`,
các thư mục `assets/`, `blog/`, `docs/`...:

![artifacts](screenshots/15_build_artifacts.png)

**Bước 3 – thêm stage và job `pages`** để triển khai lên GitLab Pages (bản cuối theo
sách; phần mở rộng ở mục 3 sửa tiếp file này):

```yaml
stages:
  - build
  - deploy

build-job:
  stage: build
  image: node:20
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - "build/"

pages:
  stage: deploy
  script:
    - mv build/ public/
  artifacts:
    paths:
      - "public/"
```

Job `pages` tự nhận artifacts `build/` từ `build-job`, đổi tên thành `public/` (thư mục
GitLab Pages đọc), sau đó GitLab sinh thêm job `pages:deploy` để xuất bản site.

### Kết quả

**Pipeline #2995487834 – Passed:** 2 stage build → deploy, ngoài `build-job` và `pages`
còn có job `pages:deploy` do GitLab tự thêm:

![pipeline pages](screenshots/16_pipeline_pages.png)

**Deploy > Pages:** bỏ tick *Use unique domain* rồi bấm **Save changes** để URL có dạng
`<user>.gitlab.io/<project>`, khớp với `url`/`baseUrl` đã đặt (nếu để domain riêng thì
site sẽ hỏng đường dẫn CSS/JS do sai `baseUrl`):

![pages settings](screenshots/17_pages_settings.png)

**Site Docusaurus chạy trên GitLab Pages** tại
`https://counting128.gitlab.io/my-pipeline-tutorial-project/`:

![site](screenshots/18_site_gitlab_pages.png)

---

## 3. Mở rộng: thêm security gate vào pipeline (6.1)

Pipeline ở mục 2 chỉ build và deploy, chưa có bước kiểm tra bảo mật nào. Phần này thêm
một stage `test` nằm giữa build và deploy, gồm 3 loại kiểm thử tự động của mục 6.1.2:

| Job | Loại | Công cụ | Nguồn |
|---|---|---|---|
| `dependency-audit` | SCA – lỗ hổng thư viện bên thứ ba | `npm audit` | tự viết |
| `semgrep-sast` | SAST – phân tích mã nguồn | Semgrep | template `Jobs/SAST.gitlab-ci.yml` |
| `secret_detection` | Secret Scanning – lộ token/mật khẩu | Gitleaks | template `Jobs/Secret-Detection.gitlab-ci.yml` |

`.gitlab-ci.yml` sau khi mở rộng (xem
[pipeline-tutorial/.gitlab-ci.yml](pipeline-tutorial/.gitlab-ci.yml)):

```yaml
stages:
  - build
  - test
  - deploy

include:
  - template: Jobs/SAST.gitlab-ci.yml
  - template: Jobs/Secret-Detection.gitlab-ci.yml

build-job:
  stage: build
  image: node:20
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - "build/"

dependency-audit:
  stage: test
  image: node:20
  script:
    - npm audit --audit-level=critical
  allow_failure: true

pages:
  stage: deploy
  script:
    - mv build/ public/
  artifacts:
    paths:
      - "public/"
```

Hai template của GitLab tự thêm job vào stage `test`. Với SAST, GitLab dò ngôn ngữ trong
repo (ở đây là JavaScript) rồi chọn analyzer phù hợp, nên job có tên `semgrep-sast`.

### 3.1 SCA chặn deploy khi có lỗ hổng critical

Lần đầu thêm `dependency-audit` chưa có `allow_failure`. `npm audit --audit-level=critical`
trả về exit code 1 khi có ít nhất một lỗ hổng mức critical, nên job **fail**. Stage `test`
fail kéo theo job `pages` ở stage `deploy` **bị bỏ qua**, site không được deploy. Đây chính
là cơ chế "cửa chắn" (security gate) của mục 6.1.1:

![pipeline failed](screenshots/19_ext_pipeline_audit_failed.png)

Log job liệt kê từng gói lỗi (ví dụ `tinypool`: Prototype Pollution dẫn tới RCE, mức
critical; `uuid`: thiếu kiểm tra biên buffer, mức moderate). Tổng **22 lỗ hổng (6 moderate,
1 high, 15 critical)**, khớp với cảnh báo ở log `build-job` (ảnh 14). Kết thúc bằng
`ERROR: Job failed: exit code 1`:

![dependency-audit log](screenshots/20_ext_dependency_audit_log.png)

Các lỗ hổng này nằm trong dependency của Docusaurus. `npm audit fix --force` sẽ hạ
`@docusaurus/core` xuống 3.7.0 (breaking change) nên mình không sửa. Thay vào đó mình
thêm `allow_failure: true`: job vẫn chạy và báo lỗi, nhưng không chặn deploy nữa. Pipeline
chuyển sang trạng thái **Warning** (job `dependency-audit` hiện dấu `!` màu cam), còn
`pages` và `pages:deploy` chạy bình thường:

![pipeline warning](screenshots/21_ext_pipeline_allow_failure.png)

> `allow_failure: true` chỉ để bài lab vẫn deploy được. Trong dự án thật, nên giữ job
> chặn (bỏ `allow_failure`) và nâng cấp hoặc thay gói lỗi, hoặc chỉ chấp nhận ngoại lệ có
> ghi lý do rõ ràng.

### 3.2 Secret Detection phát hiện token bị lộ

Để thử job `secret_detection`, mình commit file `demo-leak.txt` chứa một **token GitLab
giả** (dạng `glpat-xxxxxxxxxxxxxxxxxxxx`, không phải token thật):

```text
# Token GIA de demo Secret Detection
GITLAB_TOKEN=glpat-...
```

Gitleaks quét các commit mới, in `1 commits scanned` và `leaks found: 1`, rồi lưu kết quả
vào artifact `gl-secret-detection-report.json`:

![secret detection log](screenshots/22_ext_secret_detection_log.png)

Mở report: phát hiện **GitLab personal access token**, mức **Critical**, tại file
`demo-leak.txt`, kèm hướng dẫn thu hồi (revoke) token:

![secret detection report](screenshots/23_ext_secret_detection_report.png)

Sau khi demo xong, mình xoá `demo-leak.txt` ở commit tiếp theo (`Delete demo-leak.txt`).

Hai điểm cần chú ý:

- Job vẫn **Passed** dù tìm thấy secret. Template mặc định của GitLab chỉ **báo cáo**,
  không làm fail pipeline. Muốn chặn hẳn thì phải tự thêm bước kiểm tra report hoặc dùng
  security policy (bản GitLab Ultimate).
- Xoá file **không xoá secret khỏi lịch sử git**: token vẫn nằm trong commit `25dac4f`.
  Với token thật thì việc đầu tiên phải làm là **revoke** token, sau đó mới tính tới viết
  lại lịch sử (`git filter-repo`). Token trong bài là giả nên không ảnh hưởng.

### 3.3 SAST với Semgrep

Job `semgrep-sast` (Semgrep 1.181.0, analyzer 6.30.0) quét mã JavaScript của site và
xuất `gl-sast-report.json`. Kết quả `"vulnerabilities": []`: mã mẫu Docusaurus không có
lỗi nào khớp bộ luật của Semgrep:

![sast report](screenshots/24_ext_sast_report.png)

Ba job trên bổ sung cho nhau: SCA bắt lỗ hổng ở **thư viện**, SAST ở **mã mình viết**,
Secret Detection ở **dữ liệu nhạy cảm bị commit nhầm**. SCA tìm ra 22 lỗ hổng trong khi
SAST không ra lỗi nào, cho thấy với site tĩnh thế này rủi ro chủ yếu nằm ở dependency.

---

## Những điểm khác so với sách

- **`image: node:20` thay vì `image: node`.** Sách dùng tag mặc định (`latest`), mình
  ghim phiên bản LTS để build ổn định, không bị đổi khi image `node` lên bản mới.
- **Image mặc định của runner là `ruby:3.1`** (log ở ảnh 07/08) chứ không phải
  `ruby:2.5` như ảnh trong sách — các job ở phần 1 không khai báo `image` nên dùng image
  mặc định của instance runner GitLab.com hiện tại.
- **Nhánh mặc định là `main`** thay vì `master` như ảnh trong sách (mặc định của GitLab mới).
- Project để **private** nên GitLab bật *Access Control* cho Pages (cảnh báo đỏ ở ảnh 17):
  chỉ tài khoản có quyền mới xem được site. Muốn công khai thì vào **Settings > General >
  Visibility** và chọn *Everyone* cho Pages.
- Sửa `.gitlab-ci.yml` bằng Pipeline editor trên web nên commit nằm trên GitLab trước,
  local được `git pull` về sau.

- **Phần mở rộng (mục 3) không có trong sách.** Sách mục 6.2 chỉ dừng ở build và deploy;
  mình thêm stage `test` với SCA, SAST và Secret Detection để áp dụng lý thuyết mục 6.1.

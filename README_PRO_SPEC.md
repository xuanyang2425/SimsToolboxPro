# SimsToolbox Pro：整体软件 AI 描述（用于重构范例）

## 0. 软件定位

SimsToolbox Pro 是一个面向《模拟人生4》玩家的“专业级工具箱”，核心目标不是“替你替换游戏机制”，而是帮你管理海量 Mod/CC 与下载来源，降低重复下载、忘记用途、更新/移除出错、排错困难等长期痛点。

软件以“工作区 + 面板停靠 + 多标签并行”的专业 UI 形态呈现（类似 VS Code / PS），支持未来持续增加功能模块而不破坏整体结构。

## 1. 关键痛点与解决目标（必须覆盖）

### 1.1 玩家常见痛点

- Mod 数量巨大（上万），文件名英文、时间久了忘了用途。
- 一个 Mod 往往是“文件集合”，可能散落在多个路径：外层 ts4script + 子文件夹 package + overrides。
- 更新/移除容易漏文件，导致冲突或残留。
- 新装一堆 Mod 后报错，不知道哪些是新装的，排错效率低。
- 来源链接可能不完整，Required 依赖可能是外站，无法自动下载。
- 不同工具（下载器、文件管理、版本转换、mod管理）分散，不便同时操作。
- 任何“危险的回滚/覆盖/重命名”都可能损坏现有可用 Mod 结构，需要“安全、可撤销、可同步外部变更”。

### 1.2 解决目标（设计原则）

- 不重命名原文件（保持作者命名）。
- 组别（分组）是虚拟的：用于归类、批量操作，不强制等同文件夹结构。
- 停用/启用以“移动到停车区/移回原处”为主，天然可逆；提供 Undo/Redo。
- 允许用户绕过工具直接改 Mods 文件夹：软件需能检测外部变更并同步。
- 上万规模性能优先：增量扫描、数据库索引、虚拟列表、后台任务与进度。
- 模块化架构：未来新增功能模块可“插件式接入”。

## 2. UI 总体形态（必须做成“正规软件”）

### 2.1 主窗口结构（Qt / PySide6）

- QMainWindow 主框架。
- 左/右/底：QDockWidget 停靠面板（可拖拽、可隐藏、可并排）。
- 中央：QTabWidget 标签页区（功能可同时打开，像 VS）。
- 顶部：菜单栏 + 工具栏 + 全局搜索 + 命令面板入口（Ctrl+P）。
- 底部：状态栏（任务进度、扫描状态、外部变更提示、当前根目录）。

### 2.2 核心 UX 规范（必须落地）

- 弹窗永远相对父窗口居中，Esc 取消 Enter 确认。
- 任何刷新都要保持：树的展开状态、选中项、滚动位置。
- 300ms 操作必须有反馈；长任务必须显示进度/阶段文本，可取消。
- 不用“烦人弹窗”刷屏：使用通知中心；危险操作才二次确认。
- 批量操作一等公民：多选、全选、筛选全选、批量加入组、批量停用、批量备注。
- 右键菜单高频入口：复制信息、打开文件位置、打开链接、加入组、停用/启用、重试。
- 操作完成提供“撤销（Undo）提示条”（例如10秒内可点）。

## 3. 模块化架构（平台底座 + 模块）

### 3.1 Core 平台底座（稳定不变）

实现一套服务层，任何模块都通过服务层完成工作：

- DBService：SQLite + migrations（数据库版本迁移）。
- SettingsService：统一保存设置（目录、cookie、UI布局、最近目录等）。
- TaskService：后台任务调度（线程池/QtConcurrent），统一进度与取消。
- EventBus：事件总线（模块解耦）。
- LogService：统一日志流（底部日志面板订阅）。
- FileIndexService：Mods 扫描/增量索引/外部变更检测。
- OpLogService：文件操作日志 + Undo/Redo（比回滚安全）。
- DownloadMetaService：下载来源元信息解析（TSR页面解析、作者、发布时间、tags等）。

### 3.2 Modules 功能模块（可插拔）

每个模块以“插件式”注册到主程序：提供 Tab / Dock / Actions / Commands。

推荐模块（至少这些）：

- DownloaderModule：下载器（含 TSR 登录/可见浏览器登录/队列/重试/去重/外站链接提示）。
- ModManagerModule：虚拟组别/备注/停用启用/冲突标记/会话视图（最近新增）。
- FileManagerModule：真实文件夹浏览/高级批量操作（仍需走 OpLog 可撤销）。
- VersionConverterModule：版本转换器（独立工具页，后台任务）。

模块接口（范例）：

- module_id, name, version
- register_actions(app)
- create_docks(app)
- create_tabs(app)
- subscribe_events(bus)

## 4. 核心数据模型（必须支持“上万 Mod”）

### 4.1 数据库必须区分两类事实

- 事实 A：文件系统现状（来自 FileIndexService 扫描）。
- 事实 B：来源与语义元信息（来自下载器/网页解析/用户备注）。
- 事实 C：虚拟组别关系与操作历史。

### 4.2 推荐表（V1）

**file_index**

- id
- abs_path（唯一）
- rel_path（相对 Mods 根）
- file_name
- ext
- size
- mtime
- quick_sig（size+mtime）
- sha1（可空，按需计算）
- first_seen_at
- last_seen_at
- status（normal/missing/changed）
- source（external/downloader/import）

**downloads**

- url（唯一）
- domain
- item_id
- file_name
- file_path
- file_size
- status（success/failed/skipped）
- downloaded_at

**mod_meta**

- item_id（唯一）
- title
- creator
- publish_date
- tags_json（多级分类/标签，允许同级）
- required_links_json（外站依赖）
- notes（用户备注）
- last_updated_at

**groups（虚拟组别）**

- id
- name
- parent_id
- created_at

**group_members**

- group_id
- member_type（file / url / item / logical_mod）
- ref（路径/URL/item_id）
- created_at

**disabled_map（停用启用映射）**

- abs_path_src
- abs_path_disabled
- disabled_at
- reason（group/oneoff）

**op_log**

- id
- op_type（move/copy/delete/disable/enable）
- payload_json（源/目标/文件列表）
- status
- created_at

**settings_kv**

- key
- value_json

### 4.3 性能要求

- 所有高频字段索引：abs_path, item_id, creator, downloaded_at, group_id。
- 搜索建议启用 FTS5：title/notes/creator/tags。

## 5. 核心业务行为（必须实现的关键流程）

### 5.1 启动行为

- 默认快速启动：读 DB + 恢复布局。
- 提示“上次扫描时间/检测到外部变更数量”。
- 用户可手动点击“同步扫描”，后台跑 FileIndexService，并显示进度。
- 扫描完成触发事件 index.updated。

### 5.2 外部变更检测与同步

- 扫描后对照 file_index：新增、消失、变更（size/mtime）。
- UI 顶部横幅提示，可一键“同步到数据库视图”。
- 不强制阻止用户外部操作。

### 5.3 虚拟组别与批量停用

- 组别是虚拟分类工具，不等同文件夹结构。
- 用户可对筛选结果/选中项批量加入组别。
- “停用组别”：将该组成员的文件移动到 __DISABLED__/<group_name>/...
- 默认只移动文件；仅当文件夹“纯净”时允许移动整个文件夹。
- “启用组别”：按 disabled_map 移回原处。
- 任何移动都写入 op_log，并可 Undo。

### 5.4 下载器与去重

- 解析用户粘贴的“带标题的链接列表”，自动提取 URL。
- TSR 登录支持“可见浏览器登录”获取 cookie/session。
- 下载前检查：
  - downloads 是否已存在。
  - file_index 是否已存在同名/同 hash。
- 外站链接标红，可一键打开全部外站链接。
- 下载完成写入 downloads + mod_meta（可延迟补全）并发事件 download.finished。

## 6. 现代化增强点（可作为 V1.1/2.0）

- 命令面板（Ctrl+P）：搜索动作/模块/组别/Mod。
- 视图预设：保存常用筛选组合。
- 任务中心：统一显示后台任务，可取消重试。
- 通知中心：替代弹窗刷屏。
- 问题 Mod 视图：重复文件/同名不同 hash/脚本深度异常/缺失依赖。
- 安全模式：临时停用所有 script mods（只移动 .ts4script）。

## 7. 输出要求（给重构范例工程）

### 7.1 工程结构要求

- 采用 core/ + modules/ + ui/ 分层。
- 所有业务逻辑不得直接依赖 UI（可测试、可迁移）。
- UI 只负责展示与调用服务。
- 所有耗时操作必须走 TaskService，不允许 UI 卡死。

### 7.2 交付内容（范例版）

可运行主程序（Qt）。至少实现：

- Dock + Tab 框架。
- 日志面板、任务面板、状态栏。
- Settings 持久化（目录、布局）。
- FileIndexService 的基础扫描 + 外部变更提示。
- ModManager 的虚拟组别 + 停用/启用（移动到停车区）+ Undo（最小实现）。
- 下载器可先以“链接解析 + 队列 UI + 去重检查”的骨架为主，登录/下载能力后续补齐。

## 8. 风险与边界（必须明确）

- 不承诺替代游戏内 Mod 开关；只提供文件层面管理与提示。
- 不强制用户必须通过工具安装/管理；外部变更可检测并提示同步。
- 不做危险的“全量回滚覆盖”；以 Undo 与停车区移动为主。
- 对上万文件必须保证：列表虚拟化、扫描增量、任务后台化。

## 9. 参考说明

SimsToolbox.zip 是旧代码参考包，尤其是下载模块，可以作为重构时的实现参考。

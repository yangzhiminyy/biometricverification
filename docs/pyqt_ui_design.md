# PyQt 桌面客户端设计方案

## 1. 目标
- 构建与 Web 前端一致的桌面体验，支持人脸识别的录入、验证、用户查看与删除。
- 抽象 GUI 与业务逻辑，便于后续复用到声纹、指纹模块。
- 采用 PyQt6（或 PyQt5）实现跨平台 UI，利用现有 FastAPI 接口进行交互。

## 2. 技术选型
- **框架**：PyQt6（若需兼容旧环境可选择 PyQt5）。
- **网络层**：`requests` 或 `httpx` 进行 REST 调用；异步需求可引入 `QThread`/`asyncio`。
- **状态管理**：使用 `QObject` + `pyqtSignal` 通知 UI 更新；定义独立的 `BiometricClient` 类封装 API 调用。
- **结构模式**：推荐采用 `Model-View-Controller` 或 `View-Model`（结合 `QAbstractTableModel`）分离视图与逻辑。

## 3. 界面规划

### 3.1 主窗体
- 顶部菜单/工具栏：切换页面、刷新、设置。
- 左侧导航（`QListWidget`/`QTreeWidget`）：模块目录（Dashboard、Enroll、Verify、User）。
- 右侧内容区域：使用 `QStackedWidget` 切换各功能页。

### 3.2 Dashboard 页面
- 显示启用的模态列表（调用 `/biometric/modalities`）。
- 快速按钮：跳转到录入、验证、用户查询。
- 可展示最近操作日志（可选）。

### 3.3 录入页面
- 表单包含：
  - 模态选择（`QComboBox`）。
  - 用户 ID (`QLineEdit`)。
  - 样本列表（`QListWidget` + 添加/删除按钮）。
    - 支持文本输入、文件选择（`QFileDialog`），后续可扩展摄像头采集（`QtMultimedia`）。
- 提交按钮 -> `BiometricClient.enroll`；展示响应及存储路径，使用 `QTextEdit` 或 `QMessageBox`。

### 3.4 验证页面
- 输入模态、样本、top_k。
- 提交后显示匹配结果（`QTableView` + 自定义 `QAbstractTableModel`）。
- 标记最高得分、展示阈值对比。

### 3.5 用户详情页面
- 表单：模态、用户 ID。
- 查询后显示样本列表（`QListView` 或 `QTableView`）。
- 删除按钮：确认后调用 API，刷新视图。

### 3.6 状态与反馈
- 全局状态栏显示请求进度与结果。
- 使用 `QProgressDialog` 或 Loading 图标提示耗时操作。
- 错误统一通过弹框或状态栏输出。

## 4. 模块划分
- `ui/main_window.py`：主窗体、导航、页面切换。
- `ui/pages/dashboard.py`、`ui/pages/enroll.py` 等：各页面对应的 QWidget。
- `services/api_client.py`：请求封装，提供 `get_modalities`、`enroll`、`verify`、`get_user`、`delete_user`。
- `models/match_table_model.py`：封装匹配结果表格数据。
- `utils/config.py`：读取配置（API 基地址等）。
- `resources/`：图标、样式表（可加载 `.qss`）。

## 5. 线程与异步
- 为避免 UI 阻塞，API 调用通过 `QThread` 或 `QtConcurrent` 异步执行：
  - 页面发起请求 -> 启动工作线程 -> 完成后通过信号更新 UI。
- 若使用 `httpx` + `asyncio`，需结合 `QEventLoop` 或 `QAsyncio`，但复杂度更高，建议初版使用线程模型。

## 6. 样式与主题
- 使用 Qt Style Sheet 定制主色、按钮样式，使桌面端与 Web 端风格一致。
- 提供浅色/暗色主题切换（可选）。

## 7. 开发步骤
1. 初始化 PyQt 项目结构，配置虚拟环境与打包脚本（PyInstaller）。
2. 实现 `BiometricClient`，可复用前端的接口路径和数据结构。
3. 搭建主窗口与导航框架。
4. 逐步实现 Dashboard、Enroll、Verify、User 页面。
5. 处理异步请求与错误反馈。
6. 撰写使用说明，打包成可执行程序（Windows `.exe`、macOS `.app`）。

## 8. 后续扩展
- 集成摄像头采集（OpenCV + QtMultimedia）。
- 实时验证模式（轮询摄像头/麦克风）。
- 日志与通知中心（显示接口调用记录、模型版本信息）。
- 国际化支持（Qt 自带翻译机制）。

---

该文档为 PyQt 桌面端的初步设计蓝图，可在 Web UI 功能稳定后逐步实现。


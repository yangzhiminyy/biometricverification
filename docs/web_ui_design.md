# Web UI 设计方案（React）

## 1. 目标与范围
- 构建一个 React Web 前端，提供人脸识别模块的录入、验证、查询、删除等操作界面。
- 保持架构可扩展，后续可以快速接入声纹、指纹等模态。
- 与现有 FastAPI 接口对接，提供基础的错误处理、状态反馈和数据可视化。

## 2. 功能概览
- **首页仪表盘**
  - 展示当前启用的模态列表（调用 `/biometric/modalities`）。
  - 快速入口按钮：录入、验证、查询。
- **录入页面**
  - 表单：用户 ID、样本上传/录制（第一版支持文本、文件上传占位）。
  - 支持批量添加样本（列表/拖拽），未来可扩展摄像头实时采集。
  - 显示录入结果、存储路径。
- **验证页面**
  - 输入样本（文本占位或文件上传）。
  - 设置 `top_k` 和阈值（可选）。
  - 展示匹配结果列表（用户 ID、分数、元数据）。
- **用户详情页面**
  - 查询指定用户（GET `/biometric/{modality}/{user_id}`）。
  - 显示存储的样本列表、支持删除操作。
- **全局反馈**
  - Loading、成功/失败提示。
  - 错误统一展示，便于调试。

## 3. 技术选型
- **框架**：React + TypeScript。
- **构建工具**：Vite。
- **UI 库**：Ant Design（简化表单、表格、弹窗实现）。
- **状态管理**：React Query 管理异步数据；必要时使用 Zustand/Context。
- **HTTP 客户端**：axios 或原生 fetch（结合 React Query）。
- **样式方案**：Ant Design 默认 + Tailwind/LESS（按需）。

## 4. 项目结构建议
```
web/
  frontend/
    package.json
    vite.config.ts
    tsconfig.json
    src/
      main.tsx
      App.tsx
      pages/
        Dashboard.tsx
        Enroll.tsx
        Verify.tsx
        UserDetail.tsx
      components/
        Layout/
        Forms/
        ResultTable.tsx
      api/
        client.ts        # axios 实例
        biometric.ts     # 封装 API 调用
      hooks/
        useModalities.ts
        useEnroll.ts
        useVerify.ts
      utils/
        notifications.ts
      assets/
```

## 5. 状态与数据流
- **React Query 管理**：
  - `useQuery`：模态列表、用户详情。
  - `useMutation`：录入、验证、删除操作，结合乐观更新/刷新。
- **表单状态由 Ant Design Form 控制**；多样本输入使用动态表单项。
- **全局上下文**：可选，存储当前选择的模态、用户等信息。

## 6. API 对接
- 创建 `api/biometric.ts`：
  - `getModalities()`
  - `enroll({ modality, userId, samples })`
  - `verify({ modality, sample, topK })`
  - `getUser({ modality, userId })`
  - `deleteUser({ modality, userId })`
- 约定后端 baseURL 可通过 `.env` 配置，默认 `http://localhost:8000`.
- 错误处理：捕获 `axios` 异常并转成统一格式，使用通知组件提示。

## 7. 开发任务拆分
1. 初始化 Vite + React + TS 项目，配置 ESLint/Prettier。
2. 集成 Ant Design、React Query，创建基础 Layout（Header、Menu、Content）。
3. 实现 API 客户端封装与类型定义。
4. 开发页面：
   - Dashboard：模态列表 + 快速入口。
   - Enroll：表单 + 结果展示。
   - Verify：表单 + 匹配结果列表。
   - UserDetail：用户详情、删除。
5. 增加 Loading、Error、Success 通知与通用组件。
6. 编写简单的集成交互测试（React Testing Library）。
7. 文档补充：`README` 中加入前端启动说明。

## 8. 后续优化
- 文件上传/摄像头采集组件。
- 模型推理状态可视化（实时置信度图、日志查看）。
- 用户管理：搜索、分页、批量操作。
- 国际化、多模态切换的 UI 优化。
- 与 PyQt 客户端共享业务逻辑（提取公共服务层）。

---

该设计为初版实现的蓝图，后续可根据实际需求迭代。完成 Web UI 后，同步设计 PyQt 方案以保证桌面端体验一致。


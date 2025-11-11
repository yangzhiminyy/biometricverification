# Biometric Verification Platform

本项目致力于构建一个可扩展的多模态生物识别验证平台，当前聚焦人脸识别能力，并为后续声纹与指纹识别预留统一架构与流程。

## 当前状态
- 设计阶段：详见 `docs/face_module_design.md`。
- 正在搭建基础代码骨架与配置体系。

## 目录规划（初稿）
```
biometric_platform/
  core/                # 抽象基类、注册表、配置、任务编排
  modalities/
    face/              # 人脸识别具体实现
    voice/             # 声纹识别占位实现
    fingerprint/       # 指纹识别占位实现
  interfaces/          # API、GUI、CLI 接口层
  infrastructure/      # 数据存储、模型管理、日志、安全等
configs/                # 配置文件，如 biometric.yaml
datasets/               # 数据集（原始/处理后）
models/                 # 模型权重与配置
storage/                # 嵌入向量、数据库、缓存等
scripts/                # 辅助脚本（下载、训练、评估）
docs/                   # 设计文档与说明
```

## 快速开始（规划）
1. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. 配置 `configs/biometric.yaml` 指定当前生物模态、模型路径等。
3. 启动 FastAPI：
   ```bash
   uvicorn biometric_platform.interfaces.api.app:app --reload
   ```
4. 使用 API 进行录入/验证（后续将补充 GUI 与脚本示例）。

> 提示：`voice` 与 `fingerprint` 模块已提供占位实现，默认在配置中禁用；若需演示，可将 `enabled` 设为 `true` 并按需调整阈值、数据目录。

## API 示例
- 录入请求：
  ```bash
  curl -X POST http://localhost:8000/biometric/face/enroll \
       -H "Content-Type: application/json" \
       -d '{"user_id": "demo_user", "samples": ["sample_frame_1", "sample_frame_2"]}'
  ```
- 验证请求：
  ```bash
  curl -X POST http://localhost:8000/biometric/face/verify \
       -H "Content-Type: application/json" \
       -d '{"sample": "sample_frame_1", "top_k": 3}'
  ```

## 自检
- 运行脚本快速验证骨架是否可用：
  ```bash
  python scripts/smoke_test.py
  ```
  输出将包含 enroll 与 verify 的示例响应，主要用于验证配置与服务注册流程是否正常。

## 运行测试
- 安装依赖后执行：
  ```bash
  pytest
  ```
  目前包括注册表与多模态占位实现的基础单元测试。

## 辅助脚本
- `scripts/api_curl_examples.sh`：常用 curl 调用封装。示例：
  ```bash
  bash scripts/api_curl_examples.sh enroll
  bash scripts/api_curl_examples.sh verify
  ```
- `http/biometric_api.http`：配合 VS Code REST Client / IntelliJ HTTP Client 直接发送请求的范例。

## Web 前端
- React + Vite 项目位于 `web/frontend`。初始化后可执行：
  ```bash
  cd web/frontend
  npm install           # 已执行过可跳过
  npm run dev           # 在 http://localhost:5173 访问
  ```
- 可在 `web/frontend/.env` 中配置 `VITE_API_BASE_URL`（默认 `http://localhost:8000`）。
- 录入、验证页面已支持调用摄像头拍照并直接提交至后端，可在浏览器授权后体验。

## 模型训练
- 准备人脸训练数据：
  ```bash
  python training/scripts/prepare_face_dataset.py \
    --raw-root datasets/raw/face \
    --processed-root datasets/processed/face
  ```
- 运行占位训练脚本（后续可替换为真实模型）：
  ```bash
  python training/train_face.py --config training/configs/face_train.yaml
  ```

## 设计文档
- `docs/face_module_design.md`：人脸识别子系统设计与跨模态总体框架。
- `docs/implementation_plan.md`：阶段一实施计划与任务分解。

## 开发计划
- 阶段一：搭建核心骨架（配置、抽象类、注册表、基础 API）。
- 阶段二：实现人脸模块（录入、验证、模型加载、数据管理）。
- 阶段三：完善训练与数据集流程，准备声纹/指纹扩展。

更多细节与背景请参考设计文档并与团队讨论。欢迎贡献改进建议！


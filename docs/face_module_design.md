# 人脸识别子系统设计文档

## 1. 目标与范围
- **目标**：实现一个可扩展的人脸识别子系统，为未来引入声纹、指纹识别奠定统一架构。
- **范围**：覆盖人脸数据采集/录入、特征提取与验证、模型训练与管理、API 服务、GUI 客户端、数据集管理等模块。
- **约束**：优先使用 Python 技术栈（PyTorch、FastAPI、PyQt/Tkinter 等），保证模块化和可扩展性；遵循隐私与安全合规要求。

## 2. 跨模态总体框架设计

### 2.1 设计原则
- **统一抽象**：通过 `BiometricService`、`BiometricVerifier`、`BiometricDatasetManager` 等基类抽象录入、验证、数据管理能力，各模态只需实现具体适配器。
- **插件化扩展**：采用工厂或注册表模式，根据配置动态加载 `face`、`voice`、`fingerprint` 等实现；新增模态仅需提供实现包并注册即可。
- **解耦部署**：前端 GUI、API 网关、模型服务可独立部署或集成运行，满足桌面版与服务端不同形态需求。
- **配置驱动**：所有模态相关路径、模型、阈值均通过配置决定，避免硬编码。
- **任务编排统一化**：训练、数据集下载、批量导入等任务统一由 Task Orchestrator 管理，实现跨模态复用。

### 2.2 架构概览

```
+------------------------------------------------------------------+
|                          Interface Layer                          |
|  ├─ GUI (PyQt/Web)                                                |
|  └─ REST API / CLI                                                |
+------------------------------------------------------------------+
|                        Biometric Service Layer                    |
|  ├─ BiometricServiceRegistry                                      |
|  ├─ BiometricService (modality-agnostic facade)                   |
|  └─ {Face|Voice|Fingerprint}Service (适配器)                      |
+------------------------------------------------------------------+
|                        Core Capability Layer                      |
|  ├─ BiometricVerifier (抽象)                                      |
|  │   └─ {Face|Voice|Fingerprint}Verifier                          |
|  ├─ BiometricDatasetManager + Preprocessing Pipelines             |
|  ├─ ModelManager (统一模型生命周期)                                 |
|  └─ EmbeddingStore / Feature Index                                |
+------------------------------------------------------------------+
|                     Data & Model Infrastructure                   |
|  ├─ Raw/Processed Data Repositories per modality                  |
|  ├─ Model Zoo (weights, configs, metrics)                         |
|  └─ Metadata DB (users, profiles, audit logs)                     |
+------------------------------------------------------------------+
|                        Platform Foundation                        |
|  ├─ Config, Logging, Security, Monitoring                         |
|  ├─ Task Orchestrator (训练/评估/下载统一调度)                    |
|  └─ Shared Utils (IO, transforms, hardware abstraction)           |
+------------------------------------------------------------------+
```

### 2.3 关键流程抽象
- **录入流程**：`Interface -> BiometricServiceFacade.enroll(modality, payload)` → `ServiceRegistry` 定位模态服务 → 具体 `ModalityService` 调用 `Verifier` 生成 embedding，交由 `DatasetManager`、`EmbeddingStore` 存储。
- **验证流程**：统一的 `verify(modality, payload)` 接口，内部根据模态选择模型、阈值和后处理策略，返回标准化匹配结果。
- **模型训练**：`Task Orchestrator` 读取配置（包含模态、模型、数据集），调用 `TrainingPipelineFactory` 产出具体训练流程；训练完成后通过 `ModelManager` 注册版本并触发热更新。
- **配置与策略**：统一的 `biometric.yaml`，以 `modality` 为命名空间，描述模型路径、阈值、预处理参数；支持环境覆盖。

### 2.4 目录与包规划（初稿）
- `biometric_platform/`
  - `core/`：抽象基类、注册表、task orchestrator、配置管理。
  - `modalities/face|voice|fingerprint/`：各模态实现（verifier、service、dataset、training）。
  - `interfaces/`：API、GUI、CLI。
  - `infrastructure/`：模型管理、存储、数据库、日志、安全。
  - `scripts/`：跨模态公用脚本（下载、训练、评估）。
- `configs/`：`biometric.yaml`、环境差异配置。
- `datasets/`、`models/`、`storage/`：按模态分命名空间。

## 3. 人脸子系统高层架构

```
+--------------------------------------------------------------+
|                           GUI 层                              |
|  └─ Face Enrollment UI / Verification UI                     |
+--------------------------------------------------------------+
|                       API & 服务层                            |
|  ├─ REST API (FastAPI)                                       |
|  └─ FaceService (业务编排)                                    |
+--------------------------------------------------------------+
|                       核心能力层                              |
|  ├─ FaceVerifier (推理)                                       |
|  ├─ FaceDatasetManager (数据管理)                             |
|  ├─ ModelManager (模型加载与版本控制)                         |
|  └─ Task Orchestrator (训练/评估/下载任务)                    |
+--------------------------------------------------------------+
|                        数据与模型层                           |
|  ├─ Raw Data Storage (原始图像)                                |
|  ├─ Processed Data/Embeddings                                |
|  └─ Model Zoo (训练模型、权重、配置)                          |
+--------------------------------------------------------------+
|                        基础支撑层                             |
|  ├─ 配置管理 (YAML/JSON)                                      |
|  ├─ 日志与监控                                                |
|  ├─ 公共工具库 (IO、图像处理等)                               |
|  └─ 安全组件 (加密、权限控制)                                 |
+--------------------------------------------------------------+
```

## 4. 模块设计

### 4.1 GUI 层
- **Face Enrollment UI**：提供摄像头实时预览、拍照、图像质量提示、录入确认。扩展位：声纹录音、指纹扫描按钮预留。
- **Face Verification UI**：展示实时摄像头画面，调用验证接口返回匹配结果（置信度、匹配用户信息）。
- **技术选型**：桌面（PyQt5/Tkinter）或 Web（Electron + React / Web 前端 + 后端）。第一期建议 PyQt5，整合容易。
- **交互**：通过 API 层提交录入/验证请求，或直接调用 FaceService（同进程部署时）。

### 4.2 API & 服务层
- **REST API（FastAPI）**  
  - `POST /biometric/face/enroll`：录入人脸数据。支持上传图像或引用 GUI capture。
  - `POST /biometric/face/verify`：提交实时帧/图像，返回匹配结果。
  - `GET /biometric/face/{user_id}`：查询用户信息与 embedding 状态。
  - `DELETE /biometric/face/{user_id}`：删除相关数据、模型特征。
  - `GET /biometric/face/health`：健康检查接口。
  - 统一返回结构：`{ status, data, error }`。
- **FaceService（业务编排）**  
  - 封装录入/验证流程，协调数据管理、模型推理、日志记录。
  - 校验输入、统一错误处理、标准化响应。

### 4.3 核心能力层
- **FaceVerifier**  
  - 责任：加载人脸检测模型与识别模型；提供增量录入、embedding 生成、相似度计算、匹配排序。
  - 接口：
    - `generate_embedding(image) -> embedding`
    - `match(embedding, top_k=5) -> List[MatchResult]`
    - `enroll(user_id, images)`
    - `delete(user_id)`
  - 可插拔检测器（MTCNN/RetinaFace）与识别器（FaceNet/ArcFace）。使用配置选择。
- **FaceDatasetManager**  
  - 管理原始图像、预处理数据集、训练/验证划分。
  - 负责数据清洗、增强、命名规范、元数据记录。
- **ModelManager**  
  - 负责模型版本管理、加载、热更新；记录模型指标、训练配置。
  - 支持从本地/远程仓库加载模型。
- **Task Orchestrator**  
  - 抽象长耗时任务：数据集下载、模型训练、评估、批量导入等。
  - 支持 CLI 调度或后台任务队列（Celery/RQ）。

### 4.4 数据与模型层
- **数据结构**  
  - `BiometricProfile`：`{id, modality, raw_data_paths, embedding_path, metadata}`。
  - `EmbeddingStore`：向量数据库（FAISS/Annoy）或简单的本地存储（初期 sqlite + 二进制向量）。
- **存储规划**  
  - 原始图像：`datasets/raw/face/{user_id}/{timestamp}.jpg`
  - 清洗数据：`datasets/processed/...`
  - Embedding：`storage/embeddings/face/{user_id}.npy`
  - 元数据：`storage/db.sqlite` 或 MySQL/PostgreSQL。
- **模型目录**  
  - `models/face/{model_name}/{version}/weights.pt`
  - 保存 `config.yaml`、`metrics.json`、`labels.json` 等。

### 4.5 基础支撑层
- **配置管理**：默认使用 YAML + Pydantic（或 dataclasses）映射配置。区分 `dev/test/prod` 环境。
- **日志与监控**：使用 `loguru`/`logging`；记录关键事件（录入、验证、训练）；提供 API 请求日志；可扩展 metrics（Prometheus）。
- **安全与权限**：API 需要 Token/Key；数据加密存储；关键操作审计日志。
- **公共工具**：图像增强、摄像头采集、文件 IO、异常定义。

## 5. 数据流程

### 5.1 人脸录入
1. GUI 捕获图像（多帧）。
2. 调用 API `POST /biometric/face/enroll`。
3. API 通过 FaceService 校验 → FaceVerifier 生成 embedding。
4. FaceDatasetManager 写入原始图像与元数据，EmbeddingStore 更新。
5. 返回成功响应，包含 user_id、embedding 信息摘要。

### 5.2 人脸验证
1. GUI/外部调用 `POST /biometric/face/verify`。
2. API 将图像传递给 FaceVerifier → 生成人脸 embedding。
3. 在 EmbeddingStore 中执行相似度检索。
4. 返回匹配列表（user_id, score, threshold 判断）。

### 5.3 模型训练
1. Task Orchestrator 调用数据集下载或读取现有数据。
2. FaceDatasetManager 完成数据预处理（裁剪、对齐、增强）。
3. 训练脚本（PyTorch）读取配置，执行训练/验证。
4. 输出模型权重、指标、日志；ModelManager 记录新版本。
5. 部署时更新 FaceVerifier 所用模型。

## 6. 关键技术选型
- **语言框架**：Python 3.10+。
- **NN 框架**：PyTorch，结合 torchvision / timm。
- **检测模型**：MTCNN（简单）、RetinaFace（精度高）。可使用 `facenet-pytorch` 或自定义实现。
- **识别模型**：ArcFace (ResNet100)、FaceNet (InceptionResNet)、InsightFace。
- **向量检索**：初期用余弦相似度 + sqlite 存储；扩展可接 FAISS。
- **GUI**：PyQt5（跨平台）；后续视需求可切换 Web。
- **API**：FastAPI + Uvicorn。
- **数据库**：SQLite（开发阶段），后续可切换 PostgreSQL。
- **任务调度**：初期 CLI + cron，后续可接 Celery。

## 7. 扩展性考虑
- 接口和类命名保持模态无关：例如 `BiometricService`, `BiometricVerifier`，当前实现 `Face` 子类。
- 配置文件中加入 `modality` 字段，控制加载不同模型、数据路径。
- 数据库和存储结构适配不同模态，通过命名空间区分。
- 训练脚本设计参数化流程，只需为新模态提供数据管道与模型定义。
- API 路由可采用 `/biometric/{modality}/...` 通用前缀。

## 8. 安全与隐私
- 数据加密存储、传输采用 HTTPS/TLS。
- 敏感操作需要认证授权（API Key/JWT）。
- 提供数据脱敏与删除能力，满足隐私法规（GDPR 等）。
- 记录合规日志：用户同意、录入时间、用途说明。

## 9. 开发迭代计划
1. **Sprint 1**：项目骨架、配置、日志、基本目录结构；FaceVerifier 初版（调用预训练模型）、简单 CLI 演示。
2. **Sprint 2**：GUI 录入、API 基本流程打通；embedding 存储；简单 sqlite 数据库。
3. **Sprint 3**：数据集下载/预处理脚本；模型训练流水线；模型版本管理。
4. **Sprint 4**：完善验证策略、批量导入、健康检查、监控；文档与测试。
5. **Sprint 5**：为声纹/指纹扩展准备接口与补充文档。

## 10. 测试策略
- 单元测试：FaceVerifier 功能、数据管理、API 响应。
- 集成测试：端到端录入 → 验证流程。
- 性能测试：验证接口在不同并发下响应时间。
- 数据质量检查：录入图像质量、数据集完整性。

## 11. 文档与工具
- `README.md`：项目说明、运行步骤。
- `docs/`：设计文档（本文件）、API 说明、模型训练指南。
- `scripts/`：常用脚本（下载、预处理、训练、评估）。
- `notebooks/`：实验记录与探索性分析（可选）。

## 12. 未决事项
- GUI 技术最终选择与交互细节。
- 模型选型是自训还是直接使用开源预训练并微调。
- Embedding 存储是否引入向量数据库。
- 部署拓扑：单机应用 vs 微服务化。
- 安全合规策略细节（需结合业务场景制定）。

---

该设计文档将作为第一阶段开发基线，后续在实现过程中持续迭代与补充。


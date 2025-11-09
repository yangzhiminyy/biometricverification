# 实施计划（阶段一：人脸识别骨架落地）

## 1. 目标
- 在现有架构基础上，完成可运行的人脸识别最小闭环（录入/验证伪实现 + API）。
- 为后续模型接入、数据管理、GUI 搭建打下基础。

## 2. 任务分解
1. **依赖环境准备**
   - 使用 `python -m venv .venv` 创建虚拟环境，执行 `pip install -r requirements.txt`。
   - 确认 PyTorch 与相关依赖可用，必要时配置 CUDA/cuDNN。

2. **配置与日志**
   - 根据运行环境调整 `configs/biometric.yaml`（阈值、存储路径）。
   - 接入 logging 配置（loguru 或标准 logging），在核心服务中埋点。

3. **FaceVerifier 实现**
   - 集成检测模型（MTCNN/RetinaFace），完成人脸对齐。
   - 接入识别模型（ArcFace/FaceNet），产出 embedding。
   - 设计 embedding 存储结构（先用本地 numpy + sqlite，后续接 FAISS）。
   - 实现 `match` 方法的相似度计算与阈值判定。
   - 已创建 `biometric_platform/models/face/embedding.py` 作为自研/占位模型骨架，可依据此替换为预训练或自训模型。

4. **数据管理模块**
   - 实现 `DatasetManager` 的人脸版本：保存原始图片、元数据、维护索引。
   - 设计 `storage/` 目录结构、文件命名规范。
   - 规划批量导入和清理脚本的接口。

5. **API 与自测**
   - 扩展 FastAPI 路由，完善参数校验（Pydantic 模型）。
   - 运行 `uvicorn biometric_platform.interfaces.api.app:app --reload` 验证接口。
   - 编写简单的 `scripts/smoke_test.py` 调用 enroll/verify，确认流程通顺。

6. **测试与文档**
   - 编写单元测试（pytest）：验证服务注册表、配置加载、FaceService 接口。
   - 更新 `README.md` 的运行说明，记录常见问题（依赖安装、缺失模型）。
   - 在 `docs/` 中补充模型训练计划、数据集下载说明。

## 3. 里程碑
- **Milestone 1**：API 可启动，使用占位 embedding 成功执行录入/验证。
- **Milestone 2**：接入真实模型，支持基础识别测试，完成端到端 Demo。
- **Milestone 3**：完善数据与模型管理（版本、指标），准备扩展声纹/指纹。

## 4. 风险与缓解
- **依赖安装失败**：提前验证机器环境，必要时分离 GPU/CPU 依赖版本。
- **模型推理性能**：在实现阶段引入异步或缓存机制，预留 GPU 加速接口。
- **数据安全**：在存储模块中预留加密/权限检查钩子，配合后续安全策略。

## 5. 后续工作展望
- **真实模型集成**：选择 MTCNN/RetinaFace 检测器与 ArcFace/FaceNet 识别器，完善推理管线与批处理加速。
- **向量检索升级**：由内存存储迁移至 FAISS/Annoy 或数据库支持，并引入增量更新策略。
- **数据流水线强化**：构建数据增强、对齐、质量控制步骤；提供 CLI/GUI 批量导入工具。
- **硬件与性能优化**：支持 GPU 推理、批量处理及异步任务，评估内存与延迟指标。
- **安全合规扩展**：引入加密、访问控制、审计日志及数据生命周期管理。

---

完成上述任务后，将具备稳定的骨架，可继续投入模型训练与多模态扩展。


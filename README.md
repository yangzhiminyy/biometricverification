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
1. 创建虚拟环境并安装依赖（待发布 `requirements.txt` / `pyproject.toml`）。
2. 配置 `configs/biometric.yaml` 指定当前生物模态、模型路径等。
3. 运行接口层（FastAPI/GUI）进行人脸录入与验证。
4. 使用 `scripts/` 下工具进行数据集下载、模型训练、评估。

## 设计文档
- `docs/face_module_design.md`：人脸识别子系统设计与跨模态总体框架。

## 开发计划
- 阶段一：搭建核心骨架（配置、抽象类、注册表、基础 API）。
- 阶段二：实现人脸模块（录入、验证、模型加载、数据管理）。
- 阶段三：完善训练与数据集流程，准备声纹/指纹扩展。

更多细节与背景请参考设计文档并与团队讨论。欢迎贡献改进建议！


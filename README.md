# Parser Service - RAG Infrastructure

轻量级 RAG 基础设施服务，基于 RAGFlow 核心代码构建，提供文档解析、分块、向量化、检索能力。

## 核心能力

### 文档解析 (来自 RAGFlow deepdoc)
- PDF（含 OCR、布局分析、表格识别）
- DOCX、PPTX、Excel/CSV
- HTML、Markdown
- JSON、JSONL、TXT
- EPUB 电子书

### 分块策略 (来自 RAGFlow rag/app)
- Naive - 通用分块（支持 15+ 格式）
- Book - 长文档分块
- Table - 表格数据分块
- QA - 问答对提取
- Heading - 标题层级分块

### 向量检索
- 支持 Elasticsearch、Infinity
- 多种 Embedding 模型（OpenAI 协议兼容）
- 混合检索（向量 + 全文）

## 快速开始

### Docker 部署（推荐）

```bash
docker-compose up -d
```

服务启动后访问 `http://localhost:8000/docs` 查看接口文档。

### 本地开发

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 启动服务
uvicorn app.main:create_app --host 0.0.0.0 --port 8000 --factory --reload
```

## API 接口

核心 RAG 功能接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/datasets | 创建知识库 |
| POST | /api/v1/documents | 上传文档 |
| GET | /api/v1/documents/{doc_id} | 获取文档状态 |
| POST | /api/v1/datasets/{kb_id}/search | 检索 |

## 项目结构

```
app/
├── rag/              # RAG 核心引擎（分块、检索、嵌入）
├── deepdoc/         # 文档解析（PDF/DOCX/PPT 等）
├── common/          # 共享工具（doc_store、settings）
├── api/             # REST API 服务
├── conf/            # 配置文件
├── embedding/       # Embedding 抽象
└── vectorstore/     # 向量存储
```

## 技术栈

- **Web 框架**: FastAPI
- **数据库**: MySQL + Redis
- **向量存储**: Elasticsearch / Infinity
- **对象存储**: MinIO
- **LLM**: 支持 OpenAI 协议（云端/本地 vLLM）

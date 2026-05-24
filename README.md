# Parser Service - RAGFlow Core

基于 RAGFlow 核心代码的轻量级 RAG 基础设施服务，提供文档解析、分块、向量化、检索能力。

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
- Paper - 论文分块
- Resume - 简历解析

### 向量检索
- Elasticsearch（主要）
- Infinity（可选）
- 多种 Embedding 模型（OpenAI 协议兼容）
- 混合检索（向量 + 全文）

## 快速开始

### 1. 启动基础设施

```bash
# 启动 Docker 基础设施（MySQL, Redis, Elasticsearch, MinIO）
./start.sh up
```

服务启动后可访问：
- **Elasticsearch**: http://localhost:9200
- **MinIO Console**: http://localhost:9001 (用户名/密码: rag_flow / infini_rag_flow)

### 2. 启动 Python 服务

```bash
# 启动 Parser Service
./start.sh python
```

服务启动后访问 http://localhost:9380

### 3. 常用命令

```bash
./start.sh up         # 启动 Docker 基础设施
./start.sh python     # 启动 Python 服务
./start.sh down       # 停止所有服务
./start.sh logs       # 查看日志
./start.sh status     # 查看服务状态
./start.sh init-db    # 初始化数据库
```

## 环境配置

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

主要配置项：

```bash
# Embedding 模型（支持 OpenAI 协议兼容的服务）
EMBEDDING_BASE_URL=http://localhost:6380  # vLLM 本地服务
EMBEDDING_API_KEY=your-api-key
EMBEDDING_MODEL=bge-m3

# 或使用云端服务
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_MODEL=text-embedding-3-small
```

## API 接口

核心 RAG 功能接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/datasets | 创建知识库 |
| POST | /api/v1/documents | 上传文档 |
| GET | /api/v1/documents/{doc_id} | 获取文档状态 |
| POST | /api/v1/datasets/{kb_id}/search | 检索 |
| POST | /api/v1/chunks | 分块管理 |

访问 http://localhost:9380/docs 查看完整 API 文档。

## 项目结构

```
parser-service/
├── app/
│   ├── rag/              # RAG 核心引擎（分块、检索、嵌入）
│   ├── deepdoc/          # 文档解析（PDF/DOCX/PPT 等）
│   ├── common/           # 共享工具（doc_store、settings）
│   └── api/
│       ├── apps/         # Flask API 应用
│       │   ├── restful_apis/  # RESTful API 端点
│       │   └── services/      # API 服务层
│       └── db/           # 数据库模型和服务
├── conf/                 # 配置文件
├── main.py               # 服务入口点
├── requirements.txt      # Python 依赖
├── docker-compose.yml    # Docker 基础设施
├── start.sh              # 启动脚本
└── .env.example          # 环境变量示例
```

## 技术栈

- **Web 框架**: Flask
- **数据库**: MySQL 8.0
- **缓存**: Redis 7
- **向量存储**: Elasticsearch 8.17
- **对象存储**: MinIO
- **LLM**: 支持 OpenAI 协议（vLLM/云端）

## 使用 SDK 集成

```python
from ragflow import RAGFlow

# 初始化客户端
rag = RAGFlow(
    api_key="your-api-key",
    base_url="http://localhost:9380"
)

# 创建知识库
kb = rag.create_dataset(name="my_kb")

# 上传文档
kb.upload_document("document.pdf")

# 检索
results = kb.search("query", top_k=5)
```

## LangChain 集成

```python
from langchain_core.retrievers import BaseRetriever
from ragflow import RAGFlow

class RAGFlowRetriever(BaseRetriever):
    def __init__(self, kb_id, api_key, base_url="http://localhost:9380"):
        self.client = RAGFlow(api_key=api_key, base_url=base_url)
        self.kb_id = kb_id

    def _get_relevant_documents(self, query):
        return self.client.search(self.kb_id, query, top_k=5)

# 使用
retriever = RAGFlowRetriever(kb_id="xxx", api_key="xxx")
```

## 开发说明

### 本地开发模式

```bash
# 1. 启动基础设施
./start.sh up

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
export EMBEDDING_BASE_URL=http://localhost:6380
export EMBEDDING_API_KEY=your-key

# 4. 启动服务（调试模式）
python main.py --debug
```

### 添加新的解析器

在 `app/deepdoc/parser/` 下添加新的解析器类，继承自 `BaseParser`。

### 添加新的分块策略

在 `app/rag/app/` 下添加新的分块类，继承自 `BaseApplication`。

## 许可证

基于 RAGFlow Apache 2.0 许可证。

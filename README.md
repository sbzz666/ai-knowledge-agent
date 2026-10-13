# 知识库问答 Agent（Knowledge Agent）

面向企业资料与个人文档的可解释 RAG 应用。用户上传 PDF、DOCX、TXT 或 Markdown 文档后，系统完成解析、切分、索引、混合检索，并生成带原文引用的回答。

> 当前阶段：工程准备与可部署骨架。业务功能将在需求确认后分阶段实现。

## 为什么适合作为简历项目

- 不是简单套壳聊天：包含文档处理、向量检索、关键词检索、重排、引用校验和离线评测。
- 有清晰工程边界：前端、API、检索层、模型层、数据库与评测模块相互独立。
- 可演示也可部署：本地支持 Docker Compose，云端可以拆成 Web、API 和 PostgreSQL 服务。
- 可量化：计划记录 Recall@K、MRR、答案忠实度、引用命中率、延迟与调用成本。

## 拟实现能力

1. PDF、DOCX、TXT、Markdown 文档上传与安全校验。
2. 文档解析、结构化切分、元数据与版本管理。
3. MVP 使用 SQLite 与本地混合检索零配置运行；生产版迁移到 PostgreSQL 全文检索 + pgvector。
4. 可选重排器，提高 Top-K 片段相关性。
5. 带页码、文件名和原文片段的回答；证据不足时明确拒答。
6. 多轮会话、知识库隔离、流式回答与反馈收集。
7. RAG 离线评测、接口测试、日志与基本调用限流。

## 技术栈

| 层级 | 方案 | 选择原因 |
|---|---|---|
| Web 演示 | Streamlit | 开发快，适合公开作品演示 |
| 后端 API | FastAPI + Pydantic | 类型清晰，自动生成 OpenAPI，方便独立部署 |
| Agent 编排 | LangGraph（需要多步工作流时启用） | 适合可恢复、有状态的检索与回答流程 |
| 数据访问 | SQLAlchemy 2 + Alembic | 数据模型和迁移可维护 |
| 数据库 | SQLite（MVP）/ PostgreSQL + pgvector（生产） | 本地零配置，部署时可平滑升级 |
| 文档解析 | PyMuPDF + python-docx | 覆盖常用简历和企业文档格式 |
| 模型接入 | OpenAI-compatible SDK | 可切换 DeepSeek、OpenAI 或其他兼容服务 |
| 测试与质量 | pytest + Ruff + mypy | 单测、格式、静态检查 |
| 部署 | Docker / Docker Compose | 本地与云端环境一致，便于迁移 |
| CI | GitHub Actions | 自动执行测试、检查和镜像构建 |

## 建议部署结构

```text
Browser
   │
   ▼
Streamlit Web ─────► FastAPI
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     PostgreSQL     LLM API     Object Storage
     + pgvector                 （后续按需）
```

第一版可将 Web 与 API 放在同一容器以降低部署成本；作品完善后再拆分服务。

## 目录规划

```text
knowledge-agent/
├─ app/
│  ├─ api/             # FastAPI 路由
│  ├─ core/            # 配置、安全、日志
│  ├─ ingestion/       # 解析、切分、入库
│  ├─ retrieval/       # 关键词、向量、融合、重排
│  ├─ generation/      # Prompt、模型调用、引用校验
│  └─ main.py          # API 入口
├─ data/               # 仅保留虚构样例；私有资料禁止提交
├─ docs/               # 架构、部署、评测与项目说明
├─ tests/
├─ .env.example
├─ compose.yaml
├─ Dockerfile
└─ pyproject.toml
```

## 当前可运行内容

目前已提供可用的文档上传、混合检索、离线引用回答、DeepSeek 增强回答、知识库管理、API 和 Web 界面：

```powershell
cd "D:\codex项目\agent项目\knowledge-agent"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

打开 `http://localhost:8501`。API 可另行运行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

API 文档位于 `http://127.0.0.1:8000/docs`。

## 开发阶段

- P0：项目骨架、健康检查、容器与测试（已完成）
- P1：文档解析、切分、SQLite 持久化（已完成）
- P2：本地混合检索、引用式问答（已完成）
- P3：Streamlit 界面、API、知识库管理（已完成）
- P4：真实 Embedding、pgvector、重排器与系统化评测（下一阶段）

## 安全原则

- `.env`、API Key、真实简历、私有文档、数据库和上传文件不得提交到 Git。
- 上传文件需要限制类型、大小、页数和解压体积。
- 模型回答必须保留来源引用；没有足够证据时不编造答案。

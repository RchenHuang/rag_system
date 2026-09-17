# rag_system — V0

RAG 系统的 V0：建立统一的 ingestion 基础架构。

数据流：

```
.md 文件 → MarkdownParser → Document → SimpleChunker → list[Chunk]
```

## 结构

- `src/rag_system/models` — Document / Block / Chunk 数据模型
- `src/rag_system/ingestion/parsers` — Parser 接口 + MarkdownParser
- `src/rag_system/ingestion/chunkers` — Chunker 接口 + SimpleChunker
- `src/rag_system/pipeline.py` — IngestionPipeline 编排

## 安装与测试

```bash
uv venv .venv --python 3.12
uv pip install -e . pytest
uv run pytest
```

## 示例

```bash
uv run python examples/run_ingestion.py
```

V0 明确不包含：Embedding / 向量库 / 检索 / LLM / Ragas。

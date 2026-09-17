# RAG System — V1 Architecture Spec

## 1. V1 Goal

V1 的目标是在 V0 的基础上，把 `Chunk` 真正变成可以被机器索引、并为后续检索使用的数据。

V0：

```text
Raw Markdown
    ↓
MarkdownParser
    ↓
Document
    ↓
Block[]
    ↓
SimpleChunker
    ↓
Chunk[]
```

V1：

```text
Raw Markdown
    ↓
MarkdownParser
    ↓
Document
    ↓
Block[]
    ↓
TokenChunker
    ↓
Chunk[]
    ↓
Embedder
    ↓
Vector[]
    ↓
Indexer
    ↓
IndexRecord[]
    ↓
IndexStore
    ↓
Local Persistent Index
```

V1 不实现 Query、Retriever、LLM Answer。

V1 只负责：

> 把知识可靠地切成适合模型处理的 Chunk，并转换成向量后持久化。

---

## 2. V1 Core Concepts

V1 新增四个核心概念：

```text
Tokenizer
TokenChunker
Embedder
Indexer / IndexStore
```

---

## 3. SimpleChunker vs TokenChunker

V0 的 `SimpleChunker`：

```text
max_chars = 1000
```

使用字符数量控制 Chunk 大小。

但模型真正处理的是 token：

```text
字符数 ≠ token 数
```

因此 V1 新增：

```text
TokenChunker
```

建议配置：

```python
TokenChunker(
    tokenizer=...,
    max_tokens=512,
    overlap_tokens=50,
)
```

### TokenChunker Responsibilities

TokenChunker 必须：

1. 使用 Tokenizer 计算文本 token 数量
2. 尽量保持完整 Block
3. 在加入下一个 Block 会超过 `max_tokens` 时停止追加
4. 对单个超长 Block 允许继续按 token 切分
5. 支持 overlap
6. 保持 `document_id`
7. 保持 `block_ids`
8. 保持 Chunk 顺序

普通 Block 聚合原则：

```text
Block A = 120 tokens
Block B = 200 tokens
Block C = 260 tokens
max_tokens = 512
```

则：

```text
Chunk 0 = A + B
Chunk 1 = C
```

优先保持 Block 边界。

---

## 4. Oversized Block

如果单个 Block 本身已经超过 `max_tokens`：

```text
Block A = 1300 tokens
max_tokens = 512
```

允许按 token 拆分：

```text
Part 1: token 0 - 511
Part 2: token 462 - 973
Part 3: token 924 - ...
```

如果：

```text
overlap_tokens = 50
```

相邻部分保留约 50 token 重复。

Overlap 的作用：

> 避免一个完整概念、句子或事实刚好被切在两个 Chunk 边界。

---

## 5. Tokenizer Interface

定义：

```python
class Tokenizer(Protocol):

    def encode(self, text: str) -> list[int]:
        ...

    def decode(self, tokens: list[int]) -> str:
        ...
```

V1 第一版实现：

```text
TiktokenTokenizer
```

依赖关系：

```text
TokenChunker
     ↓
Tokenizer Interface
     ↓
TiktokenTokenizer
```

未来可以替换其他 tokenizer，而不修改 TokenChunker 主要逻辑。

---

## 6. Chunk Model

V0 的 Chunk 保持纯净：

```python
@dataclass
class Chunk:
    id: str
    document_id: str
    content: str
    block_ids: list[str]
    order: int
    metadata: dict[str, Any]
```

V1 不直接增加：

```text
embedding
embedding_model
similarity_score
```

原因：

```text
Chunk
= Knowledge Model

Embedding
= Index Representation
```

未来一个 Chunk 可能拥有多种索引表示，所以不要把所有索引信息塞进 Chunk。

---

## 7. Embedder

Embedder 的职责：

> 把文本转换成高维向量。

例如：

```text
"Short-term memory stores tool results."
```

经过 Embedding Model：

```text
[0.031, -0.772, 0.194, ...]
```

这个数组就是 vector。

语义相近的文本，通常在向量空间中也更接近。

---

## 8. Embedder Interface

定义：

```python
class Embedder(Protocol):

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...
```

必须支持 batch：

```text
Chunk[]
    ↓
extract content
    ↓
list[str]
    ↓
Embedder
    ↓
list[list[float]]
```

不要让外层对每个 Chunk 单独打一遍 API。

---

## 9. FakeEmbedder

V1 必须提供：

```text
FakeEmbedder
```

只用于测试。

要求：

1. 不访问网络
2. 不需要 API Key
3. 输出稳定
4. 固定 vector dimension
5. 输入 N 个文本输出 N 个 vectors

FakeEmbedder 不追求语义质量，只验证系统数据流。

---

## 10. Real Embedder

V1 实现：

```text
OpenAICompatibleEmbedder
```

配置：

```text
base_url
api_key
model
```

真实数据流：

```text
texts
    ↓
Embedding API
    ↓
Embedding Model
    ↓
vectors
```

配置必须来自环境变量或配置对象，例如：

```env
EMBEDDING_BASE_URL=...
EMBEDDING_API_KEY=...
EMBEDDING_MODEL=...
```

禁止把 API Key 写进源码。

`.env` 必须进入 `.gitignore`。

---

## 11. IndexRecord

新增：

```python
@dataclass
class IndexRecord:
    id: str
    chunk_id: str
    document_id: str
    content: str
    vector: list[float]
    metadata: dict[str, Any]
```

关系：

```text
Chunk
    ↓
Embedding
    ↓
IndexRecord
```

IndexRecord 是真正交给索引存储系统的数据模型。

V1 可以让：

```text
id == chunk_id
```

不要设计复杂 ID strategy。

---

## 12. Indexer

Indexer 负责 orchestration：

```text
Chunk[]
    ↓
extract chunk.content
    ↓
Embedder.embed_documents()
    ↓
Vector[]
    ↓
zip(chunks, vectors)
    ↓
IndexRecord[]
    ↓
IndexStore.upsert()
```

建议：

```python
class Indexer:

    def __init__(
        self,
        embedder: Embedder,
        store: IndexStore,
    ):
        ...

    def index(
        self,
        chunks: list[Chunk],
    ) -> list[IndexRecord]:
        ...
```

Indexer 不负责：

```text
Embedding 模型内部怎么计算
JSONL 怎么写盘
Vector Search
Query
```

它只负责编排。

---

## 13. IndexStore Interface

定义：

```python
class IndexStore(Protocol):

    def upsert(
        self,
        records: list[IndexRecord],
    ) -> None:
        ...
```

未来可以实现：

```text
JsonlIndexStore
ElasticsearchIndexStore
QdrantIndexStore
```

所有实现都遵循：

```text
IndexRecord[] → persist
```

---

## 14. V1 Local Store

V1 不使用 Elasticsearch。

第一版实现：

```text
JsonlIndexStore
```

输出：

```text
data/index.jsonl
```

示例：

```json
{"chunk_id":"c1","content":"Agent Memory...","vector":[0.1,0.3]}
{"chunk_id":"c2","content":"Short-term Memory...","vector":[0.5,0.2]}
```

选择 JSONL 是为了：

```text
简单
可直接查看
容易调试
容易测试
无 Docker
无数据库依赖
```

V1 先理解：

```text
Chunk
→ Vector
→ IndexRecord
→ Store
```

---

## 15. Pipeline Separation

V0：

```text
IngestionPipeline

Source
    ↓
Parser
    ↓
Document
    ↓
Chunker
    ↓
Chunk[]
```

V1 增加：

```text
IndexingPipeline

Chunk[]
    ↓
Indexer
    ↓
IndexStore
```

整体：

```text
Source
    ↓
IngestionPipeline
    ↓
Chunk[]
    ↓
IndexingPipeline
    ↓
IndexRecord[]
    ↓
IndexStore
```

不要创建一个负责所有事情的巨大 Pipeline。

---

## 16. Suggested Repository Structure

```text
src/rag_system/

├── models/
│   ├── document.py
│   ├── chunk.py
│   └── index.py
│
├── ingestion/
│   ├── parsers/
│   │   ├── base.py
│   │   └── markdown.py
│   │
│   ├── chunkers/
│   │   ├── base.py
│   │   ├── simple.py
│   │   └── token.py
│   │
│   └── tokenizers/
│       ├── base.py
│       └── tiktoken.py
│
├── embeddings/
│   ├── __init__.py
│   ├── base.py
│   ├── fake.py
│   └── openai_compatible.py
│
├── indexing/
│   ├── __init__.py
│   ├── indexer.py
│   └── stores/
│       ├── __init__.py
│       ├── base.py
│       └── jsonl.py
│
├── pipelines/
│   ├── __init__.py
│   ├── ingestion.py
│   └── indexing.py
│
└── config.py
```

---

## 17. Tests

### TokenChunker

必须覆盖：

```text
小于 max_tokens
→ 一个 Chunk

多个 Block 超过 max_tokens
→ 正确分 Chunk

单个超长 Block
→ 能按 token 拆开

overlap_tokens > 0
→ 相邻部分存在预期 overlap

document_id
→ 保持一致

block_ids
→ 保持来源可追溯

Chunk order
→ 连续正确
```

### FakeEmbedder

测试：

```text
输入 N 个文本
→ 输出 N 个 vectors

所有 vector dimension
→ 一致

相同输入
→ 输出稳定
```

### Indexer

输入：

```text
3 Chunks
```

经过 FakeEmbedder 后必须得到：

```text
3 IndexRecords
```

并保证字段与原 Chunk 正确对应。

### JsonlIndexStore

测试：

```text
upsert(records)
    ↓
文件存在
    ↓
行数正确
    ↓
内容可以重新读取
```

### End-to-End

完整 V1 流程：

```text
sample.md
    ↓
MarkdownParser
    ↓
Document
    ↓
TokenChunker
    ↓
Chunk[]
    ↓
FakeEmbedder
    ↓
Indexer
    ↓
JsonlIndexStore
    ↓
temporary index.jsonl
```

pytest 不得依赖真实外部 API。

---

## 18. Example

新增：

```text
examples/build_index.py
```

支持：

```bash
python examples/build_index.py tests/fixtures/sample.md
```

运行后输出类似：

```text
Document parsed
Chunks created: 3
Vectors generated: 3
Index records written: 3
Index path: data/index.jsonl
```

不要重复 parse 同一个文件。

---

## 19. Explicit Non-Goals

V1 禁止实现：

```text
Query API
Retriever
Cosine Similarity Search
Vector Database
Elasticsearch
BM25
Hybrid Search
RRF
Reranker
LLM Answer
Ragas
Transformer
Question Generation
Keyword Extraction
Summary Generation
Metadata Extraction
Parent-Child Chunking
Semantic Chunking
GraphRAG
Agentic RAG
FastAPI
Redis
Task Queue
```

不要提前实现 V2+。

---

## 20. V1 Acceptance Criteria

V1 完成后必须满足：

```text
sample.md
    ↓
MarkdownParser
    ↓
Document
    ↓
TokenChunker
    ↓
Chunk[]
    ↓
Embedder
    ↓
Vector[]
    ↓
Indexer
    ↓
IndexRecord[]
    ↓
JsonlIndexStore
    ↓
index.jsonl
```

并满足：

- V0 测试继续通过
- V1 新测试全部通过
- FakeEmbedder 测试完全离线
- API Key 不进入 Git
- `.env` 被忽略
- Chunk 不直接保存 embedding
- TokenChunker 满足原有 Chunker Protocol
- Indexer 不依赖具体 Embedder 实现
- Indexer 不依赖具体 IndexStore 实现
- 不实现任何 V2+ 功能

---

## 21. Instructions for Coding Agent

Before implementation:

1. Inspect current V0 repository.
2. Preserve V0 behavior and tests.
3. Use this V1 specification as source of truth.
4. Create a new feature branch before implementation.

Suggested branch:

```text
feat/v1-indexing
```

Implementation requirements:

1. Implement only V1.
2. Keep interfaces minimal.
3. Do not introduce Elasticsearch or vector databases.
4. Do not introduce retrieval.
5. Do not hardcode secrets.
6. Add unit tests for every new component.
7. Add one V1 end-to-end test.
8. Run the full test suite.
9. Fix all failures before completion.

When finished, report:

```text
1. Architecture implemented
2. Files created
3. Files modified
4. V0 compatibility changes
5. Main design decisions
6. Tests executed and results
7. Any deviation from SPEC_V1.md
8. Anything that should be considered before V2
```

Do not begin V2 automatically.

---

## 22. Mental Model

V1 最重要的理解：

```text
Document / Block
= 文档结构

Chunk
= 检索知识单位

Embedding
= Chunk 的机器可比较语义表示

IndexRecord
= Chunk + Index Representation

IndexStore
= IndexRecord 的持久化位置
```

最终链路：

```text
Human-readable Knowledge
        ↓
Chunk
        ↓
Embedding
        ↓
Machine-comparable Vector
        ↓
IndexRecord
        ↓
Persistent Index
```

V2 才会增加：

```text
User Query
    ↓
Query Embedding
    ↓
Similarity Search
    ↓
Retrieved Chunks
```

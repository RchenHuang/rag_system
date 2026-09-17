# RAG System — V0 Architecture Spec

## 1. V0 Goal

V0 的目标不是实现完整 RAG，也不追求检索效果。

V0 只负责建立整个 RAG 系统未来演进所需要的基础架构：

```text
Raw File
   ↓
Parser
   ↓
Document
   ↓
Chunker
   ↓
Chunk[]
```

这一版结束时，系统必须能够：

1. 读取一个最简单的 `.txt` 或 `.md` 文件
2. 将文件转换成统一的 `Document`
3. 将 `Document` 转换成若干 `Chunk`
4. 保留基本 metadata
5. 通过测试验证完整数据流

V0 不实现真正的检索、向量数据库、Embedding 和 LLM。

---

# 2. Design Principle

整个项目必须遵循：

```text
Raw Data
   ↓
Standard Internal Representation
   ↓
Processing Pipeline
```

不同类型的输入文件最终都应该被转换成统一的数据结构。

未来：

```text
PDF
Word
Markdown
HTML
PPT
Image
```

都应该经过不同 Parser：

```text
PDFParser
MarkdownParser
WordParser
...
```

但最终输出统一：

```text
Document
```

这样 Chunker、Transformer、Indexer 不需要关心原始文件格式。

---

# 3. Core Data Flow

V0 数据流：

```text
                     V0

                Raw File
                    │
                    ▼
              ┌──────────┐
              │  Parser  │
              └────┬─────┘
                   │
                   ▼
               Document
                   │
                   ▼
              ┌──────────┐
              │ Chunker  │
              └────┬─────┘
                   │
                   ▼
                Chunk[]
```

未来会扩展为：

```text
Raw File
   ↓
Parser
   ↓
Document
   ↓
Chunker
   ↓
Chunk[]
   ↓
Transformer
   ↓
EnrichedChunk[]
   ↓
Indexer
   ↓
Knowledge Store
```

但 **V0 禁止实现 Transformer 和 Indexer 的实际逻辑**。

可以预留目录或 Protocol，但不要提前实现。

---

# 4. Core Data Models

V0 需要定义三个核心数据结构：

```text
Document
Block
Chunk
```

---

## 4.1 Document

`Document` 表示：

> 一个已经被 Parser 转换成统一内部格式的完整文档。

建议字段：

```python
Document
├── id: str
├── source: str
├── filename: str
├── mime_type: str | None
├── blocks: list[Block]
└── metadata: dict[str, Any]
```

含义：

### id

系统内部唯一 Document ID。

暂时可以使用 UUID。

---

### source

原始文件路径或者来源。

例如：

```text
./data/agent_memory.md
```

未来可能扩展：

```text
s3://bucket/file.pdf

https://example.com/article

notion://page/123
```

所以不要把它命名成单纯的 `file_path`。

---

### filename

原始文件名。

例如：

```text
agent_memory.md
```

---

### mime_type

例如：

```text
text/markdown
text/plain
application/pdf
```

V0 可以允许为 `None`。

---

### blocks

文档内部结构化内容。

```python
list[Block]
```

Parser 的主要任务就是生成这些 Block。

---

### metadata

额外信息。

```python
{
    "author": "...",
    "created_at": "...",
    "course": "...",
}
```

V0 不要求自动生成复杂 metadata。

默认：

```python
{}
```

---

# 4.2 Block

`Block` 表示：

> Parser 从原始文件中提取出来的最小结构化内容单元。

例如：

```text
Heading
Paragraph
Table
Code
Image
```

V0 主要支持：

```text
heading
paragraph
```

建议：

```python
Block
├── id: str
├── type: str
├── text: str
├── order: int
├── page: int | None
├── heading_level: int | None
└── metadata: dict[str, Any]
```

例如 Markdown：

```markdown
# Agent Memory

Agent memory can be divided into...

## Short-term Memory

Short-term memory stores...
```

Parser 输出可能为：

```text
Block 1

type = heading
text = Agent Memory
heading_level = 1
order = 0


Block 2

type = paragraph
text = Agent memory can be divided into...
order = 1


Block 3

type = heading
text = Short-term Memory
heading_level = 2
order = 2


Block 4

type = paragraph
text = Short-term memory stores...
order = 3
```

---

# 4.3 Chunk

`Chunk` 表示：

> 最终交给未来 Retrieval System 的最基本知识单元。

V0：

```python
Chunk
├── id: str
├── document_id: str
├── content: str
├── block_ids: list[str]
├── order: int
└── metadata: dict[str, Any]
```

V0 不包含：

```text
embedding
keywords
questions
summary
score
```

这些属于未来版本。

---

# 5. Parser Interface

需要定义统一 Parser 接口。

例如：

```python
class Parser(Protocol):

    def parse(self, source: Path) -> Document:
        ...
```

或者使用 Abstract Base Class。

重点不是具体使用 Protocol 还是 ABC。

重点是未来所有 Parser 都遵循：

```text
Input
    Path / Source

Output
    Document
```

---

# 6. V0 Parser

V0 只实现一个简单 Parser。

推荐：

```text
MarkdownParser
```

也可以同时支持：

```text
.txt
.md
```

但不要支持：

```text
PDF
Word
PPT
Excel
Image
OCR
```

这些全部属于 V1+。

---

## MarkdownParser Basic Behavior

输入：

```markdown
# Redis

Redis is an in-memory database.

## Redis Streams

Redis Streams provides an append-only log.
```

输出：

```text
Document

├─ Block
│   type = heading
│   text = Redis
│
├─ Block
│   type = paragraph
│   text = Redis is an in-memory database.
│
├─ Block
│   type = heading
│   text = Redis Streams
│
└─ Block
    type = paragraph
    text = Redis Streams provides an append-only log.
```

V0 不需要完整支持全部 Markdown 语法。

只需要可靠识别：

```text
# Heading
## Heading
### Heading

Paragraph
```

其他 Markdown 内容暂时可以作为普通文本。

---

# 7. Chunker Interface

定义统一接口：

```python
class Chunker(Protocol):

    def chunk(self, document: Document) -> list[Chunk]:
        ...
```

未来可能有：

```text
TokenChunker
TitleChunker
SemanticChunker
ParentChildChunker
```

但 V0 只实现一个：

```text
SimpleChunker
```

---

# 8. V0 SimpleChunker

V0 不需要真正 Tokenizer。

先采用简单策略：

```text
按照 Block 聚合
+
限制最大字符数
```

例如：

```text
max_chars = 1000
```

逻辑：

```text
遍历 blocks

如果加入当前 block 后：

content <= max_chars

→ 加入当前 chunk


否则：

→ 保存当前 chunk
→ 创建新 chunk
```

必须保证：

```text
Block 不应该被随意从中间截断。
```

也就是说：

```text
Paragraph A
Paragraph B
Paragraph C
```

可以：

```text
Chunk 1
A + B

Chunk 2
C
```

不要：

```text
Chunk 1
A + B 前半段

Chunk 2
B 后半段 + C
```

真正 token-based chunking 放到 V1。

---

# 9. Suggested Repository Structure

建议：

```text
rag-system/

├── pyproject.toml
├── README.md
│
├── src/
│   └── rag/
│
│       ├── __init__.py
│
│       ├── models/
│       │   ├── __init__.py
│       │   ├── document.py
│       │   └── chunk.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   │
│       │   ├── parsers/
│       │   │   ├── __init__.py
│       │   │   ├── base.py
│       │   │   └── markdown.py
│       │   │
│       │   └── chunkers/
│       │       ├── __init__.py
│       │       ├── base.py
│       │       └── simple.py
│       │
│       └── pipeline.py
│
├── tests/
│   ├── fixtures/
│   │   └── sample.md
│   │
│   ├── test_parser.py
│   ├── test_chunker.py
│   └── test_pipeline.py
│
└── examples/
    └── run_ingestion.py
```

---

# 10. Pipeline

V0 应该提供一个非常简单的 ingestion pipeline。

例如：

```python
pipeline = IngestionPipeline(
    parser=MarkdownParser(),
    chunker=SimpleChunker(),
)

chunks = pipeline.run("sample.md")
```

内部：

```text
source
   ↓
parser.parse()
   ↓
Document
   ↓
chunker.chunk()
   ↓
list[Chunk]
```

Pipeline 不应该知道 Markdown 具体怎么解析。

也不应该知道 SimpleChunker 具体怎么切。

它只负责 orchestration。

---

# 11. Dependency Direction

必须保持：

```text
pipeline
   ↓
interfaces
   ↓
implementations
```

不要出现：

```text
MarkdownParser
直接调用 SimpleChunker
```

Parser 和 Chunker 不应该互相依赖。

正确结构：

```text
            Pipeline
          /          \
      Parser        Chunker
        │              │
MarkdownParser   SimpleChunker
```

---

# 12. ID Strategy

Document、Block、Chunk 都需要 ID。

V0 直接使用：

```python
uuid.uuid4()
```

即可。

不要在 V0 设计复杂 deterministic ID、content hash 或 distributed ID。

---

# 13. Metadata Strategy

所有核心对象都允许：

```python
metadata: dict[str, Any]
```

但不要滥用 metadata。

核心语义明确的字段应该成为正式字段。

例如：

```text
document_id
order
content
```

不要全部塞进：

```python
metadata
```

Metadata 只放：

```text
可选
扩展性
来源相关
业务相关
```

的信息。

---

# 14. Tests

V0 必须包含测试。

最低测试要求：

## Parser test

输入：

```markdown
# Agent Memory

Agent memory contains short-term memory.

## Short-term Memory

Short-term memory stores session context.
```

验证：

```text
Document 存在

blocks 数量正确

heading type 正确

heading_level 正确

paragraph 内容正确

order 正确
```

---

## Chunker test

创建：

```text
Document
 ↓
多个 Blocks
```

调用：

```text
SimpleChunker
```

验证：

```text
输出至少一个 Chunk

document_id 正确

block_ids 正确

chunk order 正确

content 顺序正确
```

---

## Pipeline test

完整测试：

```text
sample.md
    ↓
MarkdownParser
    ↓
Document
    ↓
SimpleChunker
    ↓
Chunk[]
```

必须成功。

---

# 15. Example Script

提供：

```text
examples/run_ingestion.py
```

运行：

```bash
python examples/run_ingestion.py
```

打印：

```text
Document:
id: ...
filename: sample.md
blocks: 4

Chunks:

Chunk 0
----------------
# Agent Memory

Agent memory contains short-term memory.

Chunk 1
----------------
## Short-term Memory

Short-term memory stores session context.
```

具体格式不重要。

重点是能够直观看见数据流。

---

# 16. Explicit Non-Goals

V0 禁止实现：

```text
Embedding

Vector Database

Elasticsearch

BM25

Retriever

Reranker

LLM

Ragas

Transformer

Question Generation

Keyword Extraction

Summary

Metadata Extraction

PDF Parsing

OCR

Parent-Child Chunking

Semantic Chunking

Token-based Chunking

FastAPI

Redis

Task Queue

Docker Infrastructure
```

如果某个依赖不是完成 V0 所必需的，不要添加。

---

# 17. Engineering Constraints

代码应满足：

```text
Python >= 3.12

类型注解

dataclass 或 Pydantic 均可

pytest

模块职责清晰

避免过度抽象

避免提前设计 V1+
```

不要创建大量没有实际用途的：

```text
Factory
Manager
Registry
Service
Repository
Adapter
Controller
```

V0 应尽可能简单。

抽象只用于：

```text
Parser interface

Chunker interface
```

因为这两个已经明确会有多个实现。

---

# 18. V0 Acceptance Criteria

只有满足以下全部条件，V0 才算完成。

### Architecture

* [ ] 存在 Document
* [ ] 存在 Block
* [ ] 存在 Chunk
* [ ] Parser 和 Chunker 有明确接口
* [ ] Parser 与 Chunker 解耦
* [ ] Pipeline 只负责 orchestration

### Functionality

* [ ] 可以读取一个 Markdown 文件
* [ ] 可以产生 Document
* [ ] 可以识别基本 heading / paragraph
* [ ] 可以产生 Chunk[]
* [ ] Chunk 可以追溯到 Document
* [ ] Chunk 可以追溯到来源 Block

### Quality

* [ ] pytest 全部通过
* [ ] 有完整 pipeline test
* [ ] 有 example script
* [ ] 没有引入 Vector DB / LLM / Embedding
* [ ] 没有提前实现 V1+

---

# 19. Expected Final Data Flow

V0 完成后应该能够清晰展示：

```text
sample.md
    │
    ▼

MarkdownParser
    │
    ▼

Document
│
├── Block 0
├── Block 1
├── Block 2
└── Block 3
    │
    ▼

SimpleChunker
    │
    ▼

Chunk 0
Chunk 1
...
```

这就是 V0 的全部目标。

---

# 20. Instructions for Coding Agent

Before implementing:

1. Inspect the current repository.
2. Understand existing project structure and dependencies.
3. Do not rewrite working code unnecessarily.
4. Use this specification as the source of truth.

Implementation requirements:

1. Implement only V0.
2. Keep the architecture minimal.
3. Avoid premature abstractions.
4. Do not add V1+ functionality.
5. Add tests for every core component.
6. Run the full test suite.
7. Fix all failures before completing the task.

When finished, report:

```text
1. Architecture implemented
2. Files created
3. Files modified
4. Main design decisions
5. Tests executed and results
6. Any deviation from SPEC_V0.md
7. Anything that should be considered before V1
```

Do not begin V1 automatically.

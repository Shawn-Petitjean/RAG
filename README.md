*This project has been created as part of the 42 curriculum by shapetit.*

# RAG Against the Machine

## Description

This project implements a **Retrieval-Augmented Generation (RAG)** system capable of answering questions about the vLLM codebase. Instead of relying solely on a language model's internal knowledge, the system first retrieves relevant code snippets and documentation from an indexed knowledge base, then uses them as context to generate accurate, source-grounded answers.

The pipeline covers the full RAG workflow: ingestion, chunking, indexing, retrieval, answer generation, and evaluation.

## Instructions

### Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) as the package manager

### Installation

```bash
uv venv
uv sync
# or
make install
```

### Execution

#### 1. Index the vLLM repository

```bash
uv run python -m src index --chunk_size 2000
```

#### 2. Search for a single query

```bash
uv run python -m src search "How to configure the OpenAI compatible server?" --k 5
```

#### 3. Process a full dataset

```bash
uv run python -m src search_dataset --k 10
```

#### 4. Answer a single question

```bash
uv run python -m src answer "What activation formats does the fused batched MoE layer return?"
```

#### 5. Generate answers for a full dataset

```bash
uv run python -m src answer_dataset
```

#### 6. Evaluate retrieval performance

```bash
uv run python -m src evaluate
```

### Makefile shortcuts

```bash
make install   # Install dependencies
make run       # Run the main script
make debug     # Run with Python debugger
make clean     # Remove caches and temporary files
make lint      # Run flake8 and mypy
```

## System Architecture

The RAG pipeline is organized into the following components:

```
vLLM repository
      ↓
 [Chunking]
  index.py — py_chunking / md_chunking
      ↓
 [Storage]
  utils.py — save_file / get_chunk (JSON)
      ↓
 [Indexing]
  bm25.py — BM25 index (bm25s)
      ↓
 [Retrieval]
  search.py — process_data_set / save_search
      ↓
 [Generation]
  answer.py — Qwen/Qwen3-0.6B via Transformers
      ↓
 [Evaluation]
  evaluate.py — Recall@k metrics
```

All data models are defined using **Pydantic** in `data_model.py`, ensuring type safety and easy JSON serialization throughout the pipeline. The CLI is exposed via **Python Fire** in `interface.py`.

## Chunking Strategy

Different strategies are applied depending on the file type:

**Python files (`.py`) — AST-based chunking**
The `ast` module parses each file into a syntax tree. Functions and classes are extracted as individual chunks using their start and end line numbers, converted to character indices. A chunk for global-level code (imports, constants, module-level variables) is also created from the content before the first definition. Chunks exceeding `max_chunk_size` are split using a sliding window with a configurable overlap (`OVLAP`) to preserve context across boundaries.

**Markdown files (`.md`) — Header-based chunking**
Each file is split at heading lines (lines starting with `#`). Each section between two headings becomes one chunk. Sections exceeding `max_chunk_size` are further split with the same sliding window strategy.

**Common parameters:**
- Maximum chunk size: 2000 characters (configurable via `--chunk_size`)
- Overlap between split chunks: configurable via `OVLAP` in `config.py`
- Minimum chunk size: configurable via `MIN_CHUNK` — chunks below this threshold are discarded

## Retrieval Method

Retrieval is performed using **BM25** (Best Match 25) via the `bm25s` library.

BM25 scores each chunk against a query by combining two signals:
- **TF (Term Frequency):** how often a query term appears in the chunk
- **IDF (Inverse Document Frequency):** how rare the term is across all chunks — rarer terms score higher

The ranking formula is controlled by two parameters tuned for this codebase:
- `k1`: controls term frequency saturation
- `b`: controls document length normalization

Stopwords are filtered during tokenization to reduce noise from common words. The index is saved to disk after the first `index` call and reloaded on subsequent commands, avoiding re-indexing on every run.

Retrieved chunks are returned with their `file_path`, `first_character_index`, and `last_character_index` — the exact format required by the evaluation system.

## Performance Analysis

Evaluation is performed using **Recall@k** — the proportion of ground-truth sources successfully retrieved in the top-k results. A source is considered found if the overlap (IoU) between the retrieved chunk and the reference chunk exceeds 5%.

| Dataset | Recall@1 | Recall@3 | Recall@5 | Recall@10 |
|---------|----------|----------|----------|-----------|
| Docs    | —        | —        | **0.80** | —         |
| Code    | —        | —        | **0.72** | —         |

**Required thresholds:** Docs ≥ 0.80 ✅ — Code ≥ 0.50 ✅

The code dataset scores above the required threshold thanks to AST-based chunking that preserves function and class boundaries, avoiding cuts in the middle of logical units.

## Design Decisions

**Why BM25 over TF-IDF?**
BM25 handles term frequency saturation better than raw TF-IDF — a term appearing 100 times does not score 100× higher than one appearing once. This is particularly useful for source code where keywords like `self` or `return` repeat heavily.

**Why AST for Python chunking?**
Regex or line-based splitting can easily cut a function in half. Using the `ast` module ensures chunks always align with syntactic boundaries (functions, classes), which improves the semantic coherence of each chunk and therefore retrieval quality.

**Why separate indexes for code and docs?**
Python and Markdown have very different vocabularies and structures. Keeping them in a unified index avoids vocabulary pollution between the two domains.

**Why Pydantic for all data models?**
Pydantic provides automatic validation and easy JSON serialization/deserialization with `model_dump_json()` and `model_validate()`. This eliminates an entire class of bugs related to malformed data flowing through the pipeline.

## Challenges Faced

**Character index alignment**
The evaluation system measures overlap using character indices. An off-by-one error in `get_index()` (adding +1 to start and -1 to end) caused all chunks to be slightly misaligned with the ground truth, silently degrading recall. Fixing this required careful tracing of how line numbers are converted to character positions.

**BM25 corpus persistence**
When saving the BM25 index with `retriever.save()`, the corpus (list of indices) must be explicitly passed as an argument. Without it, `retrieve()` cannot map results back to the original chunks and raises an `IndexError` at runtime.

**Chunk size vs. recall tradeoff**
Larger chunks increase the chance of containing the relevant content but reduce precision and may exceed the model's context window. Smaller chunks improve precision but may miss context split across boundaries. The overlap mechanism mitigates this at the cost of a larger index.

**Qwen3 `<think>` blocks**
Qwen3-0.6B generates internal reasoning wrapped in `<think>...</think>` tags before producing the actual answer. These blocks must be stripped from the output before storing the answer, otherwise the `answer` field in the JSON output contains reasoning rather than a response.

## Example Usage

```bash
# Index the repository with default chunk size
uv run python -m src index --chunk_size 2000

# Ask a single question
uv run python -m src answer "What HTTP endpoint is used to load a LoRA adapter?"

# Run retrieval on the full docs dataset and save results
uv run python -m src search_dataset --k 10

# Generate answers for all retrieved results
uv run python -m src answer_dataset

# Evaluate retrieval quality
uv run python -m src evaluate
```

## Resources

**RAG & Retrieval**
- [Lewis et al. (2020) — Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
- [BM25 explained — Robertson & Zaragoza](https://www.staff.city.ac.uk/~seb/publications/foundations_of_ir.pdf)
- [bm25s documentation](https://github.com/xhluca/bm25s)

**Python tooling**
- [Python `ast` module documentation](https://docs.python.org/3/library/ast.html)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Python Fire documentation](https://github.com/google/python-fire)

**Language models**
- [Qwen3 model card — Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Transformers documentation](https://huggingface.co/docs/transformers)

**AI usage in this project**
Claude (Anthropic) was used as a learning and debugging assistant throughout the project. Specifically:
- Explaining how `bm25s`, `ast`, and Pydantic work with concrete examples
- Helping identify bugs (off-by-one in character indices, corpus not saved with BM25 index, `<think>` blocks in Qwen3 output)
- optimisation of bm25 with preprocess

All code was written and understood by the student — AI was used as a reference tool, not a code generator.

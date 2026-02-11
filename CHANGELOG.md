# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2026-02-05

### Synced (Search-Roca v0.8.1)
- **PoC Integration**: Synced latest `search-roca` PoC v5 & v6 files to `poc/bjy/`.
  - **Modules**: `backend`, `frontend`, `poc` (Reasoning Engine, Map Debugger, Latency Benchmark).
  - **Data**: Updated Mock Product DB and Map Data.
- **Dependencies**: Updated `requirements.txt` to match `search-roca` environment.
- **Maintenance**: Moved old PoC files to `poc/bjy/old/` and gitignored them.

## [0.5.0] - 2026-02-05

### Added (PoC v2 Integration)
- **Integration**: Ported complete PoC v2 AG Module from `search-roca`.
- **Scripts** (`poc/`):
    - `poc_v2_step1_query_processor.py`: Intent Extraction.
    - `poc_v2_step2_hybrid_retrieval.py`: Hybrid Search (BM25+Vector).
    - `poc_v2_step3_ag_reranker.py`: LLM Reranking & Location Guide.
    - `poc_v2_generate_mock_data.py`: Mock DB enrichment w/ LLM.
    - `poc_v2_generate_golden_dataset.py`: 30 Hard Test Cases.
- **Reports**:
    - `poc/POC_v2_FINAL_REPORT.md`: Overall PoC summary validation report.

## [0.3.1] - 2026-01-19

### Added (RAG Robustness PoC)
- **Integration**: Merged RAG Optimization PoC from `search-roca` into main repo.
- **Scripts** (`poc/`):
    - `RAG_System_experiment_keyword.py`: Verified K=30/Keyword Optimization script.
    - `RAG_System_experiment_baseline.py`: Sentence-input baseline script.
    - `generate_large_data.py`: 200-product scaling data generator.
- **Reports** (`docs/`):
    - `RAG_ROBUSTNESS.md`: Final optimization report (K=30 Success).
    - `RAG_BASELINE.md`: Baseline failure analysis.
- **Prompts**: `poc/prompts/intent_rules_prompt.txt` (Rule-based Intent Classification).

---

## [0.3.0] - 2026-01-16

### Added (LangGraph Migration)
- **Logic**: Migrated backend logic to `LangGraph` (Cyclic State Machine)
- **Agent**: Implemented 5-node workflow (`NLU`, `Search`, `AmbiguityCheck`, `Clarification`, `Response`)
- **Context**: Full conversation history persistence using `MemorySaver`
- **Frontend**: Added `/kioskmode` route and Landing Page UI
- **Dependencies**: `langgraph`, `langchain`, `langchain-google-genai`

### Improved
- **Clarification**: Added "Drill-Down" logic to clarify broad categories (e.g., Cleaning -> Detergent vs Tools)
- **Loop Prevention**: Fixed infinite loop bug where AI kept asking same questions
- **Language**: Strictly enforced Korean output in system prompts

## [0.2.0] - 2026-01-16

### Added
- **Category System**: Product categorization with major/middle categories (대분류/중분류)
- `category_matcher.py`: Keyword-based category matching script
- `categories` table: 48 category entries (12 major × multiple middle)
- Products table now has `category_major` and `category_middle` columns

### Stats
- 401 products matched (67%)
- 200 products unmatched (to be fixed with full re-crawl)

## [0.1.1] - 2026-01-16

### Fixed
- Updated `requirements.txt` with exact package versions from search-roca conda environment
- Added missing dependencies: `sentence-transformers`, `huggingface-hub`, `tokenizers`, `safetensors`, `scipy`, `scikit-learn`

## [0.1.0] - 2026-01-16

### Added
- **Product Database** (`backend/database/`)
  - `products.db`: SQLite database with 601 crawled products
  - `images/`: 601 product images from Daiso Mall ranking
  - `database.py`: Database operations module
  - `embeddings.py`: CLIP-based multimodal embeddings (text + image)
  - `generate_test_data.py`: 3000 test utterances generator (85% normal, 15% hard)

### Database Schema
- `products`: id, rank, name, price, image_url, image_name, image_path
- `test_utterances`: utterance, difficulty, expected_product_id
- `product_embeddings`: text_embedding, image_embedding (CLIP 512-dim vectors)

### Dependencies Added
- `selenium`, `webdriver-manager`: Web crawling
- `transformers`, `torch`: CLIP embeddings
- `Pillow`: Image processing

---

## [0.0.0] - Initial

- Initial project setup
- Basic FastAPI backend structure
- Frontend placeholder

import os
import json
import sys
import argparse
from pathlib import Path

# Add project root to sys.path to allow importing poc.kdg modules
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

try:
    from poc.kdg.poc_v5_experiment_phase_1 import advanced_rerank
except ImportError:
    print("Error: Could not import 'advanced_rerank' from 'poc.kdg.poc_v5_experiment_phase_1'.")
    print("Make sure the file exists and sys.path is correct.")
    sys.exit(1)

def load_catalog(catalog_path):
    """Loads catalog TSV into a dict {doc_id: {id, name, desc}}"""
    products = {}
    if not os.path.exists(catalog_path):
        print(f"Warning: Catalog file not found: {catalog_path}")
        return products
        
    with open(catalog_path, 'r', encoding='utf-8') as f:
        # Skip header if exists (starts with # or id)
        for line in f:
            if line.startswith("#") or line.lower().startswith("doc_id") or line.lower().startswith("id"):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                doc_id = parts[0]
                title = parts[1]
                text = parts[2]
                # desc is text
                products[doc_id] = {"id": doc_id, "name": title, "desc": text}
    return products

def process_benchmark_output(run_dir, catalog_path, output_file):
    run_path = Path(run_dir)
    detail_path = run_path / "detail.jsonl"
    
    if not detail_path.exists():
        print(f"Error: detail.jsonl not found in {run_dir}")
        return

    print(f"Loading catalog from {catalog_path}...")
    catalog = load_catalog(catalog_path)
    
    print(f"Processing benchmark results from {detail_path}...")
    
    results = []
    
    with open(detail_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            case = json.loads(line)
            
            # Skip non-case logs
            if "case_id" not in case: continue
            
            query = case.get("intent_text", "") or case.get("raw_text", "")
            
            # Get candidates from retrieval phase
            # run_benchmark outputs 'predicted_doc_ids' (Top N)
            # We take Top 10 for reranking (save tokens/time)
            top_ids = case.get("predicted_doc_ids", [])[:10]
            
            candidates = []
            for doc_id in top_ids:
                if doc_id in catalog:
                    candidates.append(catalog[doc_id])
                else:
                    candidates.append({"id": doc_id, "name": "Unknown", "desc": ""})
            
            print(f"Reranking Query: '{query}' ({len(candidates)} candidates)...")
            
            # Call KDG Reranker
            rerank_result = advanced_rerank(query, candidates)
            
            output_item = {
                "case_id": case.get("case_id"),
                "query": query,
                "retrieved_ids": top_ids,
                "selected_id": rerank_result.get("selected_id"),
                "reason": rerank_result.get("reason"),
                "latency_ms": rerank_result.get("latency", 0) * 1000
            }
            results.append(output_item)
            
            print(f"  -> Selected: {output_item['selected_id']}")

    # Save Results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\nReranking Complete. Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, help="Directory containing benchmark detail.jsonl")
    parser.add_argument("--catalog", required=True, help="Path to catalog TSV")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    
    args = parser.parse_args()
    
    process_benchmark_output(args.run_dir, args.catalog, args.out)

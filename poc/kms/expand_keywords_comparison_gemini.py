
import os
import re
import time
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
import sys

# Import Gemini logic from existing nlu.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.logic.nlu import expand_search_keywords as expand_gemini_func

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_JSON_PATH = os.path.join(BASE_DIR, "poc", "data", "extracted_keywords.json")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "poc", "data", "expansion_result.json")

def load_extracted_data(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def main():
    script_start_time = time.time()
    print(f"Reading extracted keywords from {INPUT_JSON_PATH}...")
    
    data_list = load_extracted_data(INPUT_JSON_PATH)
    if not data_list:
        return

    print(f"Found {len(data_list)} items.")
    
    api_latencies = []
    processing_times = []
    
    # Structure for final output
    final_results = []
    
    # Process all keywords
    for i, item in enumerate(data_list):
        # Extract keyword from previous step result
        # Structure: item -> extraction -> keyword
        extraction = item.get("extraction", {})
        kw = extraction.get("keyword", "")
        
        if not kw or "error" in extraction:
            print(f"[{i+1}] Skipping invalid/error keyword.")
            item["expansion"] = {"error": "No valid keyword from extraction"}
            final_results.append(item)
            continue
            
        func_start_time = time.time()
        
        # Call Gemini expansion (using existing nlu logic)
        try:
             # usage now contains 'latency_seconds' from nlu.py modification
             expanded_list, usage = await expand_gemini_func(kw, return_usage=True)
             
             func_end_time = time.time()
             total_time = func_end_time - func_start_time # Total time including wrapper overhead
             
             api_time = usage.get("latency_seconds", total_time) # Fallback to total if not found
             processing_time = total_time - api_time
             if processing_time < 0: processing_time = 0

             api_latencies.append(api_time)
             processing_times.append(processing_time)
             
             print(f"[Gemini] {i+1}/{len(data_list)}: '{kw}' -> {len(expanded_list)} items")
             
             # Append result to item structure
             item["expansion"] = {
                 "expanded_keywords": expanded_list,
                 "meta": {
                     "total_time_seconds": total_time,
                     "api_latency_seconds": api_time,
                     "processing_overhead_seconds": processing_time,
                     "total_tokens": usage.get("total_tokens", 0),
                     "prompt_tokens": usage.get("prompt_tokens", 0),
                     "completion_tokens": usage.get("completion_tokens", 0)
                 }
             }

        except Exception as e:
            print(f"Error processing {kw}: {e}")
            item["expansion"] = {"error": str(e)}

        final_results.append(item)

        # Frequent save
        if (i+1) % 5 == 0:
             with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, ensure_ascii=False, indent=2)

    # Final Save
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
        
    script_end_time = time.time()
    total_duration = script_end_time - script_start_time

    # Summary Statistics
    valid_count = len(api_latencies)
    if valid_count > 0:
        # API Stats
        max_api = max(api_latencies)
        min_api = min(api_latencies)
        avg_api = sum(api_latencies) / valid_count
        
        # Processing Stats
        max_proc = max(processing_times)
        min_proc = min(processing_times)
        avg_proc = sum(processing_times) / valid_count
        
        stats_msg = (
            f"\n[Gemini Expansion Analysis (N={valid_count})]\n"
            f"1. API Call Latency (Network + Model):\n"
            f"   - AVG: {avg_api:.3f}s (Min: {min_api:.3f}s, Max: {max_api:.3f}s)\n"
            f"2. Processing/Overhead Time (Script Logic):\n"
            f"   - AVG: {avg_proc:.3f}s (Min: {min_proc:.3f}s, Max: {max_proc:.3f}s)\n"
        )
    else:
        stats_msg = "\n[Gemini Stats] No successful requests."

    print(stats_msg)
    print(f"Total Script Execution Time: {total_duration:.2f} seconds")
    print(f"Results saved to {OUTPUT_JSON_PATH}")
    
    # Export to TSV for run_benchmark.py
    tsv_path = OUTPUT_JSON_PATH.replace(".json", ".tsv")
    save_as_tsv(final_results, tsv_path)
    print(f"TSV for benchmark saved to {tsv_path}")

def save_as_tsv(data: List[Dict], filepath: str):
    # Columns required by run_benchmark.py:
    # id, raw_text, intent_text, expected_doc_ids, expected_category, needs_clarification, notes
    
    header = "id\traw_text\tintent_text\texpected_doc_ids\texpected_category\tneeds_clarification\tnotes"
    lines = [header]
    
    for i, item in enumerate(data):
        # 1. ID
        row_id = f"STT-{item.get('id', i+1):05d}"
        
        # 2. Raw Text (Utterance)
        raw_text = item.get("utterance", "").strip()
        if not raw_text:
            raw_text = "(Empty Utterance)"
            
        # 3. Intent Text (Extracted Keyword)
        # Using the primary extracted keyword as the intended search query
        extraction = item.get("extraction", {})
        intent_text = extraction.get("keyword", "").strip()
        
        if not intent_text:
            intent_text = raw_text # Fallback if no keyword extracted
            
        # 4. Expected Doc IDs (Unknown/Ground Truth missing)
        expected_doc_ids = "" 
        
        # 5. Expected Category (Unknown)
        expected_category = ""
        
        # 6. Needs Clarification
        # If error present or empty intent, verify might be needed
        needs_clarification = "true" if not intent_text or "error" in extraction else "false"
        
        # 7. Notes
        # Storing expanded keywords or original filename here for reference
        expansion = item.get("expansion", {})
        expanded_kws = expansion.get("expanded_keywords", [])
        if isinstance(expanded_kws, list):
            # Join top 5 expanded keywords for visibility
            note_content = ",".join(expanded_kws[:5])
        else:
            note_content = ""
        
        row = [
            row_id,
            raw_text,
            intent_text,
            expected_doc_ids,
            expected_category,
            needs_clarification,
            f"Src:{item.get('filename','')}|Exp:{note_content}"
        ]
        
        # Sanitize tabs/newlines in fields to avoid breaking TSV
        safe_row = [str(col).replace('\t', ' ').replace('\n', ' ') for col in row]
        lines.append("\t".join(safe_row))
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    asyncio.run(main())

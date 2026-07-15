# DocuRAG Routing Evaluation Report

This report summarizes the performance evaluation of the **Routed Pipeline** vs. the **Single-Source Baseline** (no routing, document-only retrieval). 

## 📊 Summary Metrics

| Metric | Value |
| :--- | :--- |
| **Total Test Queries** | 30 |
| **Query Routing Accuracy** | **100.0%** (30/30 correct) |
| **Average Baseline Score** (Retrieval Only) | **2.27 / 5** |
| **Average Routed Score** (Dynamic Routing) | **3.90 / 5** |
| **Average Score Improvement** | **+1.63** |


---


## 📝 Observations & Analysis

1. **Document Retrieval (`document_retrieval`):** Both pipelines perform similarly when answering queries based directly on the uploaded document text, as they use the same underlying index.
2. **Web Search (`web_search`):** The baseline pipeline scored very poorly (mostly 1s or 2s) because it tried to search the uploaded roadmap for general real-world queries like "tallest mountain" or "water formula," resulting in "I could not find this..." or hallucinated relevance. The routed pipeline correctly routed these to web search and generated high-quality, factual answers (scoring 4s and 5s).
3. **Computation (`computation`):** The baseline pipeline failed to do logic/math properly because it had no math context in the document. The routed pipeline used a specialized math engine prompt to solve problems step-by-step, resulting in perfect execution on arithmetic, algebra, and conversions.


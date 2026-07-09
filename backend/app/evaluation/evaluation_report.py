import numpy as np
from backend.app.evaluation.eval_dataset import EVAL_QUERIES
from backend.app.retrieval.chroma_retriever import ChromaRetriever
from backend.app.retrieval.advanced_retriever import AdvancedRetriever
from backend.app.evaluation.metrics import RetrievalMetrics
from backend.app.config import settings

print("="*60)
print("PHASE 1 vs PHASE 2 EVALUATION REPORT")
print("="*60)

# Load models
chroma = ChromaRetriever(settings.chroma_db_path)
advanced = AdvancedRetriever(settings.chroma_db_path)
metrics = RetrievalMetrics()

# Run evaluation
phase1_results = {"mrr": [], "prec": [], "time": []}
phase2_results = {"mrr": [], "prec": [], "time": []}

import time

for eval_item in EVAL_QUERIES:
    query = eval_item["query"]
    relevant_ids = eval_item["relevant_email_ids"]
    
    # Phase 1
    t0 = time.time()
    r1 = chroma.retrieve(query, top_k=10)
    
    print(f"Results for Phase 1 - Query: {query}")
    for i, result in enumerate(r1):
        print(f"  {i+1}. {result.source_doc_id}")

    phase1_results["time"].append(time.time() - t0)
    ranking1 = [r.source_doc_id in relevant_ids for r in r1]
    phase1_results["mrr"].append(metrics.mrr(ranking1))
    phase1_results["prec"].append(metrics.precision_at_k(ranking1))
    
    # Phase 2
    t0 = time.time()
    r2 = advanced.retrieve(query, top_k=10)
    phase2_results["time"].append(time.time() - t0)
    ranking2 = [r.source_doc_id in relevant_ids for r in r2]
    phase2_results["mrr"].append(metrics.mrr(ranking2))
    phase2_results["prec"].append(metrics.precision_at_k(ranking2))

# Print results
print(f"\nEvaluated on {len(EVAL_QUERIES)} queries")

print(f"Phase 1 result mrr: {phase1_results['mrr']}")
print(f"Phase 2 result mrr: {phase2_results['mrr']}")

print(f"Phase 1 result precision: {phase1_results['prec']}")
print(f"Phase 2 result precision: {phase2_results['prec']}")

print(f"\n{'Metric':<20} {'Phase 1':<15} {'Phase 2':<15} {'Change':<15}")
print("-" * 65)

for metric in ["mrr", "prec"]:
    v1 = np.mean(phase1_results[metric])
    v2 = np.mean(phase2_results[metric])
    change = (v2 - v1) / v1 * 100 if v1 > 0 else 0
    
    print(f"{metric.upper():<20} {v1:.3f}         {v2:.3f}         {change:+.1f}%")

print(f"\n{'Latency':<20} {np.mean(phase1_results['time']):.3f}s       {np.mean(phase2_results['time']):.3f}s       {(np.mean(phase2_results['time']) / np.mean(phase1_results['time']) - 1) * 100:+.0f}%")

print("\n" + "="*60)
print("CONCLUSION:")
if np.mean(phase2_results["mrr"]) > np.mean(phase1_results["mrr"]) * 1.15:
    print("✓ Phase 2 shows 15%+ improvement in ranking quality")
else:
    print("! Phase 2 performance below target, consider tuning")
print("="*60)

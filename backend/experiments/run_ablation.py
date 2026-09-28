import os
import json
import logging
import sys

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.evaluation.benchmark_runner import BenchmarkRunner
from app.evaluation.reports import generate_ablation_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(os.path.join(data_dir, "corpus.jsonl")):
        logger.error(f"Dataset not found at {data_dir}. Please run download_scifact.py first.")
        sys.exit(1)
        
    runner = BenchmarkRunner(data_dir)
    results = runner.run_ablation()
    
    report_path = os.path.join(os.path.dirname(__file__), "results", "ablation_report.md")
    generate_ablation_report(results, report_path)
    
if __name__ == "__main__":
    main()

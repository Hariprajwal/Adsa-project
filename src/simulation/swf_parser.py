"""
Standard Workload Format (.swf) Parser
Parses official 18-column SWF traces from the Parallel Workloads Archive:
- Ignores comments (lines starting with ';')
- Extracts metadata and computes summary statistics for journal Table 1
- Returns structured SWFJobRecord objects for simulation
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class SWFJobRecord:
    job_id: int
    submit_time: int
    wait_time: int
    run_time: int
    alloc_procs: int
    avg_cpu_time: int
    used_mem_kb: int
    req_procs: int
    req_time: int
    req_mem_kb: int
    status: int
    user_id: int
    group_id: int
    exe_id: int
    queue_id: int
    partition_id: int
    preceding_job_id: int
    think_time: int

class SWFParser:
    """
    Parser for Standard Workload Format (.swf) files.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.headers: Dict[str, str] = {}
        self.records: List[SWFJobRecord] = []
        self._parsed = False

    def parse(self) -> List[SWFJobRecord]:
        if self._parsed:
            return self.records
            
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"SWF trace file not found: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith(";"):
                    # Header comment
                    comment = line[1:].strip()
                    if ":" in comment:
                        key, val = comment.split(":", 1)
                        self.headers[key.strip()] = val.strip()
                    continue

                parts = line.split()
                if len(parts) < 18:
                    continue

                record = SWFJobRecord(
                    job_id=int(parts[0]),
                    submit_time=int(parts[1]),
                    wait_time=int(parts[2]),
                    run_time=int(parts[3]),
                    alloc_procs=int(parts[4]),
                    avg_cpu_time=int(parts[5]),
                    used_mem_kb=int(parts[6]),
                    req_procs=int(parts[7]),
                    req_time=int(parts[8]),
                    req_mem_kb=int(parts[9]),
                    status=int(parts[10]),
                    user_id=int(parts[11]),
                    group_id=int(parts[12]),
                    exe_id=int(parts[13]),
                    queue_id=int(parts[14]),
                    partition_id=int(parts[15]),
                    preceding_job_id=int(parts[16]),
                    think_time=int(parts[17])
                )
                self.records.append(record)

        self._parsed = True
        return self.records

    def get_statistics(self) -> Dict[str, Any]:
        """
        Computes the exact metrics required for Table 1 of the paper:
        - Trace Name
        - Total Recorded Jobs
        - Number of Nodes
        - Trace Duration (hours or timespan)
        - Mean Job Runtime (s)
        - Std Dev Runtime (s)
        """
        if not self._parsed:
            self.parse()

        if not self.records:
            return {
                "total_jobs": 0,
                "node_count": int(self.headers.get("MaxNodes", 0)),
                "trace_duration_s": 0,
                "mean_runtime_s": 0.0,
                "std_runtime_s": 0.0
            }

        total_jobs = len(self.records)
        runtimes = [r.run_time for r in self.records]
        mean_rt = sum(runtimes) / total_jobs
        variance_rt = sum((r - mean_rt) ** 2 for r in runtimes) / total_jobs
        std_rt = variance_rt ** 0.5
        
        start_t = min(r.submit_time for r in self.records)
        end_t = max(r.submit_time + r.run_time for r in self.records)
        duration_s = end_t - start_t
        
        node_count = int(self.headers.get("MaxNodes", 1024))

        return {
            "trace_name": os.path.basename(self.filepath),
            "system_name": self.headers.get("Computer", "Unknown HPC Cluster"),
            "total_jobs": total_jobs,
            "node_count": node_count,
            "trace_duration_s": duration_s,
            "trace_duration_hours": round(duration_s / 3600.0, 2),
            "mean_runtime_s": round(mean_rt, 2),
            "std_runtime_s": round(std_rt, 2)
        }

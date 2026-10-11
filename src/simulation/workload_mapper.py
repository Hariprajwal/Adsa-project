"""
Workload Mapper: Multi-Dimensional Resource Vector & Job Class Mapper
Translates raw SWF records from HPC traces into high-fidelity multi-dimensional Job instances
compatible with the Phase 1 Core DSA Engine (EntropyHierarchicalBalancer & Baselines).
"""

from typing import List, Optional
from src.core.balancer import Job, JobType
from .swf_parser import SWFJobRecord

class WorkloadMapper:
    """
    Transforms SWF trace records into multi-dimensional Jobs with normalized resource requirements.
    """
    def __init__(self, time_scale_factor: float = 1.0):
        """
        :param time_scale_factor: Scaling ratio for simulation duration (e.g. 0.05 or 0.1 for accelerated simulation).
        """
        self.time_scale_factor = time_scale_factor

    def map_record_to_job(self, record: SWFJobRecord) -> Job:
        # 1. Determine Job Type from resource signatures
        # Ratio of CPU time used to total wallclock time
        cpu_ratio = (record.avg_cpu_time / max(1, record.run_time)) if record.avg_cpu_time > 0 else 0.8
        mem_mb = record.used_mem_kb / 1024.0

        if cpu_ratio > 0.85 and record.alloc_procs >= 4:
            job_type = JobType.CPU_BOUND
            cpu_req = min(95.0, max(15.0, 20.0 + (record.alloc_procs * 4.0)))
            mem_req = min(50.0, max(10.0, mem_mb / 400.0))
            net_req = 10.0
            disk_req = 8.0
        elif mem_mb > 4096.0 or (record.req_mem_kb > 8388608):
            job_type = JobType.MEMORY_BOUND
            cpu_req = min(50.0, max(10.0, 15.0 + (record.alloc_procs * 2.0)))
            mem_req = min(90.0, max(30.0, mem_mb / 200.0))
            net_req = 15.0
            disk_req = 10.0
        elif record.run_time < 300 and record.alloc_procs >= 8:
            job_type = JobType.IO_BOUND
            cpu_req = 15.0
            mem_req = 15.0
            net_req = min(90.0, max(25.0, 20.0 + record.alloc_procs * 3.0))
            disk_req = min(80.0, max(20.0, 15.0 + record.alloc_procs * 2.5))
        else:
            job_type = JobType.BALANCED
            cpu_req = min(60.0, max(10.0, 15.0 + record.alloc_procs * 2.5))
            mem_req = min(50.0, max(10.0, mem_mb / 300.0))
            net_req = 15.0
            disk_req = 12.0

        # Predictability: Long-running jobs (> 1000s in trace) are predictable HPC batches;
        # Short bursty interactive jobs (< 180s) are volatile/bursty.
        is_predictable = (record.run_time >= 600)

        # Scale runtime for discrete-event simulator efficiency
        scaled_duration = max(1.0, float(record.run_time) * self.time_scale_factor)
        scaled_submit = float(record.submit_time) * self.time_scale_factor

        return Job(
            job_id=f"job_{record.job_id}",
            job_type=job_type,
            cpu_req=round(cpu_req, 2),
            mem_req=round(mem_req, 2),
            net_req=round(net_req, 2),
            disk_req=round(disk_req, 2),
            duration=round(scaled_duration, 2),
            is_predictable=is_predictable,
            submit_time=round(scaled_submit, 2)
        )

    def map_records(self, records: List[SWFJobRecord], max_jobs: Optional[int] = None) -> List[Job]:
        selected = records if max_jobs is None else records[:max_jobs]
        return [self.map_record_to_job(r) for r in selected]

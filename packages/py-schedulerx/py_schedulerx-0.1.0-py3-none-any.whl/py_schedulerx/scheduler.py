import time
from typing import List, Callable, Any
from .job import Job


class Scheduler:
    
    def __init__(self):
        self.jobs: List[Job] = []
        self._running = False
    
    def every(self, interval: str, threaded: bool = False) -> Callable:
        def decorator(func: Callable) -> Callable:
            job = Job(func, interval, threaded)
            self.jobs.append(job)
            return func
        return decorator
    
    def add_job(self, func: Callable, interval: str, threaded: bool = False) -> Job:
        job = Job(func, interval, threaded)
        self.jobs.append(job)
        return job
    
    def remove_job(self, func: Callable) -> bool:
        for i, job in enumerate(self.jobs):
            if job.func == func:
                del self.jobs[i]
                return True
        return False
    
    def clear_jobs(self) -> None:
        self.jobs.clear()
    
    def run_pending(self) -> None:
        for job in self.jobs:
            if job.should_run():
                job.run()
    
    def run_forever(self, sleep_interval: float = 1.0) -> None:
        self._running = True
        
        try:
            while self._running:
                self.run_pending()
                time.sleep(sleep_interval)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self) -> None:
        self._running = False
    
    def get_jobs(self) -> List[Job]:
        return self.jobs.copy()
    
    def next_run_time(self) -> float:
        if not self.jobs:
            return float('inf')
        return min(job.next_run for job in self.jobs)
    
    def __len__(self) -> int:
        return len(self.jobs)

from .scheduler import Scheduler
from .job import Job
from .interval import IntervalParser
from .utils import format_duration, validate_interval

__version__ = "0.1.0"
__author__ = "firatmio"
__description__ = "A lightweight and simple task scheduler for Python"

_default_scheduler = Scheduler()

every = _default_scheduler.every
add_job = _default_scheduler.add_job
remove_job = _default_scheduler.remove_job
clear_jobs = _default_scheduler.clear_jobs
run_pending = _default_scheduler.run_pending
run_forever = _default_scheduler.run_forever
stop = _default_scheduler.stop
get_jobs = _default_scheduler.get_jobs
next_run_time = _default_scheduler.next_run_time

__all__ = [
    "Scheduler",
    "Job", 
    "IntervalParser",
    "every",
    "add_job",
    "remove_job", 
    "clear_jobs",
    "run_pending",
    "run_forever",
    "stop",
    "get_jobs",
    "next_run_time",
    "format_duration",
    "validate_interval",
]

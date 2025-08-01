import time
import threading
from typing import Callable, Any, Optional
from .interval import IntervalParser


class Job:
    
    def __init__(self, func: Callable, interval: str, threaded: bool = False):
        self.func = func
        self.interval_seconds = IntervalParser.parse(interval)
        self.threaded = threaded
        self.last_run = 0
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
    
    def should_run(self) -> bool:
        return time.time() - self.last_run >= self.interval_seconds
    
    def run(self) -> Any:
        if self.is_running and self.threaded:
            return None
        
        if self.threaded:
            self._thread = threading.Thread(target=self._execute)
            self._thread.daemon = True
            self._thread.start()
        else:
            return self._execute()
    
    def _execute(self) -> Any:
        self.is_running = True
        self.last_run = time.time()
        
        try:
            result = self.func()
            return result
        except Exception as e:
            self._handle_error(e)
        finally:
            self.is_running = False
    
    def _handle_error(self, error: Exception) -> None:
        import sys
        print(f"Error in job {self.func.__name__}: {error}", file=sys.stderr)
    
    @property
    def next_run(self) -> float:
        return self.last_run + self.interval_seconds
    
    def __repr__(self) -> str:
        return f"Job(func={self.func.__name__}, interval={self.interval_seconds}s, threaded={self.threaded})"

import unittest
import time
from unittest.mock import Mock
from py_schedulerx.scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    
    def setUp(self):
        self.scheduler = Scheduler()
    
    def test_scheduler_creation(self):
        self.assertEqual(len(self.scheduler), 0)
        self.assertFalse(self.scheduler._running)
    
    def test_add_job_decorator(self):
        @self.scheduler.every("30s")
        def test_func():
            return "test"
        
        self.assertEqual(len(self.scheduler), 1)
        job = self.scheduler.jobs[0]
        self.assertEqual(job.func, test_func)
        self.assertEqual(job.interval_seconds, 30.0)
    
    def test_add_job_method(self):
        func = Mock()
        job = self.scheduler.add_job(func, "1m", threaded=True)
        
        self.assertEqual(len(self.scheduler), 1)
        self.assertEqual(job.func, func)
        self.assertEqual(job.interval_seconds, 60.0)
        self.assertTrue(job.threaded)
    
    def test_remove_job(self):
        func = Mock()
        self.scheduler.add_job(func, "30s")
        
        self.assertEqual(len(self.scheduler), 1)
        
        removed = self.scheduler.remove_job(func)
        self.assertTrue(removed)
        self.assertEqual(len(self.scheduler), 0)
    
    def test_remove_nonexistent_job(self):
        func = Mock()
        removed = self.scheduler.remove_job(func)
        self.assertFalse(removed)
    
    def test_clear_jobs(self):
        self.scheduler.add_job(Mock(), "30s")
        self.scheduler.add_job(Mock(), "1m")
        
        self.assertEqual(len(self.scheduler), 2)
        
        self.scheduler.clear_jobs()
        self.assertEqual(len(self.scheduler), 0)
    
    def test_run_pending(self):
        func = Mock()
        self.scheduler.add_job(func, "0.1s")
        
        time.sleep(0.2)
        self.scheduler.run_pending()
        
        func.assert_called_once()
    
    def test_get_jobs(self):
        func1 = Mock()
        func2 = Mock()
        
        self.scheduler.add_job(func1, "30s")
        self.scheduler.add_job(func2, "1m")
        
        jobs = self.scheduler.get_jobs()
        self.assertEqual(len(jobs), 2)
        self.assertIsNot(jobs, self.scheduler.jobs)
    
    def test_next_run_time_empty(self):
        next_run = self.scheduler.next_run_time()
        self.assertEqual(next_run, float('inf'))
    
    def test_next_run_time_with_jobs(self):
        func = Mock()
        self.scheduler.add_job(func, "30s")
        
        next_run = self.scheduler.next_run_time()
        self.assertIsInstance(next_run, float)
        self.assertGreater(next_run, time.time())


if __name__ == "__main__":
    unittest.main()

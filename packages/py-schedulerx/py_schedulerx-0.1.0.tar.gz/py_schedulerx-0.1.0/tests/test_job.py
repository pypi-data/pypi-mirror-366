import unittest
import time
from unittest.mock import Mock
from py_schedulerx.job import Job


class TestJob(unittest.TestCase):
    
    def test_job_creation(self):
        func = Mock()
        job = Job(func, "30s", threaded=False)
        
        self.assertEqual(job.func, func)
        self.assertEqual(job.interval_seconds, 30.0)
        self.assertEqual(job.threaded, False)
        self.assertFalse(job.is_running)
    
    def test_should_run_initially(self):
        func = Mock()
        job = Job(func, "1s")
        
        self.assertTrue(job.should_run())
    
    def test_should_not_run_immediately_after_run(self):
        func = Mock()
        job = Job(func, "10s")
        
        job.run()
        self.assertFalse(job.should_run())
    
    def test_should_run_after_interval(self):
        func = Mock()
        job = Job(func, "0.1s")
        
        job.run()
        time.sleep(0.2)
        self.assertTrue(job.should_run())
    
    def test_function_execution(self):
        func = Mock(return_value="test_result")
        job = Job(func, "1s")
        
        result = job.run()
        func.assert_called_once()
        self.assertEqual(result, "test_result")
    
    def test_next_run_time(self):
        func = Mock()
        job = Job(func, "30s")
        
        before_run = time.time()
        job.run()
        after_run = time.time()
        
        expected_next = job.last_run + 30
        self.assertAlmostEqual(job.next_run, expected_next, delta=1)
    
    def test_error_handling(self):
        def failing_func():
            raise ValueError("Test error")
        
        job = Job(failing_func, "1s")
        
        result = job.run()
        self.assertIsNone(result)
        self.assertFalse(job.is_running)


if __name__ == "__main__":
    unittest.main()

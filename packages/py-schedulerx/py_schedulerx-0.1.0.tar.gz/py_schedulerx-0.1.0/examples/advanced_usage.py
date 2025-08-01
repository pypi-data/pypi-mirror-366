import py_schedulerx as schedule
from py_schedulerx import Scheduler
import time


def custom_error_handler():
    print("This function will raise an error!")
    raise ValueError("Intentional error for demonstration")


def healthy_task():
    print(f"Healthy task running at {time.strftime('%H:%M:%S')}")


def main():
    print("=== Advanced Usage Example ===")
    
    scheduler = Scheduler()
    
    scheduler.add_job(healthy_task, "3s")
    scheduler.add_job(custom_error_handler, "5s")
    
    @scheduler.every("7s", threaded=True)
    def threaded_task():
        print("Threaded task is running in background")
        time.sleep(2)
        print("Threaded task completed")
    
    print(f"Total jobs scheduled: {len(scheduler)}")
    print("Jobs info:")
    for i, job in enumerate(scheduler.get_jobs(), 1):
        print(f"  {i}. {job}")
    
    print(f"\nNext run time: {time.ctime(scheduler.next_run_time())}")
    
    print("\nStarting scheduler with custom instance...")
    print("Notice how errors don't stop the scheduler")
    print("Press Ctrl+C to stop")
    
    try:
        scheduler.run_forever()
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped gracefully.")


def demonstrate_utilities():
    from py_schedulerx import format_duration, validate_interval
    
    print("\n=== Utility Functions Demo ===")
    
    durations = [30, 300, 3600, 86400, 604800]
    for duration in durations:
        formatted = format_duration(duration)
        print(f"{duration} seconds = {formatted}")
    
    intervals = ["30s", "5m", "2h", "1d", "invalid", ""]
    print("\nInterval validation:")
    for interval in intervals:
        is_valid = validate_interval(interval)
        print(f"'{interval}' -> {'Valid' if is_valid else 'Invalid'}")


if __name__ == "__main__":
    main()
    demonstrate_utilities()

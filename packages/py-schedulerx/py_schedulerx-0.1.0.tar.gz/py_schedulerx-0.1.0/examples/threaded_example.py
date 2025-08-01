import py_schedulerx as schedule
import time
import threading


@schedule.every("3s", threaded=True)
def background_task():
    print(f"[{threading.current_thread().name}] Background task started")
    time.sleep(5)
    print(f"[{threading.current_thread().name}] Background task completed")


@schedule.every("2s")
def quick_task():
    print(f"[{threading.current_thread().name}] Quick task executed")


@schedule.every("10s", threaded=True)
def heavy_computation():
    print(f"[{threading.current_thread().name}] Heavy computation started")
    total = sum(i * i for i in range(1000000))
    print(f"[{threading.current_thread().name}] Heavy computation done: {total}")


if __name__ == "__main__":
    print("Starting threaded scheduler...")
    print("Notice how background tasks don't block quick tasks")
    print("Press Ctrl+C to stop")
    
    try:
        schedule.run_forever()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")

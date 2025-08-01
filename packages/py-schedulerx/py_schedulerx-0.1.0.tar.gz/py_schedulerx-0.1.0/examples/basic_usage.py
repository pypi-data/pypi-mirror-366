import py_schedulerx as schedule
import time


@schedule.every("5s")
def say_hello():
    print(f"Hello! Current time: {time.strftime('%H:%M:%S')}")


@schedule.every("10s")
def fetch_data():
    print("Fetching data from API...")


@schedule.every("1m")
def log_status():
    print("System status: OK")


if __name__ == "__main__":
    print("Starting scheduler...")
    print("Press Ctrl+C to stop")
    
    try:
        schedule.run_forever()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")

import os
import time
import multiprocessing
from homebot.app import app
from homebot.tasks import (
    collect_mikrotik_leases,
    collect_shelly_metrics,
    collect_hikvision_data,
    collect_weather,
    process_data
)

def run_api():
    """Runs the Flask API."""
    app.run(host='0.0.0.0', port=5000, debug=False)

def run_scheduler(task_func, interval, *args, **kwargs):
    """Generic loop for running a task at a set interval."""
    # Run immediately on startup
    task_func(*args, **kwargs)
    
    while True:
        time.sleep(interval)
        task_func(*args, **kwargs)

if __name__ == '__main__':
    # Load Intervals
    SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL_SECONDS", 600))
    SHELLY_INTERVAL = int(os.getenv("SHELLY_POLL_INTERVAL_SECONDS", 60))
    HIK_CONFIG_INTERVAL = int(os.getenv("HIKVISION_CONFIG_INTERVAL_SECONDS", 3600))
    HIK_SHOT_INTERVAL = int(os.getenv("HIKVISION_SCREENSHOT_INTERVAL_SECONDS", 300))
    WEATHER_INTERVAL = int(os.getenv("WEATHER_SYNC_INTERVAL_SECONDS", 1800))

    processes = []

    # 1. API Server
    p_api = multiprocessing.Process(target=run_api, name="API_Server")
    processes.append(p_api)

    # 2. Mikrotik Lease Sync (Inventory)
    # Also triggers data processing after sync usually, or we run processing separately.
    # Let's chain them: Sync -> Process
    def sync_and_process():
        collect_mikrotik_leases()
        process_data()

    p_sync = multiprocessing.Process(
        target=run_scheduler, 
        args=(sync_and_process, SYNC_INTERVAL),
        name="Mikrotik_Sync"
    )
    processes.append(p_sync)

    # 3. Shelly Polling
    p_shelly = multiprocessing.Process(
        target=run_scheduler,
        args=(collect_shelly_metrics, SHELLY_INTERVAL),
        name="Shelly_Poller"
    )
    processes.append(p_shelly)

    # 4. HikVision Config
    p_hik_conf = multiprocessing.Process(
        target=run_scheduler,
        args=(collect_hikvision_data, HIK_CONFIG_INTERVAL, True), # True for config_only
        name="Hik_Config"
    )
    processes.append(p_hik_conf)

    # 5. HikVision Screenshots
    p_hik_shot = multiprocessing.Process(
        target=run_scheduler,
        args=(collect_hikvision_data, HIK_SHOT_INTERVAL, False), # False for screenshots
        name="Hik_Screenshots"
    )
    processes.append(p_hik_shot)

    # 6. Weather Sync
    p_weather = multiprocessing.Process(
        target=run_scheduler,
        args=(collect_weather, WEATHER_INTERVAL),
        name="Weather_Sync"
    )
    processes.append(p_weather)

    # Start all processes
    print("Starting HomeBot Services...")
    for p in processes:
        p.start()
        print(f"Started {p.name} (PID: {p.pid})")

    # Keep main process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        for p in processes:
            p.terminate()
            p.join()
        print("All services stopped.")

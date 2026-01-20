import os
import json
import time
import pandas as pd
import duckdb
from datetime import datetime
import re
from services.mikrotik import MikroTikService
from services.hikvision import HikVisionService
from services.weather import WeatherService
from services.geoip import GeoIPService

# Configuration
PARQUET_DIR = "data"
DB_NAME = "network.db"

# Service Initialization
mt_service = MikroTikService(
    os.getenv("MIKROTIK_HOST", "10.10.100.1"),
    os.getenv("MIKROTIK_USER", "homebot"),
    os.getenv("MIKROTIK_PASSWORD", "homebot!2025!")
)

hik_service = HikVisionService(
    os.getenv("HIK_VISION_USER", "homebot"),
    os.getenv("HIK_VISION_PASS", "homebot!2025!")
)

weather_service = WeatherService()
geoip_service = GeoIPService()

# Helper to load latest leases for inventory
def _get_latest_leases():
    try:
        lease_path = f"{PARQUET_DIR}/leases_latest.parquet"
        if os.path.exists(lease_path):
            return pd.read_parquet(lease_path)
    except Exception as e:
        print(f"Error reading latest leases: {e}")
    return pd.DataFrame()

def _save_parquet(data, prefix, timestamp, save_latest=False):
    """Helper to save list of dicts to parquet"""
    if not data:
        return
    try:
        df = pd.DataFrame(data)
        os.makedirs(PARQUET_DIR, exist_ok=True)
        filename = f"{PARQUET_DIR}/{prefix}_{timestamp}.parquet"
        df.to_parquet(filename, engine='pyarrow', index=False)
        if save_latest:
             df.to_parquet(f"{PARQUET_DIR}/{prefix}_latest.parquet", engine='pyarrow', index=False)
    except Exception as e:
        print(f"Error saving {prefix}: {e}")

def collect_mikrotik_data():
    """Fetches comprehensive Mikrotik data and saves to Parquet."""
    print(f"[{datetime.now()}] Starting Mikrotik Data Sync...")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # 1. DHCP Leases (Inventory Base)
        leases = mt_service.get_dhcp_leases()
        _save_parquet(leases, "leases", ts, save_latest=True)
        print(f"[{datetime.now()}] Leases saved.")

        # 2. Kid Control
        try:
            kid_devs = mt_service.get_kid_control_devices()
            _save_parquet(kid_devs, "mikrotik_kid_control", ts)
        except Exception as e:
             print(f"Error fetching Kid Control: {e}")

        # 3. Active Services
        try:
            services = mt_service.get_active_services()
            _save_parquet(services, "mikrotik_services", ts)
        except Exception as e:
             print(f"Error fetching Active Services: {e}")

        # 4. Wireless Registrations
        try:
            wifi = mt_service.get_wireless_registrations()
            _save_parquet(wifi, "mikrotik_wifi", ts)
        except Exception as e:
             print(f"Error fetching WiFi Regs: {e}")

        # 5. ARP Table
        try:
            arp = mt_service.get_arp_table()
            _save_parquet(arp, "mikrotik_arp", ts)
        except Exception as e:
             print(f"Error fetching ARP: {e}")

        # 6. Firewall Data
        try:
            fw_data = mt_service.get_firewall_rules()
            # Save each table separately
            _save_parquet(fw_data.get('filter'), "mikrotik_fw_filter", ts)
            _save_parquet(fw_data.get('nat'), "mikrotik_fw_nat", ts)
            _save_parquet(fw_data.get('mangle'), "mikrotik_fw_mangle", ts)
            _save_parquet(fw_data.get('connections'), "mikrotik_fw_conns", ts)
        except Exception as e:
             print(f"Error fetching Firewall Data: {e}")

        print(f"[{datetime.now()}] Mikrotik Sync Complete.")

    except Exception as e:
        print(f"[{datetime.now()}] Critical Error in Mikrotik Sync: {e}")

def collect_shelly_metrics():
    """Polls Shelly devices found in inventory."""
    print(f"[{datetime.now()}] Starting Shelly Polling...")
    try:
        df_leases = _get_latest_leases()
        if df_leases.empty:
            print("No leases found. Skipping Shelly poll.")
            return

        # Simple filter for Shelly devices based on hostname
        shelly_devices = df_leases[df_leases['host-name'].fillna('').str.lower().str.startswith('shelly')]
        
        results = []
        scan_time = datetime.now()
        
        # Inline probe function to avoid circular imports or redefining
        def _probe(ip):
            import requests
            try:
                res = requests.get(f"http://{ip}/rpc/Shelly.GetStatus", timeout=2)
                if res.status_code == 200: return {"gen": 2, "data": res.json()}
            except: pass
            try:
                res = requests.get(f"http://{ip}/status", timeout=2)
                if res.status_code == 200: return {"gen": 1, "data": res.json()}
            except: pass
            return None

        for _, row in shelly_devices.iterrows():
            ip = row.get('address')
            hostname = row.get('host-name')
            if ip:
                info = _probe(ip)
                if info:
                    results.append({
                        "scanned_at": scan_time,
                        "ip": ip,
                        "hostname": hostname,
                        "gen": info["gen"],
                        "raw_status": json.dumps(info["data"])
                    })

        if results:
            df_shelly = pd.DataFrame(results)
            # Append to a daily file or time-partitioned file
            date_str = datetime.now().strftime("%Y%m%d")
            # We use a unique filename per batch to avoid file lock issues if multiple writers
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{PARQUET_DIR}/shelly_metrics_{date_str}_{timestamp}.parquet"
            df_shelly.to_parquet(filename, engine='pyarrow', index=False)
            print(f"[{datetime.now()}] Shelly Polling Complete. {len(results)} devices scanned.")
        else:
            print(f"[{datetime.now()}] Shelly Polling Complete. No devices reachable.")

    except Exception as e:
        print(f"[{datetime.now()}] Error in Shelly Polling: {e}")

def collect_hikvision_data(config_only=False):
    """Fetches HikVision config and/or screenshots."""
    task_name = "HikVision Config" if config_only else "HikVision Screenshots"
    print(f"[{datetime.now()}] Starting {task_name}...")
    try:
        df_leases = _get_latest_leases()
        if df_leases.empty: return

        ptr_pattern = os.getenv("HIK_VISION_PTR", "cam[0-9].lan")
        
        targets = []
        for _, row in df_leases.iterrows():
            hostname = row.get('host-name', '')
            ip = row.get('address')
            if hostname and ip and re.search(ptr_pattern, hostname):
                targets.append(ip)

        if not targets:
            print(f"No HikVision devices found matching {ptr_pattern}.")
            return

        if config_only:
            count = hik_service.get_config(targets)
            print(f"[{datetime.now()}] HikVision Config Complete. {count} configs saved.")
        else:
            # Screenshots
            for ip in targets:
                path = hik_service.get_screenshot(ip)
                if path:
                    print(f"Screenshot saved: {path}")
            print(f"[{datetime.now()}] HikVision Screenshots Complete.")

    except Exception as e:
        print(f"[{datetime.now()}] Error in {task_name}: {e}")

def collect_weather():
    """Fetches weather data."""
    print(f"[{datetime.now()}] Starting Weather Sync...")
    try:
        city = os.getenv("WEATHER_CITY", "London")
        data = weather_service.get_weather(city)
        if "error" not in data:
            df = pd.DataFrame([data])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            df.to_parquet(f"{PARQUET_DIR}/weather_{timestamp}.parquet", engine='pyarrow', index=False)
            print(f"[{datetime.now()}] Weather Sync Complete for {city}.")
        else:
            print(f"[{datetime.now()}] Weather Sync Failed: {data['error']}")
    except Exception as e:
        print(f"[{datetime.now()}] Error in Weather Sync: {e}")

def process_data():
    """Loads parquet into DuckDB and runs DBT/SQL."""
    print(f"[{datetime.now()}] Starting Data Processing...")
    try:
        con = duckdb.connect(DB_NAME)
        
        # 1. Update Leases
        if os.path.exists(f"{PARQUET_DIR}/leases_latest.parquet"):
            con.execute(f"CREATE OR REPLACE TABLE raw_leases AS SELECT * FROM read_parquet('{PARQUET_DIR}/leases_latest.parquet')")
        
        # 2. Update Shelly Data (Example: Load all today's files)
        date_str = datetime.now().strftime("%Y%m%d")
        shelly_files = f"{PARQUET_DIR}/shelly_metrics_{date_str}_*.parquet"
        try:
            con.execute(f"CREATE TABLE IF NOT EXISTS raw_shelly_data AS SELECT * FROM read_parquet('{shelly_files}') WHERE 1=0")
            con.execute(f"INSERT INTO raw_shelly_data SELECT * FROM read_parquet('{shelly_files}')")
        except:
            pass # No files yet

        con.close()
        print(f"[{datetime.now()}] Data Processing Complete.")
    except Exception as e:
        print(f"[{datetime.now()}] Error in Data Processing: {e}")
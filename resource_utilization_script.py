import os
import requests
import psutil
import time
import statistics
import threading

GROCY_URL = "http://localhost:8000/api"
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "GROCY-API-KEY": API_KEY,
    "Accept": "application/json"
}

ENDPOINTS = [
    "/objects/products",
    "/stock",
    "/chores",
    "/tasks",
]

def get_php_process():
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            name = proc.info['name'].lower()
            cmdline = " ".join(proc.info['cmdline'] or []).lower()
            if 'php' in name and ('localhost' in cmdline or '8000' in cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

def get_php_memory_mb(proc):
    try:
        total = proc.memory_info().rss
        for child in proc.children(recursive=True):
            try:
                total += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return total / (1024 * 1024)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0

php_proc = get_php_process()
if not php_proc:
    print("ERROR: PHP process not found.")
    exit(1)

# Warm up the cpu_percent call — first call always returns 0.0
php_proc.cpu_percent(interval=None)
time.sleep(0.5)

print(f"Found PHP process: PID {php_proc.pid}\n")

cpu_peaks = []
ram_peaks = []

for i in range(100):
    endpoint = ENDPOINTS[i % len(ENDPOINTS)]
    url = GROCY_URL + endpoint

    # Collect CPU samples in background thread during the request
    cpu_samples = []
    stop_sampling = threading.Event()

    def sample_cpu():
        while not stop_sampling.is_set():
            try:
                sample = php_proc.cpu_percent(interval=0.05)
                if sample > 0:
                    cpu_samples.append(sample)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

    sampler = threading.Thread(target=sample_cpu, daemon=True)
    sampler.start()

    ram_before = get_php_memory_mb(php_proc)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"Request {i+1} failed: {e}")
        stop_sampling.set()
        continue

    ram_after = get_php_memory_mb(php_proc)
    stop_sampling.set()
    sampler.join()

    peak_cpu = max(cpu_samples) if cpu_samples else 0.0
    peak_ram = max(ram_before, ram_after)

    cpu_peaks.append(peak_cpu)
    ram_peaks.append(peak_ram)

    print(f"Request {i+1}: {endpoint} | CPU: {peak_cpu:.1f}% | RAM: {peak_ram:.1f} MB | Status: {response.status_code}")
    time.sleep(0.1)

print("\n--- RESULTS ---")
print(f"Peak CPU across all requests:  {max(cpu_peaks):.1f}%")
print(f"Average peak CPU:              {statistics.mean(cpu_peaks):.1f}%")
print(f"Peak RAM across all requests:  {max(ram_peaks):.1f} MB")
print(f"Average peak RAM:              {statistics.mean(ram_peaks):.1f} MB")
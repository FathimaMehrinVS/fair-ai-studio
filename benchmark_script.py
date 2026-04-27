import time
import requests

def benchmark_endpoint(url, name):
    print(f"Benchmarking {name}...")
    start = time.time()
    try:
        response = requests.get(url)
        end = time.time()
        print(f"  Status: {response.status_code}")
        print(f"  Time: {end - start:.4f}s")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    # Give the server a moment to start
    time.sleep(2)
    benchmark_endpoint("http://localhost:8000/api/charts/distributions", "Distributions Chart")
    benchmark_endpoint("http://localhost:8000/api/summary", "Summary API")
    benchmark_endpoint("http://localhost:8000/api/charts/gauges", "Gauges API")

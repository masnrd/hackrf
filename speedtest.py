import subprocess
import json

def run_speedtest():
    # Run speedtest-cli with JSON output
    result = subprocess.run(['speedtest-cli', '--json'], capture_output=True, text=True)
    
    # Parse the JSON result
    speedtest_result = json.loads(result.stdout)
    
    # Extract and return relevant metrics
    download_speed = speedtest_result['download'] / 1e6  # Convert to Mbps
    upload_speed = speedtest_result['upload'] / 1e6  # Convert to Mbps
    latency = speedtest_result['ping']
    
    return download_speed, upload_speed, latency

download, upload, latency = run_speedtest()
print(f"Download Speed: {download} Mbps")
print(f"Upload Speed: {upload} Mbps")
print(f"Latency: {latency} ms")

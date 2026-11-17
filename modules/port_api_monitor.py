import socket
import requests

def check_ports_and_api(host, ports, url):
    port_results = {}
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            port_results[port] = "OPEN" if sock.connect_ex((host, port)) == 0 else "CLOSED"

    try:
        resp = requests.get(url, timeout=5)
        api_status = {"url": url, "http_code": resp.status_code, "latency_ms": round(resp.elapsed.total_seconds() * 1000, 2)}
    except Exception as e:
        api_status = {"url": url, "error": str(e)}

    return {"host": host, "ports": port_results, "api": api_status}

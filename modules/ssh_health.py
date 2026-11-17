import paramiko

def check_ssh_health(host, user, key_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    commands = {
        "uptime_load": "uptime | awk -F'load average:' '{print $2}'",
        "memory_pct": "free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'",
        "disk_pct": "df -h / | awk 'NR==2{print $5}'",
        "docker_running": "docker ps --format '{{.Names}}: {{.Status}}' | tr '\n' '; '"
    }
    report = {"host": host, "status": "REACHABLE", "metrics": {}}
    try:
        client.connect(hostname=host, username=user, key_filename=key_path, timeout=10)
        for key, cmd in commands.items():
            _, stdout, _ = client.exec_command(cmd)
            report["metrics"][key] = stdout.read().decode().strip()
    except Exception as e:
        report["status"] = f"UNREACHABLE ({e})"
    finally:
        client.close()
    return report

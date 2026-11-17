# Python Server & AWS Infrastructure Automation Toolkit

A modular, config-driven Python CLI toolkit for automating routine Linux server health checks, TCP port and HTTP endpoint monitoring, log error analysis, and AWS EC2/S3 operational tasks.

Built to monitor live Ubuntu EC2 instances running containerized web applications behind an Nginx reverse proxy without heavy monitoring agent overhead.

---

## Features

- **Remote SSH Server Health Checks (`paramiko`):** Connects to Ubuntu hosts via SSH key authentication to gather uptime/CPU load averages, memory usage, root disk utilization, and active Docker container statuses.
- **TCP Port & API Endpoint Monitoring (`socket`, `requests`):** Verifies open/closed TCP ports (e.g., confirming port `80` is publicly reachable while internal application ports like `5000` remain firewalled) and measures HTTP response codes and latency.
- **System & Nginx Log Analyzer (`re`):** Scans `/var/log` system and web server logs for recurring error patterns (`ERROR`, `CRITICAL`, `502 Bad Gateway`, `504 Gateway`, `Failed password`) and outputs structured JSON summaries.
- **AWS EC2 Inventory & S3 Log Backups (`boto3`):** Queries live EC2 instance metadata and attached Security Groups, and archives diagnostic logs into compressed `.tar.gz` bundles uploaded directly to Amazon S3.
- **Cron-Ready Automation:** Designed to run unattended via Linux `cron` jobs for scheduled health checks and daily S3 log backups.

---

## Project Structure

```text
python-aws-infra-toolkit/
├── cli.py                     # Unified CLI entrypoint using argparse
├── config/
│   ├── hosts.example.json     # Configuration template for target servers & AWS
│   └── hosts.json             # Local runtime config (ignored by Git)
├── modules/
│   ├── __init__.py
│   ├── ssh_health.py          # Remote SSH system & Docker health checks
│   ├── port_api_monitor.py    # TCP socket scanner & HTTP health checker
│   ├── log_analyzer.py        # Regex log parser with JSON summary output
│   └── aws_ops.py             # Boto3 EC2 inventory & S3 archive uploader
├── logs/                      # Generated diagnostic reports
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.8+
- AWS CLI configured (`aws configure`) or an IAM Role attached to the host with permissions for `ec2:DescribeInstances` and `s3:PutObject`
- SSH private key (`.pem`) with `chmod 400` permissions for target Linux servers

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vaishchava/python-aws-infra-toolkit.git
   cd python-aws-infra-toolkit
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure target hosts and AWS settings:**
   ```bash
   cp config/hosts.example.json config/hosts.json
   ```
   Update `config/hosts.json` with your server IP, SSH user, `.pem` key path, target ports, and S3 bucket name:
   ```json
   {
     "servers": [
       {
         "name": "web-server-ec2",
         "host": "3.110.121.4",
         "user": "ubuntu",
         "key_path": "/home/ubuntu/.ssh/your-key.pem",
         "ports": [22, 80, 5000],
         "health_url": "http://3.110.121.4/"
       }
     ],
     "aws": {
       "region": "ap-south-1",
       "s3_bucket": "your-s3-backup-bucket"
     }
   }
   ```

---

## Usage

Run any module via `cli.py`:

### 1. Remote SSH Server Health Check
```bash
python cli.py --task health
```

### 2. TCP Port & HTTP Endpoint Verification
```bash
python cli.py --task ports
```
**Sample Output:**
```json
{
  "host": "3.110.121.4",
  "ports": {
    "22": "OPEN",
    "80": "OPEN",
    "5000": "CLOSED"
  },
  "api": {
    "url": "http://3.110.121.4/",
    "http_code": 200,
    "latency_ms": 61.52
  }
}
```

### 3. Log File Error Analysis
```bash
python cli.py --task logs --logfile /var/log/syslog
```

### 4. AWS EC2 & Security Group Inventory
```bash
python cli.py --task aws-inventory
```

### 5. Compress & Upload Logs to Amazon S3
```bash
python cli.py --task s3-backup
```

---

## Automating with Cron

To schedule automated checks every 15 minutes and daily S3 log backups at midnight, add the following entries via `crontab -e`:

```cron
# Check SSH health every 15 minutes
*/15 * * * * cd /home/ubuntu/python-aws-infra-toolkit && ./venv/bin/python cli.py --task health >> logs/health.log 2>&1

# Archive and upload diagnostic logs to S3 daily at 00:00
0 0 * * * cd /home/ubuntu/python-aws-infra-toolkit && ./venv/bin/python cli.py --task s3-backup >> logs/backup.log 2>&1
```

---

## Security Practices

- Private keys (`*.pem`), environment variables (`.env`), and active host configurations (`config/hosts.json`) are excluded via `.gitignore`.
- AWS API calls rely on standard IAM credential chains (`~/.aws/credentials` or EC2 Instance Profiles) rather than hardcoded access keys.
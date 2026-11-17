import argparse
import json
from modules.ssh_health import check_ssh_health
from modules.port_api_monitor import check_ports_and_api
from modules.log_analyzer import analyze_log_file
from modules.aws_ops import get_ec2_inventory, backup_logs_to_s3

with open("config/hosts.json") as f:
    CONFIG = json.load(f)

parser = argparse.ArgumentParser(description="Python Server & AWS Infrastructure Automation Toolkit")
parser.add_argument("--task", required=True, choices=["health", "ports", "logs", "aws-inventory", "s3-backup"])
parser.add_argument("--logfile", default="/var/log/syslog", help="Path to log file for analysis")
args = parser.parse_args()

if args.task == "health":
    for srv in CONFIG["servers"]:
        print(json.dumps(check_ssh_health(srv["host"], srv["user"], srv["key_path"]), indent=2))
elif args.task == "ports":
    for srv in CONFIG["servers"]:
        print(json.dumps(check_ports_and_api(srv["host"], srv["ports"], srv["health_url"]), indent=2))
elif args.task == "logs":
    print(json.dumps(analyze_log_file(args.logfile), indent=2))
elif args.task == "aws-inventory":
    print(json.dumps(get_ec2_inventory(CONFIG["aws"]["region"]), indent=2))
elif args.task == "s3-backup":
    uri = backup_logs_to_s3("logs", CONFIG["aws"]["s3_bucket"], CONFIG["aws"]["region"])
    print(f"Uploaded backup to {uri}")

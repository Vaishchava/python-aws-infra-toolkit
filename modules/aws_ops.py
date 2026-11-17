import boto3
import tarfile
import os
from datetime import datetime

def get_ec2_inventory(region):
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances()
    instances = []
    for res in response["Reservations"]:
        for inst in res["Instances"]:
            instances.append({
                "id": inst["InstanceId"],
                "type": inst["InstanceType"],
                "state": inst["State"]["Name"],
                "public_ip": inst.get("PublicIpAddress", "N/A"),
                "security_groups": [sg["GroupName"] for sg in inst.get("SecurityGroups", [])]
            })
    return instances

def backup_logs_to_s3(log_dir, bucket_name, region):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_name = f"/tmp/infra_logs_{timestamp}.tar.gz"
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(log_dir, arcname=os.path.basename(log_dir))

    s3 = boto3.client("s3", region_name=region)
    s3_key = f"backups/infra_logs_{timestamp}.tar.gz"
    s3.upload_file(archive_name, bucket_name, s3_key)
    os.remove(archive_name)
    return f"s3://{bucket_name}/{s3_key}"

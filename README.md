# CartWatch 
Real-time cart abandonment detection on AWS — when a user drops off, an alert hits your inbox in seconds.

## How it works
```
Python Simulator → Kinesis → Lambda → SNS (email alert)
                                    → S3 (event log)
```
Built with: **AWS Kinesis · Lambda · SNS · S3 · Terraform · Kubernetes · GitHub Actions**

## What's interesting

- All AWS infrastructure provisioned with **Terraform** (one `terraform apply` to spin up everything)
- Lambda auto-deployed via **GitHub Actions** on every push to `lambda/`
- Status API containerized and running on a local **Kubernetes** cluster (kind)
- Zero manual AWS console clicks after initial setup

## Run it

```bash
# 1. Provision infrastructure
cd terraform && terraform init && terraform apply

# 2. Stream events
python3 simulator/simulate_events.py

# 3. Watch your inbox for abandonment alerts
```

## Cleanup
```bash
cd terraform && terraform destroy
```

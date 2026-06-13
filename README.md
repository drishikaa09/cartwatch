# CartWatch 🛒

![GitHub Actions](https://github.com/drishikaa09/cartwatch/actions/workflows/deploy.yml/badge.svg)
![AWS](https://img.shields.io/badge/AWS-Kinesis%20%7C%20Lambda%20%7C%20RDS%20%7C%20SNS-orange)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-blue)

> Event-driven cart abandonment detection — from user drop-off to email alert in under a second.

## Architecture
Simulator → Kinesis → Lambda → SNS (instant alert)

→ S3  (raw backup)

→ RDS (queryable events)
Kubernetes → FastAPI → RDS → Live analytics dashboard

## Stack

| Layer | Tech |
|---|---|
| Streaming | AWS Kinesis |
| Processing | AWS Lambda (Python) |
| Alerting | AWS SNS |
| Storage | AWS S3 + PostgreSQL RDS |
| Infrastructure | Terraform |
| Orchestration | Kubernetes (kind) |
| CI/CD | GitHub Actions |

## Quickstart

```bash
cd terraform && terraform apply        # spin up all AWS infra
python3 simulator/simulate_events.py   # start streaming events
kubectl port-forward svc/cartwatch-api 8080:80  # start dashboard
```

## Teardown
```bash
cd terraform && terraform destroy
```
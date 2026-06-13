# --- Provider ---
provider "aws" {
  region  = "eu-north-1"
  profile = "cartwatch"
}

# --- Kinesis Stream ---
resource "aws_kinesis_stream" "cartwatch" {
  name             = "cartwatch-stream"
  shard_count      = 1
  retention_period = 24

  tags = {
    Project = "cartwatch"
  }
}

# --- S3 Bucket ---
resource "aws_s3_bucket" "cartwatch" {
  bucket = "cartwatch-events-732778637529"

  tags = {
    Project = "cartwatch"
  }
}

# --- SNS Topic ---
resource "aws_sns_topic" "abandonment_alerts" {
  name = "cartwatch-abandonment-alerts"
}

# --- SNS Email Subscription ---
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.abandonment_alerts.arn
  protocol  = "email"
  endpoint  = "0903charutiwari@gmail.com"
}

# --- IAM Role for Lambda ---
resource "aws_iam_role" "lambda_role" {
  name = "cartwatch-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# --- IAM Policy for Lambda ---
resource "aws_iam_role_policy" "lambda_policy" {
  name = "cartwatch-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["kinesis:GetRecords", "kinesis:GetShardIterator", "kinesis:DescribeStream", "kinesis:ListStreams"]
        Resource = aws_kinesis_stream.cartwatch.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.cartwatch.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["sns:Publish"]
        Resource = aws_sns_topic.abandonment_alerts.arn
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "*"
      }
    ]
  })
}

# --- Lambda Function ---
resource "aws_lambda_function" "cartwatch" {
  filename         = "../lambda/handler.zip"
  function_name    = "cartwatch-handler"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = filebase64sha256("../lambda/handler.zip")

  tags = {
    Project = "cartwatch"
  }
}

# --- Kinesis Trigger for Lambda ---
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = aws_kinesis_stream.cartwatch.arn
  function_name     = aws_lambda_function.cartwatch.arn
  starting_position = "LATEST"
  batch_size        = 10
}
# --- VPC for RDS ---
resource "aws_vpc" "cartwatch" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Project = "cartwatch" }
}

resource "aws_subnet" "cartwatch_a" {
  vpc_id            = aws_vpc.cartwatch.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-north-1a"
  tags = { Project = "cartwatch" }
}

resource "aws_subnet" "cartwatch_b" {
  vpc_id            = aws_vpc.cartwatch.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "eu-north-1b"
  tags = { Project = "cartwatch" }
}

# --- Route Table ---
resource "aws_route_table" "cartwatch" {
  vpc_id = aws_vpc.cartwatch.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cartwatch.id
  }

  depends_on = [aws_internet_gateway.cartwatch]

  tags = { Project = "cartwatch" }
}
# --- Security Group for RDS ---
resource "aws_security_group" "rds" {
  name   = "cartwatch-rds-sg"
  vpc_id = aws_vpc.cartwatch.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Project = "cartwatch" }
}

# --- Internet Gateway ---
resource "aws_internet_gateway" "cartwatch" {
  vpc_id = aws_vpc.cartwatch.id
  tags = { Project = "cartwatch" }
}

# --- RDS Subnet Group ---
resource "aws_db_subnet_group" "cartwatch" {
  name       = "cartwatch-subnet-group"
  subnet_ids = [aws_subnet.cartwatch_a.id, aws_subnet.cartwatch_b.id]
  tags = { Project = "cartwatch" }
}

# --- RDS PostgreSQL ---
resource "aws_db_instance" "cartwatch" {
  identifier        = "cartwatch-db"
  engine            = "postgres"
  engine_version    = "16.9"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "cartwatch"
  username = "cartwatch_user"
  password = "cartwatch_pass_2024"

  db_subnet_group_name   = aws_db_subnet_group.cartwatch.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = true
  skip_final_snapshot = true

  depends_on = [aws_internet_gateway.cartwatch]

  tags = { Project = "cartwatch" }
}
# --- Output RDS Endpoint ---
output "rds_endpoint" {
  value = aws_db_instance.cartwatch.endpoint
}
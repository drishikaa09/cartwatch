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
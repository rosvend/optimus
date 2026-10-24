variable "bucket_prefix" {
  description = "Prefix for the S3 bucket name; AWS appends a unique suffix"
  type        = string
}

variable "source_dir" {
  description = "Built dashboard files (dashboard/dist)"
  type        = string
}

variable "api_url" {
  description = "Telemetry API URL written into config.json"
  type        = string
}

variable "signaling_url" {
  description = "Video signaling WebSocket URL written into config.json"
  type        = string
}

variable "video_room_id" {
  description = "Room the dashboard joins to watch the robot's camera"
  type        = string
}

variable "aws_profile" {
  description = "AWS CLI profile used to create the bucket"
  type        = string
}

variable "aws_region" {
  description = "Region the bucket is created in"
  type        = string
}

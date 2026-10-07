output "api_url" {
  description = "Local URL of the API"
  value       = "http://127.0.0.1:8006"
}

output "ui_url" {
  description = "Local URL of the Streamlit UI"
  value       = "http://127.0.0.1:8506"
}

output "network_name" {
  description = "Docker network managed by Terraform"
  value       = docker_network.group.name
}

output "volume_name" {
  description = "Docker volume used for SQLite data"
  value       = docker_volume.data.name
}
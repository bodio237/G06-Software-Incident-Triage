terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "4.0.0"
    }
  }
}

provider "docker" {
  host = var.docker_host
}

resource "docker_image" "app" {
  name         = var.image_name
  keep_locally = true
}

resource "docker_network" "group" {
  name = "g06-network"
}

resource "docker_volume" "data" {
  name = "g06-data"
}

resource "docker_container" "api" {
  name  = "g06-api"
  image = docker_image.app.image_id

  networks_advanced {
    name = docker_network.group.name
  }

  env = [
    "LLM_PROVIDER=local",
    "SCENARIO_ID=g06",
    "LLM_BASE_URL=${var.llm_base_url}",
    "LLM_MODEL=${var.llm_model}",
    "LLM_TIMEOUT=${var.llm_timeout}",
    "LLM_MAX_TOKENS=${var.llm_max_tokens}",
    "DB_PATH=/data/analyses.db"
  ]

  ports {
    internal = 8000
    external = 8000 + var.group_id
    ip       = "127.0.0.1"
  }

  volumes {
    volume_name    = docker_volume.data.name
    container_path = "/data"
  }
}

resource "docker_container" "ui" {
  name  = "g06-ui"
  image = docker_image.app.image_id

  networks_advanced {
    name = docker_network.group.name
  }

  command = [
    "python",
    "-m",
    "streamlit",
    "run",
    "ui/app.py",
    "--server.address=0.0.0.0",
    "--server.port=8501"
  ]

  env = [
    "API_URL=http://g06-api:8000"
  ]

  ports {
    internal = 8501
    external = 8500 + var.group_id
    ip       = "127.0.0.1"
  }

  depends_on = [
    docker_container.api
  ]
}
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
    }
  }
}

provider "docker" {}

resource "docker_network" "app_network" {
  name = "${var.project_name}-network"
}

resource "docker_volume" "mysql_data" {
  name = "${var.project_name}-mysql-data"
}

resource "docker_image" "mysql" {
  name         = "mysql:8.0"
  keep_locally = true
}

resource "docker_container" "mysql" {
  name  = "${var.project_name}-mysql"
  image = docker_image.mysql.image_id
  
  env = [
    "MYSQL_ROOT_PASSWORD=${var.db_password}",
    "MYSQL_DATABASE=${var.db_name}",
    "MYSQL_USER=${var.db_user}",
    "MYSQL_PASSWORD=${var.db_user_password}"
  ]

  networks_advanced {
    name    = docker_network.app_network.name
    aliases = ["mysql"]
  }

  volumes {
    host_path      = abspath("${path.module}/database/seed.sql")
    container_path = "/docker-entrypoint-initdb.d/seed.sql"
  }
  
  volumes {
    volume_name    = docker_volume.mysql_data.name
    container_path = "/var/lib/mysql"
  }
  
  ports {
    internal = 3306
    external = 3306
  }
}

resource "docker_image" "backend" {
  name = "${var.project_name}-backend"
  build {
    context = "${path.module}/backend"
    tag     = ["${var.project_name}-backend:latest"]
  }
}

resource "docker_container" "backend" {
  name  = "${var.project_name}-backend"
  image = docker_image.backend.image_id

  env = [
    "DB_HOST=mysql",
    "DB_PORT=3306",
    "DB_NAME=${var.db_name}",
    "DB_USER=${var.db_user}",
    "DB_PASSWORD=${var.db_user_password}"
  ]

  networks_advanced {
    name    = docker_network.app_network.name
    aliases = ["backend"]
  }

  ports {
    internal = 8000
    external = 8000
  }

  depends_on = [docker_container.mysql]
}

resource "docker_image" "nginx" {
  name         = "nginx:latest"
  keep_locally = true
}

resource "docker_container" "frontend" {
  name  = "${var.project_name}-frontend"
  image = docker_image.nginx.image_id

  networks_advanced {
    name    = docker_network.app_network.name
    aliases = ["frontend"]
  }

  ports {
    internal = 80
    external = 80
  }

  volumes {
    host_path      = abspath("${path.module}/frontend")
    container_path = "/usr/share/nginx/html"
  }

  volumes {
    host_path      = abspath("${path.module}/frontend/nginx.conf")
    container_path = "/etc/nginx/conf.d/default.conf"
  }

  depends_on = [docker_container.backend]
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "devsecops-tp04"
}

variable "db_password" {
  description = "Password for the MySQL database root user"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "usersdb"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "admin"
}

variable "db_user_password" {
  description = "Password for the database user"
  type        = string
  sensitive   = true
}
